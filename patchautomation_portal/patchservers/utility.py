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


import datetime
import docker
from .models import ServerPatchDetails

import time
import logging
import calendar
from django.db.models import Q
from django.utils.timezone import make_aware
from dateutil.relativedelta import relativedelta
from . import variables

logger = logging.getLogger('Utility')

workdir = variables.workdir
volumes = variables.volumes
image_name = variables.image_name
pythonMpa = variables.pythonMpa

def generate_hostcsv(filepath, object_list):
    with open(filepath + ".csv", "w") as f:
        # Write each item to the file, one item per line
        f.write("host\n")
        for server in object_list:
            f.write(server.hostname + "\n")
    f.close()
    # return render(None, 'generic_response.html', {'result': "result"})


def generte_masteryml(filepath, object_list):

    with open(filepath + ".yml", "w") as f:
        # Write each item to the file, one item per line
        # f.write("host,u_user,u_pass\n")
        for server in object_list:
            f.write(server.defaultuser + "\n")
            f.write(server.defaultpass + "\n")
    f.close()


def convert_map_to_list(objects, fname):
    keys = []
    values = []
    for item in objects:
        key = item[fname]
        count = item["count"]
        keys.append(key)
        values.append(count)
    return keys, values

def update_server_details(upload_id, readylist_tmp, run_id, state, action, remarks):
    for host in readylist_tmp:
        logger.debug("####################################host", host)
        tempobject = ServerPatchDetails.objects.get(id=host[0])
        tempobject.uploadid = upload_id
        tempobject.state = state
        tempobject.action = action
        tempobject.runid = run_id
        tempobject.remarks = remarks
        tempobject.save()

def update_server_objects(upload_id, server_list, run_id, state, action, remarks):
    for host in server_list:
        logger.debug("####################################host", host)
        tempobject = host
        tempobject.uploadid = upload_id
        tempobject.state = state
        tempobject.action = action
        tempobject.runid = run_id
        tempobject.remarks = remarks
        tempobject.save()

def callplaywirght(prop_file):
    time.sleep(10)
    logger.debug("10 more seconds to invoke playwright docker with properties : "+ prop_file)
    time.sleep(10)
    logger.debug("starting the background thread!")

    client = docker.from_env()

    container = client.containers.create(
        image=image_name,
        command=["python", pythonMpa, prop_file],
        working_dir=workdir,
        volumes=[volumes],
        detach=True,
    )
    # container.logs()
    container.start()
    logger.debug("started the container with " + container.id)


def getMasterValues(param):
    logger.debug("calling get master data with param " + param)
    if param == "All":
        #onboarded = ServerPatchDetails.objects.all()
        query={}
    else:
        query= {'instance__appname':param}
        logger.debug(query)
    
    onboarded = ServerPatchDetails.objects.all().filter(**query)
    
    prevmon,currmonth, nextmon = getmonths()

    nextmonpatch = onboarded.filter(Q(state__in=["Completed"]) & Q(latestpatch__in=[nextmon])).filter(**query)
    if len(nextmonpatch) <= 0:
        nextmon=currmonth
        currmonth=prevmon
        nextmonpatch = onboarded.filter(Q(state__in=["Completed"]) & Q(latestpatch__in=[nextmon])).filter(**query)

    othermonpatch = onboarded.filter(Q(state__in=["Completed"]) & ~Q(latestpatch__in=[nextmon,currmonth])).filter(**query)

    logger.debug(nextmon +" --------"+ str(len(nextmonpatch)))
    currmonthpatch = onboarded.filter( Q(state__in=["Completed"]) & Q(latestpatch__in=[currmonth])).filter(**query)
    logger.debug(currmonth +"-----------"+str(len(currmonthpatch)))
    logger.debug("othermonpatch --------"+ str(len(othermonpatch)))
    logger.debug(currmonth + " *******   " + nextmon)
    patched = onboarded.filter(Q(state__in=["Completed"])).filter(**query)
    pending_schedule =onboarded.filter(
        Q(action__in=["To be Scheduled"] )
    ).filter(**query)
    reonboard = onboarded.filter(Q(action__in=["MPA Failed","Reonboard"])).filter(**query)
    halted = onboarded.filter(
        Q(state__in=["Blocked"]) & Q(remarks__icontains="Onepatch reached")
    ).filter(**query)
    failed = onboarded.filter(
        Q(state__in=["Blocked"])
        & ~Q(action__in=["Credentials Failed"])
        & ~Q(remarks__icontains="Onepatch reached")
        & ~Q(action__in=["MPA Failed","Reonboard"])
    ).filter(**query)
    unreachable = onboarded.filter(
        Q(action__in=["Credentials Failed"])
        | Q(remarks__icontains="Host is not eligible for patching")
    ).filter(**query)
    recheck = onboarded.filter(
        Q(state__in=["ReCheck"])
        & ~Q(action__in=["To be Scheduled"])
        & ~Q(remarks__icontains="Host is not eligible for patching")
    ).filter(**query)
    stuck = onboarded.filter(
        Q(state__in=["Failed"])
        | Q(state__in=["Inprogress"])
        | (Q(state__in=["New"]) & ~Q(action__in=["To be Scheduled"]))
    ).filter(**query)
    data = {
        "Master_data": onboarded,
        "Patched": patched,
        "Pending_schedule": pending_schedule,
        "Reonboard": reonboard,
        "Halted": halted,
        "Failed": failed,
        "Unreachable": unreachable,
        "Recheck": recheck,
        "Stuck": stuck
        }
    patchdets={
        "currmon":currmonth,
        "nextmon":nextmon,
        "currmonlen":len(currmonthpatch),
        "nextmonlen":len(nextmonpatch),
        "othermonlen":len(othermonpatch)
    }
    return patchdets,data

def getmonths():
    today = datetime.datetime.today()
    cmonth = today.strftime("%b").upper()  # Get abbreviated month name (e.g., Apr) and uppercase it
    cyear = today.strftime("%y") 
    currmonth=cmonth+cyear
    # Add one month to the current date
    #next_month = today + datetime.timedelta(days = (calendar.monthrange(today.year, today.month)[1] + 1) % 32, weeks=(today.day // 7) - (calendar.monthrange(today.year, today.month)[0] == 6))
    next_month = today + relativedelta(months=1)
    month = next_month.strftime("%b").upper()  # Get abbreviated month name (e.g., Apr) and uppercase it
    year = next_month.strftime("%y") 
    nextmon=month+year

    # mimus one month to the current date
    #prev_month = today - datetime.timedelta(days = (calendar.monthrange(today.year, today.month)[1] +1) % 32, weeks=(today.day // 7) - (calendar.monthrange(today.year, today.month)[0] == 6))
    prev_month = today + relativedelta(months=-1)
    month = prev_month.strftime("%b").upper()  # Get abbreviated month name (e.g., Apr) and uppercase it
    year = prev_month.strftime("%y") 
    prevmon=month+year

    return prevmon,currmonth,nextmon


def validatedate(start_date1,end_date1):
        # Validate and process dates
    try:
        if not start_date1 or not end_date1:
            raise ValueError("Both dates are required.")
        start_date = make_aware(
            datetime.datetime.strptime(
                start_date1 + " 00:00:00", "%Y-%m-%d %H:%M:%S"
            )
        )
        end_date = make_aware(
            datetime.datetime.strptime(end_date1 + " 23:59:59", "%Y-%m-%d %H:%M:%S")
        )
        if start_date > end_date:
            raise ValueError("Start date cannot be after end date.")
        logger.debug("start_date " + str(start_date) + " end_date " + str(end_date))

    except ValueError as e:
        raise

    return start_date,end_date
