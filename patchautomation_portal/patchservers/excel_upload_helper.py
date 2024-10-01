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

from openpyxl import Workbook
from .models import ServerPatchDetails ,Upload_runid
from django.db.models import QuerySet
import datetime
import pandas as pd
import random
from .ansibleVaultEncrypter import ansibleEncrypter
import logging

logger = logging.getLogger(__name__)

success_action_items = ['Patch Successful', 'Patch skipped', 'Patch Failed']
reupload_action_items = ['Credentials Failed' ]

'''def enrypt_pass(key, val):
    output = subprocess.run(['ansible-vault', 'encrypt_string', val, '--name' , key, '--vault-password-file', 'pass.txt'], capture_output=True)
    logger.debug(output)
    logger.debug(output.stdout.decode())
    return output.stdout.decode()'''

def enrypt_pass(key, val):
    return ansibleEncrypter(val,'itops',key)

def generate_runid(upload_id):
    """Generates a run ID in the format yyyymmmddhhmmss."""
    now = datetime.datetime.utcnow()    
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute
    second = now.second
    runid = f'{year}{month:02}{day:02}_{hour:02}{minute:02}{second:02}'
    Upload_runid.objects.create(uploadid=upload_id,runid=runid)
    return runid

def generate_uploadid():
    """Generates a run ID in the format yyyymmmddhhmmss."""
    now = datetime.datetime.utcnow()    
    year = now.year
    month = now.month
    day = now.day
    otp = random.randint(100000, 999999)
    uploadid = f'{year}{month:02}{day:02}_{otp}'
    return uploadid


def validatefile(db_frame,excel_frame,instanceid):
    invalidlist=[]
    onboardlist=[]
    reuploadlist=[]
    readylist=[]
    for Exrow in excel_frame.itertuples():
           hostname = Exrow.hostname
                   
           new_host = Exrow.hostname                    

           #new_host = Exrow.hostname+".iuser.iroot.adidom.com" 
           if ((db_frame['hostname'] == new_host).any()):
               obj=ServerPatchDetails.objects.filter(hostname__icontains=new_host)
               action=db_frame.loc[db_frame['hostname'] == new_host, 'action'].iloc[0]
               #logger.debug(new_host+" " +action +" "+ obj.values_list('action'))
               if action in reupload_action_items:
                logger.debug(new_host + " added to reupload")
                #reuploadlist.append([new_host,enrypt_pass(new_host+"_user", Exrow.defaultuser),enrypt_pass(new_host+"_pass", Exrow.defaultpass)])
                reuploadlist.append([new_host,enrypt_pass(new_host+"_user", " "),enrypt_pass(new_host+"_pass", " ")])
                
               elif action in success_action_items:
                logger.debug(new_host + " added to ready")
                readylist.append([obj.values_list('id')[0][0],obj.values_list('uploadid')[0][0],obj.values_list('hostname')[0][0],obj.values_list('state')[0][0],
                                    obj.values_list('action')[0][0],obj.values_list('remarks')[0][0]])
               else:
                logger.debug(new_host +" added to invalid")
                invalidlist.append([obj.values_list('uploadid')[0][0],obj.values_list('hostname')[0][0]])
             
           else :
               logger.debug(new_host+" added to onboard")
               #onboardlist.append([new_host,enrypt_pass(new_host+"_user", Exrow.defaultuser),enrypt_pass(new_host+"_pass", Exrow.defaultpass),instanceid])
               onboardlist.append([new_host,enrypt_pass(new_host+"_user", " "),enrypt_pass(new_host+"_pass", " "),instanceid])
    return onboardlist,invalidlist,readylist,reuploadlist


def convert_task_objects_to_pandas_dataframe(serverpatchdetails: QuerySet[ServerPatchDetails]) -> pd.DataFrame:
    column_names = ["uploadid", "hostname", "action", "remarks", "defaultuser", "defaultpass"]
    values = []
    for task in serverpatchdetails:
        row = [task.uploadid, task.hostname,task.action, task.remarks,task.defaultuser,task.defaultpass]
        values.append(row)
    df = pd.DataFrame(values, columns=column_names)
    return df

def create_excel_workbook(querysets):

    workbook = Workbook()

    for name, queryset in querysets.items():
        sheet = (
            workbook.active
            if name == list(querysets.keys())[0]
            else workbook.create_sheet()
        )
        sheet.title = name  # Name the sheet based on the variable name

        # Get field names for headers
        headers = []
        # Set column headers
        # headers = list(field.name for field in ServerPatchDetails._meta.fields)
        # worksheet.append(headers)
        excludes = ["id", "runid", "defaultuser", "defaultpass", "instance"]
        for field in ServerPatchDetails._meta.fields:
            if field.name not in excludes:
                headers.append(field.name)
            elif field.name == "instance":
                headers.append("lot")
                headers.append("AppId")
                headers.append("AppName")

        sheet.append(headers)

        # Add data to the sheet
        for obj in queryset:
            rowdata = []
            for field in ServerPatchDetails._meta.fields:
                if field.name not in excludes:
                    print(field.name )
                    print(str(getattr(obj, field.name)))
                    print(obj)
                    rowdata.append(str(getattr(obj, field.name)))
                elif field.name == "instance":
                    inst = getattr(obj, field.name)
                    # logger.debug(inst.lot)
                    # insdet = Instance.objects.filter(Q(id__in = [getattr(obj, field.name)]))
                    rowdata.append(inst.lot)
                    rowdata.append(inst.appid)
                    rowdata.append(inst.appname)
            # logger.debug(rowdata)
            sheet.append(rowdata)
    # workbook.save(filename)
    return workbook
