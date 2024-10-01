#!/bin/sh
/usr/bin/python3.11 -m uvicorn --workers 5 --host=0.0.0.0 --port=61008 serverPatchingEndpoints:app
