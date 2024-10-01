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

from fastapi import FastAPI, Body, HTTPException
from datetime import datetime
import json
from typing import Optional
from pydantic import BaseModel
from awx_api import *
import sqlite3
import uvicorn
import time


class updateAll(BaseModel):
    runid: Optional[str]
    hostname: Optional[str]
    state: Optional[str]
    action: Optional[str]
    remarks: Optional[str]
    osmake: Optional[str]
    osversion: Optional[str]
    latestpatch: Optional[str]


class PatchTask(BaseModel):
    id: int
    runid: str
    hostname: str
    ipaddress:str
    state: str
    action: str
    remarks: str
    defaultuser:str
    defaultpass:str
    created_at: str

class Updateaction(BaseModel):
    runid: str
    hostname: str
    action: str

class UpdateRemarks(BaseModel):
    runid: str
    hostname: str
    remarks: str

class UpdateOnBoard(BaseModel):
    runid: str
    hostname: str
    state: str


class generateRunId(BaseModel):
    uploadid: str

class UpdateAll(BaseModel):
    runid: str
    hostname: str
    state: str
    action: str
    remarks: str

class Mpa(BaseModel):
    runid: str

class batch(BaseModel):
    batch_size: str
    data_list: Optional[list] = []


class templateNotification(BaseModel):
    status: str
    extra_vars: str

class request_data(BaseModel):
    data_string: Optional[str] = ""
    data_dict: Optional[dict] = {}
    data_list: Optional[list] = []

app = FastAPI()

database_url=properties.database_url

# Connect to the SQLite database
connection = sqlite3.connect(database_url, check_same_thread=False)


cursor = connection.cursor()


# Create a new task planner entry
@app.post("/patch_task")
async def create_patch_task(patch_task: PatchTask):
    print(patch_task)
    cursor.execute("""INSERT INTO patchservers_serverpatchdetails (runid, hostname, ipaddress,created_at, action, remarks, state,defaultuser,defaultpass)
    VALUES (?, ?, ?, ?,?, ?, ?,?,?)""", (patch_task.runid, patch_task.hostname,  patch_task.ipaddress,patch_task.created_at, patch_task.action, patch_task.remarks, patch_task.state,patch_task.defaultuser,patch_task.defaultpass))
    connection.commit()

    patch_task.id = cursor.lastrowid
    return patch_task

# Update a patchservers_serverpatchdetails entry
@app.post("/updateaction")
async def updateaction( updateaction: Updateaction):
    print (updateaction)

    cursor.execute("""UPDATE patchservers_serverpatchdetails SET action = ?
    WHERE hostname = ? and runid=?""", (updateaction.action,updateaction.hostname,updateaction.runid))

    connection.commit()
    # Get the number of rows updated
    rows_updated = cursor.rowcount

    return "Updated " + str(rows_updated) +" Rows"

# Update a patchservers_serverpatchdetails entry
@app.post("/updateremarks")
async def updateremarks( updateremarks: UpdateRemarks):
    print (updateremarks)

    cursor.execute("""UPDATE patchservers_serverpatchdetails SET remarks = ?
    WHERE hostname = ? and runid=?""", (updateremarks.remarks,updateremarks.hostname,updateremarks.runid))

    connection.commit()
    # Get the number of rows updated
    rows_updated = cursor.rowcount

    return "Updated " + str(rows_updated) +" Rows"

# Update a patchservers_serverpatchdetails entry
@app.post("/updateonboard")
async def updateonboard( updateonboard: UpdateOnBoard):
    print (updateonboard)

    cursor.execute("""UPDATE patchservers_serverpatchdetails SET state = ?
    WHERE hostname = ? and runid=?""", (updateonboard.state,updateonboard.hostname,updateonboard.runid))

    connection.commit()
    # Get the number of rows updated
    rows_updated = cursor.rowcount

    return "Updated " + str(rows_updated) +" Rows"

# Create a new task planner entry
@app.post("/invoke_mpa")
async def invoke_mpa (data: Mpa):
    print ("got invoked... going to sleep",data, time.localtime)
    time.sleep(10)
    print ("wokeup from  sleep",data, time.localtime)
    return "patch_task"


@app.post("/updateall")
async def updateall(updateall: updateAll):
    print(updateall)
    # Update the record in the database, checking if each value is present before updating it
    update_statement = 'UPDATE patchservers_serverpatchdetails SET '
    update_values = []
    cursor1 = connection.cursor()


    if updateall.state:
        update_statement += 'state = ? '
        update_values.append(updateall.state)

    if updateall.action:
        update_statement += ',action = ? '
        update_values.append(updateall.action)

    if updateall.remarks:
        update_statement += ',remarks = ? '
        update_values.append(updateall.remarks)


    if updateall.osmake:
        update_statement += ',osmake = ? '
        update_values.append(updateall.osmake)

    if updateall.osversion:
        update_statement += ',osversion = ? '
        update_values.append(updateall.osversion)

    if updateall.latestpatch:
        update_statement += ',latestpatch = ? '
        update_values.append(str(updateall.latestpatch).upper())

    if updateall.runid:
        update_statement += ',runid = ? '
        update_values.append(updateall.runid)

    #update_statement += 'WHERE runid = ?'
    #update_values.append(updateall.runid)
    update_statement += 'WHERE hostname = ?'
    update_values.append(updateall.hostname)

    print(update_statement)
    print(update_values)
    cursor1.execute(update_statement, update_values)

    # Commit the changes to the database
    connection.commit()

    rows_updated = cursor1.rowcount
    cursor1.close()
    return "Updated " + str(rows_updated) + " Rows"


