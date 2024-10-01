"""Copyright 2018 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. """

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.hmac import HMAC
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher as C_Cipher, algorithms, modes
import codecs
import os
import yaml
from binascii import unhexlify, hexlify

CRYPTOGRAPHY_BACKEND = default_backend()
HAS_CRYPTOGRAPHY = True
_COMPOSED_ERROR_HANDLERS = frozenset(
    (None, "surrogate_or_replace", "surrogate_or_strict", "surrogate_then_replace")
)
binary_type = bytes
try:
    codecs.lookup_error("surrogateescape")
    HAS_SURROGATEESCAPE = True
except LookupError:
    HAS_SURROGATEESCAPE = False


def to_bytes(obj, encoding="utf-8", errors=None, nonstring="simplerepr"):

    if isinstance(obj, binary_type):
        return obj

    # We're given a text string
    # If it has surrogates, we know because it will decode
    original_errors = errors
    if errors in _COMPOSED_ERROR_HANDLERS:
        if HAS_SURROGATEESCAPE:
            errors = "surrogateescape"
        elif errors == "surrogate_or_strict":
            errors = "strict"
        else:
            errors = "replace"

    if isinstance(obj, str):
        try:
            # Try this first as it's the fastest
            return obj.encode(encoding, errors)
        except UnicodeEncodeError:
            if original_errors in (None, "surrogate_then_replace"):
                # We should only reach this if encoding was non-utf8 original_errors was
                # surrogate_then_escape and errors was surrogateescape

                # Slow but works
                return_string = obj.encode("utf-8", "surrogateescape")
                return_string = return_string.decode("utf-8", "replace")
                return return_string.encode(encoding, "replace")
            raise

    # Note: We do these last even though we have to call to_bytes again on the
    # value because we're optimizing the common case
    if nonstring == "simplerepr":
        try:
            value = str(obj)
        except UnicodeError:
            try:
                value = repr(obj)
            except UnicodeError:
                # Giving up
                return to_bytes("")
    elif nonstring == "passthru":
        return obj
    elif nonstring == "empty":
        # python2.4 doesn't have b''
        return to_bytes("")
    elif nonstring == "strict":
        raise TypeError("obj must be a string type")
    else:
        raise TypeError(
            "Invalid value %s for to_bytes' nonstring parameter" % nonstring
        )

    return to_bytes(value, encoding, errors)


def ansibleEncrypter(plaintext, password, name):
    custom_salt = os.urandom(32)
    b_salt = to_bytes(custom_salt)
    b_password = to_bytes(password, errors="surrogate_or_strict")
    b_plaintext = to_bytes(plaintext, errors="surrogate_or_strict")
    key_length = 32
    iv_length = algorithms.AES.block_size // 8
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=2 * key_length + iv_length,
        salt=b_salt,
        iterations=10000,
        backend=CRYPTOGRAPHY_BACKEND,
    )
    b_derivedkey = kdf.derive(b_password)
    b_key1 = b_derivedkey[:key_length]
    b_key2 = b_derivedkey[key_length : (key_length * 2)]
    b_iv = b_derivedkey[(key_length * 2) : (key_length * 2) + iv_length]
    cipher = C_Cipher(algorithms.AES(b_key1), modes.CTR(b_iv), CRYPTOGRAPHY_BACKEND)
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    b_ciphertext = encryptor.update(padder.update(b_plaintext) + padder.finalize())
    b_ciphertext += encryptor.finalize()

    # COMBINE SALT, DIGEST AND DATA
    hmac = HMAC(b_key2, hashes.SHA256(), CRYPTOGRAPHY_BACKEND)
    hmac.update(b_ciphertext)
    b_hmac = hmac.finalize()

    b_hmac = to_bytes(hexlify(b_hmac), errors="surrogate_or_strict")
    b_ciphertext = hexlify(b_ciphertext)
    b_vaulttext = b"\n".join([hexlify(b_salt), b_hmac, b_ciphertext])
    # Unnecessary but getting rid of it is a backwards incompatible vault
    # format change
    b_vaulttext = hexlify(b_vaulttext)
    vaultString = (
        name
        + ": !vault |\r\n  $ANSIBLE_VAULT;1.1;AES256\r\n  "
        + b_vaulttext.decode()
        + "\r\n"
    )
    # b_vaulttext

    return vaultString