# Update all patchservers_upload_runid entry for one template
@app.post("/update_runid")
async def template_notification(notification: templateNotification):
    print(notification)
    cursor1 = connection.cursor()
    extra_vars = json.loads(notification.extra_vars)
    print(extra_vars["run_id"])
    cursor1.execute("""UPDATE patchservers_upload_runid SET action = ?
    WHERE runid=?""", (notification.status, extra_vars["run_id"]))

    connection.commit()
    rows_updated = cursor1.rowcount
    cursor1.close()
    return "Updated " + str(rows_updated) +" Rows"


# Update all patchservers_upload_runid entry for one template
@app.post("/generate_runid")
async def generate_runid(generate_runid: generateRunId):
    print(f"data: {generate_runid}")
    upload_id = generate_runid.uploadid
    now = datetime.utcnow()
    year, month, day, hour, minute, second = now.year, now.month, now.day, now.hour, now.minute, now.second
    run_id = f'{year}{month:02}{day:02}_{hour:02}{minute:02}{second:02}'

    cursor.execute("""INSERT INTO patchservers_upload_runid (uploadid, runid)
    VALUES (?, ?)""", (upload_id, run_id))

    connection.commit()
    json_data = {"run_id":run_id}
    return json_data


# Update all patchservers_serverpatchdetails entry for all hosts
@app.post("/trigger_patch")
async def trigger_patch(trigger_data: templateNotification):
    print("trigger data:" + str(trigger_data))
    cursor1 = connection.cursor()
    extra_vars = json.loads(trigger_data.extra_vars)
    print("extra_vars" + str(extra_vars["run_id"]))
    host_data = cursor1.execute(f"""
                    SELECT hostname, uploadid
                    FROM patchservers_serverpatchdetails
                    WHERE runid='{extra_vars["run_id"]}' AND state='Inprogress' AND action='Ready to patch'
                   """).fetchall()
    print("host Data: " + str(host_data))
    print(awx_patch_handler(host_data, 'onepatch_execution'))
    return "successfully triggered"



def create_batches(data, batch_size):
  """
  This function takes a list and a batch size and returns a generator
  that yields batches of the specified size.
  """
  for i in range(0, len(data), batch_size):
    yield data[i:i+batch_size]

@app.post("/check_connectivity")
async def check_connectivity(batch_data: batch):
    
    cursor1 = connection.cursor()
    host_data = cursor1.execute(f"""
                    SELECT hostname, uploadid from patchservers_serverpatchdetails 
                    where ( osmake is null or latestpatch = 'Not Available' ) 
                    and hostname in ( SELECT  hostname from patchservers_serverpatchdetailsaudit 
                    where state = 'Blocked' and action = 'Credentials Failed' ) ;
                    """).fetchall()
    print("host Data: " + str(host_data))
    batch_size = int(batch_data.batch_size)
    print("batch::::::::")
    print(batch_data)
    for batch in create_batches(host_data, batch_size):
        print(awx_patch_handler(batch, 'get_server_details'))
    return "successfully triggered"

@app.post("/latest_patch_checker")
async def latest_patch_checker(batch_data: batch):
    
    cursor1 = connection.cursor()
   
    host_data = cursor1.execute(f"""
                    SELECT hostname, uploadid from patchservers_serverpatchdetails 
                    where state = 'Completed'
                    """).fetchall()
    print("host Data: " + str(host_data))
    batch_size = int(batch_data.batch_size)
    print("batch::::::::")
    print(batch_data)
    for batch in create_batches(host_data, batch_size):
#        continue
        print(awx_patch_handler(batch, 'latest_patch_checker'))
    return "successfully triggered"

@app.post("/updatelatestpatch")
async def updateremarks(request_data: request_data):
    print(updateremarks)


    cursor.execute("""UPDATE patchservers_serverpatchdetails SET latestpatch = ? , uptime = ?
    WHERE hostname = ?""", (request_data.data_dict['latestpatch'].upper(), request_data.data_dict['uptime'],
                            request_data.data_dict['hostname']))

    connection.commit()
    # Get the number of rows updated
    rows_updated = cursor.rowcount

    return "Updated " + str(rows_updated) + " Rows"

# Call AWX API
@app.post("/awx_handler")
def awx_endpoint(data: awx_data):
    response = awx_handler(data)
    return response
