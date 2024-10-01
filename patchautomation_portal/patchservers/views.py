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

import time
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.db.models import Count, CharField, Value
import threading
from .awx_helper import callget_serverdetails, callonboardchecker
from .utility import (
    callplaywirght,
    convert_map_to_list,
    getMasterValues,
    update_server_details,
    update_server_objects,
    validatedate,
)
from .models import (
    
    ServerPatchDetails,
    ServerPatchDetailsAudit,
    SkippedServers,
    Instance,
    Uploadmaster,
    
)
from datetime import datetime

from .resources import ServerPatchDetailsResource
import pandas as pd
from tablib import Dataset
from django.db.models import Q


from django.conf import settings


from .encrypt_helper import encrypt
from .excel_upload_helper import *


import urllib3

from django.template.defaulttags import register
from django.shortcuts import render
from django.http import JsonResponse
from .models import ServerPatchDetails

import logging
from . import variables
logger = logging.getLogger("Views")


@register.filter(name="split")
def split(value, key):

    value.split("key")
    return value.split(key)


mpa_url = variables.mpa_url

# for test

# awx_url="http://10.54.47.140:61001/awx_handler" #test
# host_file_path="/patchAutomation/pw/user_files"
# prop_file_path="/patchAutomation/pw/user_var"
# pythonMpa= "/app/mp/pw/fetch_password_from_mpa.py"
# workdir="/app/mp/pw"
# volumes='/patchAutomation:/app/mp'
# image_name="pwenv:5.0"

# for live
# Live
host_file_path =variables.host_file_path
prop_file_path = variables.prop_file_path



urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from django.shortcuts import render


settings.TIME_ZONE  # 'UTC'


# Create your views here.
def home(request):
    return render(request, "home.html", {})


def get_chart(request):
    return render(request, "chart.html", {})


# def get_report(request):
#     result = ""
#     options = Instance.objects.all()
#     sorted_appname=sorted(options,key=lambda option:option.appname)
#     sorted_appid=sorted(options,key=lambda option:option.appid)
    
#     logger.debug(" request.POST.get('options1')" + str(request.POST.get("options1")))
#     if request.method == "POST" and request.POST.get("options1") is not None:

#         start_date1 = request.POST.get("start_date")
#         end_date1 = request.POST.get("end_date")
#         try:
#             start_date, end_date = validatedate(start_date1, end_date1)
#         except ValueError as e:
#             error_message = str(e)
#             return render(
#                 request, "getreport.html", {"result": error_message, "options": options,"sorted_appname":sorted_appname,"sorted_appid":sorted_appid}
#             )

#         lot = request.POST.get("options1")
#         appid = request.POST.get("options2")
#         appname = request.POST.get("options3")
#         logger.debug(lot + " - " + appid + " - " + appname)

#         if lot != "" and appid != "" and appname != "":
#             logger.debug("instance details and date")
#             obj = Instance.objects.filter(
#                 Q(lot__icontains=lot)
#                 & Q(appid__icontains=appid)
#                 & Q(appname__icontains=appname)
#             ).values_list("id", flat=True)
#         elif lot != "" and appid != "":
#             logger.debug("lot and appid details and  date")
#             obj = Instance.objects.filter(
#                 Q(lot__icontains=lot) & Q(appid__icontains=appid)
#             ).values_list("id", flat=True)
#         elif lot != "":
#             logger.debug("lot details and date")
#             obj = Instance.objects.filter(Q(lot__icontains=lot)).values_list(
#                 "id", flat=True
#             )
#         elif appname != "":
#             logger.debug("lot and appid details and  date")
#             obj = Instance.objects.filter(Q(appname__icontains=appname)).values_list(
#                 "id", flat=True
#             )
#         else:
#             logger.debug("only date")
#             obj = Instance.objects.all().values_list("id", flat=True)
#         logger.debug(str(obj) + "   length of obj array " + str(len(obj)))
#         if len(obj) <= 0:
#             logger.debug("No data Found")
#             return render(
#                 request,
#                 "getreport.html",
#                 {
#                     "result": "No Data Found For Given Application Details",
#                     "options": options,
#                     "sorted_appname":sorted_appname,"sorted_appid":sorted_appid,
#                 },
#             )
#         else:
#             try:
#                 logger.debug(obj)
#                 serverdata = ServerPatchDetails.objects.filter(
#                     Q(instance__in=obj) & Q(update_date__range=[start_date, end_date])
#                 )
#                 if len(serverdata) > 0:
#                     data = {"ServerDetails": serverdata}
#                     workbook = create_excel_workbook(data)
#                     filename = f"Server_data_{start_date1}_{end_date1}.xlsx"
#                     response = HttpResponse(
#                         content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#                     )
#                     response["Content-Disposition"] = f"attachment; filename={filename}"
#                     workbook.save(response)
#                     return response
#                 else:
#                     return render(
#                         request,
#                         "getreport.html",
#                         {"result": "Given Filter Had No Data", "options": options,"sorted_appname":sorted_appname,"sorted_appid":sorted_appid},
#                     )
#             except KeyError:
#                 logger.debug("inside catch")
#                 return render(
#                     request,
#                     "getreport.html",
#                     {"result": "Error During Report Generation", "options": options,"sorted_appname":sorted_appname,"sorted_appid":sorted_appid},
#                 )
#     else:
#         logger.debug("returning from upload  action.")
#         return render(
#             request,
#             "getreport.html",
#             {
#                 "result": "Select one or more filter to generate a report",
#                 "options": options,
#                 "sorted_appname":sorted_appname,"sorted_appid":sorted_appid,
#             },
#         )


def chart_data():
    logger.debug("Inside Chart_data action")
    labels = []
    masterdata=ServerPatchDetails.objects.all()
    unique_lots = masterdata.values("instance__lot").distinct()
    actionList = masterdata.values("action").distinct()
    for action in actionList:
        labels.append(action["action"])
  
    table='<table id="table" class="table" ><tr><th>Lot</th><th>AppName</th><th>Action</th><th>Count</th><th>Patch Level Grouping</tr>'

    for lot in unique_lots:

        lotdata =masterdata.filter(Q(instance__lot=lot["instance__lot"]))
        unique_apps=lotdata.values("instance__appname").distinct()
        table+='<tr><td rowspan='+str(len(unique_apps)*len(labels))+'>'+lot["instance__lot"] +'</td>'
        for apps in unique_apps:
            table+='<td rowspan='+str(len(labels))+'>'+apps["instance__appname"] +'</td>'
            appsdata = lotdata.filter(Q(instance__appname=apps["instance__appname"]))
            unique_actions =  appsdata.values("action").annotate(count=Count("id"))            
            
            for label in labels:                
                patchdata = appsdata.filter(Q(action=label))               
                if len(patchdata)>0:
                    table+='<td>'+label +'</td>'
                    table+='<td>'+ str(len(patchdata)) +'</td>'
                    unique_patches=patchdata.values("latestpatch").annotate(count=Count("id")) 
                    table+='<td>'
                    for patch in unique_patches:
                        table+= patch['latestpatch']+ " : <b>" + str(patch['count'])+"</b> | "
                    table+='</td>'
                table+='</tr><tr>'

    table+='</table>'    
    
    logger.debug("returning from  Chart_data action.")

    return table


def dashboard(request):
    action_counts = (
        ServerPatchDetails.objects.values("action")
        .annotate(count=Count("id"))
        .order_by("action")
    )
    latest_counts = (
        ServerPatchDetails.objects.values("latestpatch")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    osmake_counts = (
        ServerPatchDetails.objects.values("osversion")
        .annotate(count=Count("id"))
        .order_by("osversion")
    )
    #    lot_counts = ServerPatchDetails.objects.values('instance__lot').annotate(count=Count('id'))
    app_counts = (
        ServerPatchDetails.objects.values("instance__appname")
        .annotate(count=Count("id"))
        .order_by("instance__appname")
    )

    action_keys, action_values = convert_map_to_list(action_counts, "action")
    latest_keys, latest_values = convert_map_to_list(latest_counts, "latestpatch")
    osmake_keys, osmake_values = convert_map_to_list(osmake_counts, "osversion")
    #    lot_keys, lot_values = convert_map_to_list(lot_counts , 'instance__lot' )
    app_keys, app_values = convert_map_to_list(app_counts, "instance__appname")

    data = {
        "action_counts": action_counts,
        "osmake_counts": osmake_counts,
        "latest_counts": latest_counts,
        "app_counts": app_counts,
    }
    context = {
        "osmake_keys": osmake_keys,
        "osmake_values": osmake_values,
        "action_keys": action_keys,
        "action_values": action_values,
        "latest_keys": latest_keys,
        "latest_values": latest_values,
        "app_keys": app_keys,
        "app_values": app_values,
        "table":chart_data,
        "data": data,
    }
    logger.debug("returning from  dashboard action.")
    return render(request, "dashboard.html", context)


def serverpatchdetails_index(request):
    serverpatchdetails = ServerPatchDetails.objects.all().order_by("-id")
    context = {"serverpatchdetailss": serverpatchdetails}
    logger.debug("returning from  serverdetails default action.")
    return render(request, "serverpatchdetails_index.html", context)


def serverpatchdetails_list(request):

    options = Instance.objects.all()
    sorted_appname=sorted(options,key=lambda option:option.appname)
    logger.debug(" request.POST.get('options3')" + str(request.POST.get("options3")))
    if request.method == "POST":
        onboarded = ServerPatchDetails.objects.all()

        start_date1 = request.POST.get("start_date")
        end_date1 = request.POST.get("end_date")
        start_date = ""
        end_date = ""
        print(start_date1)
        # Validate and process dates
        if start_date1 != "":
            try:
                start_date, end_date = validatedate(start_date1, end_date1)

            except ValueError as e:
                error_message = str(e)
                return render(
                    request,
                    "serverpatchdetails_list.html",
                    {"regrouped_data": None, "result": error_message, "options": options,"sorted_appname":sorted_appname},
                )

        appname = request.POST.get("options3")
        logger.debug(
            "appname  "
            + appname
            + " start_date "
            + str(start_date)
            + " end_date "
            + str(end_date)
        )
        if start_date == "" and end_date == "":
            grouped_data = (
                onboarded.filter(Q(instance__appname=appname))
                .values("state", "action", "uploadid", "instance__appname")
                .annotate(count=Count("id"), instance_count=Count("instance"))
                .order_by("-uploadid")
            )
        elif appname == "":
            grouped_data = (
                onboarded.filter(
                    Q(update_date__range=[start_date, end_date])
                )
                .values("state", "action", "uploadid", "instance__appname")
                .annotate(count=Count("id"), instance_count=Count("instance"))
                .order_by("-uploadid")
            )

        else:
            grouped_data = (
               onboarded.filter(
                    Q(instance__appname=appname)
                    & Q(update_date__range=[start_date, end_date])
                )
                .values("state", "action", "uploadid", "instance__appname")
                .annotate(count=Count("id"), instance_count=Count("instance"))
                .order_by("-uploadid")
            )
        regrouped_data = {}
        for item in grouped_data:
            uploadid = item["uploadid"]
            instance__appname = item["instance__appname"]
            filter = uploadid + " - " + instance__appname
            if (filter) not in regrouped_data:
                regrouped_data[filter] = {"data": []}
            uploaded_by = Uploadmaster.objects.filter((Q(uploadid=uploadid))).values(
                "uploadedby"
            )
            # logger.debug('uploaded_by : '+uploaded_by[0]['uploadedby'] +' uploadid : '+uploadid)
            regrouped_data[filter]["data"].append(
                {
                    "status": item["state"] + "-" + item["action"],
                    "counts": str(item["count"]),
                    "id": item["uploadid"],
                    "owner": uploaded_by[0]["uploadedby"],
                }
            )

        # objects = ServerPatchDetails.objects.all().order_by('-id')

        context = {
            "regrouped_data": regrouped_data,
            "result": "Fetched the Upload Details",
            "options": options,
            "sorted_appname":sorted_appname,
        }
        logger.debug("returning from  serverlist action.")
        return render(request, "serverpatchdetails_list.html", context)
    else:
        context = {
            "regrouped_data": None,
            "result": "Please select either the Lot or Date Range",
            "options": options,
            "sorted_appname":sorted_appname,
        }
        return render(request, "serverpatchdetails_list.html", context)


def overview(request):
    options = Instance.objects.all()
    sorted_appname=sorted(options,key=lambda option:option.appname)
    appname = "All"
    if request.method == "POST":
        logger.debug("Inside Overview : " + request.POST.get("options3"))
        appname = request.POST.get("options3")
        patchdets, data = getMasterValues(appname)
    else:
        patchdets, data = getMasterValues("All")
    context = {
        "data": data,
        "options": options,
        "appname": appname,
        "patchdets": patchdets,
        "sorted_appname":sorted_appname,
    }
    logger.debug("returning from  overview action. with data ")
    return render(request, "overview.html", context)


def downloadrun(request, uploadid):
    objects = ServerPatchDetails.objects.filter(Q(uploadid__in=[uploadid])).order_by(
        "state", "action"
    )

    context = {"objects": objects}
    return render(request, "searchserver.html", context)


def getdump(request, appname):
    patchdets, data = getMasterValues(appname)
    workbook = create_excel_workbook(data)
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        f'attachment; filename={"MasterDump_"+appname+".xlsx"}'
    )
    workbook.save(response)
    return response


def list_server_patch_details(request):
    server_patch_details = ServerPatchDetails.objects.all()
    unique_state_values = ServerPatchDetails.objects.values("state").distinct()
    context_list = {}
    for task in unique_state_values:
        logger.debug(f"{task['state']}")
        state = task["state"]
        context_list[state] = (
            server_patch_details.filter(state=state)
            .values(
                "id",
                "hostname",
                "uploadid",
                "runid",
                "action",
                "remarks",
                "osmake",
                "state",
                "osversion",
                "latestpatch",
                "instance__lot",
                "instance__appid",
                "instance__appname",
            )
            .order_by("state")
        )
    context = {
        "grouped_by_action": context_list,
    }
    logger.debug("returning from  serverdetails lsit response  action.")
    return render(request, "list.html", context)


def serverpatchdetails_detail(request, id):
    serverpatchdetails = ServerPatchDetails.objects.get(id=id)
    serverpatchdetailsaudits = ServerPatchDetailsAudit.objects.filter(
        hostname__icontains=serverpatchdetails.hostname
    ).order_by("-id")
    context = {
        "serverpatchdetails": serverpatchdetails,
        "serverpatchdetailsaudits": serverpatchdetailsaudits,
    }
    logger.debug("returning from  server details  action.")
    return render(request, "serverpatchdetails_detail.html", context)


def upload_task(request):
    result = ""
    options = Instance.objects.all()
    sorted_appname = sorted(options, key=lambda option: option.appname)
    sorted_appid = sorted(options, key=lambda option: option.appid)
    if request.method == "POST" and len(request.FILES) > 0:
        lot = request.POST.get("options1")
        appid = request.POST.get("options2")
        appname = request.POST.get("options3")
        username = request.POST.get("username")
        logger.debug(
            request.POST.get("options1")
            + " - "
            + request.POST.get("options2")
            + " - "
            + request.POST.get("options3")
            + " - "
            + request.POST.get("username")
        )
        if (
            lot is None
            or appid is None
            or appname is None
            or lot == ""
            or appid == ""
            or appname == ""
        ):
            return render(
                request,
                "Import_excel_db.html",
                {
                    "result": "Please Select all the values",
                    "upload_id": "",
                    "uploaded_file_url": "",
                    "object_list": "",
                    "run_id": "",
                    "onboardlist": "",
                    "invalidlist": "",
                    "hostname_duplicates": "",
                    "readylist": "",
                    "options": options,
                    "sorted_appname":sorted_appname,
                    "sorted_appid": sorted_appid
                },
            )
        else:
            obj = Instance.objects.filter(
                Q(lot__icontains=lot)
                & Q(appid__icontains=appid)
                & Q(appname__icontains=appname)
            ).first()

            if obj is None:
                return render(
                    request,
                    "Import_excel_db.html",
                    {
                        "result": "Please Select Valid Application Details",
                        "upload_id": "",
                        "uploaded_file_url": "",
                        "object_list": "",
                        "run_id": "",
                        "onboardlist": "",
                        "invalidlist": "",
                        "hostname_duplicates": "",
                        "readylist": "",
                        "options": options,
                        "sorted_appname":sorted_appname,
                        "sorted_appid": sorted_appid,
                    },
                )
            else:
                try:
                    logger.debug(obj.id)
                    filename = request.FILES["myfile"]
                    # uploaded_file_url = fs.url(filename)
                    excel_frame = pd.read_excel(filename)
                    hostname_duplicates = excel_frame.loc[
                        excel_frame["hostname"].duplicated(), "hostname"
                    ].tolist()
                    excel_frame = excel_frame.drop_duplicates(subset=["hostname"])
                    tasks = (
                        ServerPatchDetails.objects.all()
                    )  # .filter(action__in=['Pipelined'])
                    db_frame = convert_task_objects_to_pandas_dataframe(tasks)
                    upload_id = generate_uploadid()
                    onboardlist_tmp, invalidlist, readylist_tmp, reuploadlist = (
                        validatefile(db_frame, excel_frame, obj.id)
                    )
                    # logger.debug("onboard "+ str(onboardlist_tmp) +" \n invalid " + str(invalidlist) +" \n ready " + str(readylist_tmp) +" \n hostname " + str(hostname_duplicates))
                    object_list = []
                    run_id = "0"
                    onboardlist = []
                    readylist = []

                    if len(reuploadlist) > 0:
                        run_id = generate_runid(upload_id)
                        logger.debug(
                            "generated a new run_id same will be used if we have new server to onboard"
                            + run_id
                        )
                        for host in reuploadlist:
                            logger.debug(f"reuploading {host[0]} with new credentials")
                            ServerPatchDetails.objects.all().filter(
                                hostname=host[0]
                            ).update(
                                runid=run_id,
                                uploadid=upload_id,
                                # state="ReCheck",
                                # action="Re-Upload",
                                state="New",
                                action="Pipelined",
                                remarks="Retry - For Connectivity",
                                defaultuser=host[1],
                                defaultpass=host[2],
                            )

                    if len(invalidlist) > 0:
                        for host in invalidlist:
                            SkippedServers.objects.create(
                                #uploadid=upload_id, hostname=host[1]
                                uploadid=upload_id, hostname=host[1], old_uploadid=host[0]
                            )
                            # obj.save()

                    if len(onboardlist_tmp) > 0 or len(reuploadlist) > 0:
                        if run_id == "0":
                            run_id = generate_runid(upload_id)
                            logger.debug(
                                "generated a new run_id as we had no active runid or reuploaded server"
                                + run_id
                            )
                        else:
                            logger.debug(
                                "reusing run_id as we had no active runid or reuploaded server"
                                + run_id
                            )

                        for host in onboardlist_tmp:
                            ServerPatchDetails.objects.create(
                                uploadid=upload_id,
                                runid=run_id,
                                hostname=host[0],
                                state="New",
                                action="Pipelined",
                                remarks="Get Server Details",
                                defaultuser=host[1],
                                defaultpass=host[2],
                                latestpatch="Not Available",
                                instance_id=host[3],
                            )
                            # obj.save()
                        onboardlist = ServerPatchDetails.objects.filter(
                            Q(runid__icontains=run_id)
                            & (
                                Q(action__icontains="Pipelined")
                                | Q(action__icontains="Re-Upload")
                            )
                        )

                    if len(readylist_tmp) > 0:
                        if run_id == "0":
                            run_id = generate_runid(upload_id)
                        update_server_details(
                            upload_id,
                            readylist_tmp,
                            run_id,
                            "ReCheck",
                            "To be Scheduled",
                            "Validate ITOPS User",
                        )
                        readylist = ServerPatchDetails.objects.filter(
                            Q(runid__icontains=run_id)
                            & Q(state__icontains="ReCheck")
                            & Q(action__icontains="To be Scheduled")
                        )

                    # object_list = ServerPatchDetails.objects.filter(runid__icontains=run_id)
                    onboardlistlen = 0
                    invalidlen = 0
                    duplicatelen = 0
                    readylistlen = 0
                    onboardlistlen = len(onboardlist)
                    invalidlen = len(invalidlist)
                    duplicatelen = len(hostname_duplicates)
                    readylistlen = len(readylist)
                    if (
                        (onboardlistlen > 0 or readylistlen > 0)
                        and invalidlen == 0
                        and duplicatelen == 0
                    ):
                        Uploadmaster.objects.create(
                            uploadid=upload_id, uploadedby=username
                        )
                        result = "File Uploaded Successfully"
                    elif (onboardlistlen > 0 or readylistlen) and (
                        invalidlen > 0 or duplicatelen > 0
                    ):
                        Uploadmaster.objects.create(
                            uploadid=upload_id, uploadedby=username
                        )
                        result = "File Uploaded - Few records are skipped Due to Validation Errors"
                    elif (onboardlistlen == 0 and readylistlen == 0) and (
                        invalidlen > 0 or duplicatelen > 0
                    ):
                        Uploadmaster.objects.create(
                            uploadid=upload_id, uploadedby=username
                        )
                        result = "File Upload skipped Due to Validation Errors"
                    else:
                        result = "Error During File Upload "

                    logger.debug(
                        "Proceeding with callget_serverdetails, getting OS details "
                    )
                    # Create a background thread
                    thread = threading.Thread(
                        target=callget_serverdetails, args=(run_id,)
                    )
                    # Start the background thread
                    thread.start()
                    time.sleep(10)
                    logger.debug(
                        "Proceeding with callonboardchecker , checking if ITOPS User is there"
                    )
                    # Create a background thread
                    thread = threading.Thread(target=callonboardchecker, args=(run_id,))
                    # Start the background thread
                    thread.start()

                    # logger.debug (onboardlistlen +" "+ readylistlen +" "+ invalidlen +" "+ duplicatelen +" "+ result +" "+ object_list)
                    return render(
                        request,
                        "Import_excel_db.html",
                        {
                            "result": result,
                            "upload_id": upload_id,
                            "run_id": run_id,
                            "onboardlist": onboardlist,
                            "onboardlistl": onboardlistlen,
                            "invalidlist": invalidlist,
                            "invalidlistl": invalidlen,
                            "readylistl": readylistlen,
                            "readylist": readylist,
                            "hostname_duplicates": hostname_duplicates,
                            "hostname_duplicatesl": duplicatelen,
                            "options": options,
                            "sorted_appname":sorted_appname,
                            "sorted_appid": sorted_appid,
                        },
                    )
                except KeyError:
                    logger.debug("inside catch")
                    return render(
                        request,
                        "Import_excel_db.html",
                        {
                            "result": "Error During File Upload",
                            "upload_id": "",
                            "run_id": run_id,
                            "onboardlist": onboardlist,
                            "invalidlist": invalidlist,
                            "hostname_duplicates": hostname_duplicates,
                            "readylist": readylist,
                            "options": options,
                        },
                    )
    else:
        logger.debug("returning from upload  action.")
        return render(
            request,
            "Import_excel_db.html",
            {
                "result": "Please select a file to upload",
                "object_list": "",
                "run_id": "",
                "onboardlist": "",
                "invalidlist": "",
                "hostname_duplicates": "",
                "readylist": "",
                "upload_id": "",
                "options": options,
                "sorted_appname":sorted_appname,
                "sorted_appid": sorted_appid
            },
        )



def Import_excel(request):
    if request.method == "POST":
        ServerPatchDetails = ServerPatchDetailsResource()
        dataset = Dataset()
        new_Task = request.FILES["myfile"]
        data_import = dataset.load(new_Task.read())
        result = ServerPatchDetailsResource.import_data(dataset, dry_run=True)
        if not result.has_errors():
            ServerPatchDetailsResource.import_data(dataset, dry_run=False)
    return render(request, "Import_excel_db.html", {})


def trackupload_task(request):
    unique_uploadid_values = (
        ServerPatchDetails.objects.values("uploadid", "instance__appname")
        .distinct()
        .order_by(
            "-uploadid",
            "instance__appname",
        )
    )
    # print(unique_uploadid_values)
    unique_skipped_values = (
        SkippedServers.objects.values("uploadid").distinct().order_by("-uploadid")
    )
    return render(
        request,
        "track_upload.html",
        {"valid": unique_uploadid_values, "skipped": unique_skipped_values},
    )


def trackresult_task(request, uploadid=None, result=None):
    # result=None
    runid = ""
    logger.debug("getting into trackresult_task ")
    if (request.method == "POST" and request.POST["upload_id"]) or uploadid:
        if uploadid:
            val = uploadid
        else:
            val = request.POST["upload_id"]

        logger.debug("Upload ID : " + val)
        # task = Task.objects.get(hostname=val)
        masterdata= ServerPatchDetails.objects.filter( Q(uploadid__in=[val]))

        object_list = masterdata.filter(
            (
                Q(state__icontains="New")
                | Q(state__icontains="ReCheck")
                | Q(state__icontains="Inprogress")
            )
        ).order_by("-update_date")

        blocked_object_list = masterdata.filter(
           Q(state__icontains="Blocked")
            & (Q(action__icontains="Credentials Failed") )
        ).order_by("-update_date")
        mpaFailed = masterdata.filter(
            Q(action__icontains="MPA Failed") |Q(action__icontains="Reonboard")
        ).order_by("-update_date")
        skipped_object_list = SkippedServers.objects.filter(uploadid__in=[val])
        upload_run = ""
        onboardobject_list =masterdata.filter(
            Q(action__icontains="To be Scheduled")
            & (Q(state__icontains="New") | Q(state__icontains="Recheck"))
        )
        reonboarding_list = onboardobject_list.filter(Q(state__icontains="ReCheck") 
        )
        complete_object_list = masterdata.filter( Q(state__icontains="Completed")
        )
        failed_object_list = masterdata.filter((Q(state__icontains="Failed") | Q(action__icontains="Patch Failed"))
        )
        logger.debug(
            "onboard == "
            + str(len(onboardobject_list))
            + "MpaFailed=="
            + str(len(mpaFailed))
            + " validobject == "
            + str(len(object_list))
            + " reonboarding_list "
            + str(len(reonboarding_list))
            + " complete_object_list "
            + str(len(complete_object_list))
            + "failed_object_list"
            + str(len(failed_object_list))
        )

        if len(onboardobject_list) > 0 and len(reonboarding_list) <= 0:
            upload_run = "successful"
        elif len(mpaFailed) > 0:
            upload_run = "mpaFailed"
        # elif len(reonboarding_list) >= 0:
        #    upload_run = "successful"
        elif len(onboardobject_list) > 0 and len(reonboarding_list) >= 0:
            upload_run = "pending"
        elif len(object_list) <= 0:
            upload_run = ""
        else:
            runid = object_list[0].runid
            logger.debug("proceeding to retrive runid " + runid)
            upload_run_obj = Upload_runid.objects.filter(
                Q(uploadid__in=[val]) & Q(runid__in=[runid])
            )
            if len(upload_run_obj) > 0:
                upload_run = upload_run_obj[0].action
            logger.debug("upload_run  :: " + str(upload_run))
        if (
            len(object_list) <= 0
            and len(skipped_object_list) <= 0
            and len(reonboarding_list) <= 0
            and len(blocked_object_list) <= 0
            and len(complete_object_list) <= 0
            and len(mpaFailed) <= 0
        ):
            result = "No details found for given Upload Id"
            logger.debug("No details found for given Upload Id")
        logger.debug("result :: " + str(result))
        if str(result) == "None":
            return render(
                request,
                "trackrun_output.html",
                {
                    "skipped": skipped_object_list,
                    "result": result,
                    "upload_id": val,
                    "allobjects": object_list,
                    "blocked_object_list": blocked_object_list,
                    "complete_object_list": complete_object_list,
                    "failed_object_list": failed_object_list,
                    "upload_run": upload_run,
                    "mpaFailed": mpaFailed,
                    "run_id": runid,
                },
            )
        else:
            return render(
                request,
                "trackrun_task.html",
                {
                    "result": result,
                    "upload_id": val,
                    "upload_run": upload_run,
                    "run_id": runid,
                },
            )
    else:
        return render(request, "trackrun_task.html", {"result": ""})


def invokempa(request, uploadid, operation):
    isreboot = False
    logger.debug("inside invokempa  " + uploadid + "  operation  " + operation)
    if operation is None:
        object_list = ServerPatchDetails.objects.filter(
            Q(uploadid__in=[uploadid])
            & Q(action__icontains="To be Scheduled")
            & (Q(state__icontains="New") | Q(state__icontains="ReCheck"))
        )
    elif operation == "reboot":
        
        isreboot = True
    else:
        object_list = ServerPatchDetails.objects.filter(
            Q(uploadid__in=[uploadid])
            & (
                (
                    Q(action__icontains="To be Scheduled")
                    & (Q(state__icontains="New") | Q(state__icontains="ReCheck"))
                )
                | (Q(action__icontains="MPA Failed") & Q(state__icontains="Blocked"))
                | (Q(action__icontains="Reonboard") & Q(state__icontains="Blocked"))
            )
        )
    if len(object_list) <= 0:
        context = {"uploadid": uploadid}
        return HttpResponseRedirect(
            "/trackresult/" + uploadid + "/No Active Server to Patch"
        )
    else:
        logger.debug(object_list[0].runid)
        context = {
            "objects": object_list,
            "uploadid": uploadid,
            "runid": object_list[0].runid,
            "isreboot": isreboot,
        }
        return render(request, "onboard_servers.html", context)


def invokeplaywright(request):

    result = ""
    if (
        request.method == "POST"
        and request.POST["username"]
        and request.POST["password"]
    ):
        uploadid = request.POST["uploadid"]
        runid = request.POST["runid"]
        isreboot = request.POST["isreboot"]

        logger.debug(
            "inside invokeplaywright  by "
            + request.POST["username"]
            + "  for "
            + uploadid
            + "  runid "
            + runid
            + " isreboot  "
            + isreboot
        )

       
        filepath = host_file_path +"/"+ runid +"_ERROR.csv"
        
        logger.debug("inside onboard module")
        filepath = host_file_path + "/" + runid + "_host_onboard.csv"
        reonboard_list = ServerPatchDetails.objects.filter(
            Q(uploadid__in=[uploadid])
            & (
                (Q(action__icontains="MPA Failed") & Q(state__icontains="Blocked"))
                | (Q(action__icontains="Reonboard") & Q(state__icontains="Blocked"))
                | (
                    Q(action__icontains="To be Scheduled")
                    & Q(state__icontains="ReCheck")
                )
            )
        ).distinct()
        if len(reonboard_list) > 0:
        #    runid = generate_runid(uploadid)
            update_server_objects(
                uploadid,
                reonboard_list,
                runid,
                "ReCheck",
                "To be Scheduled",
                "ReOnboard Server",
            )

        object_list = ServerPatchDetails.objects.filter(
            Q(uploadid__in=[uploadid])
            & Q(action__icontains="To be Scheduled")
            & Q(state__icontains="New")
        ).distinct()
        if len(object_list) > 0:
            update_server_objects(
                uploadid,
                object_list,
                runid,
                "New",
                "To be Scheduled",
                "Onboard Server",
            )
        logger.debug("******")
        logger.debug(filepath)
        logger.debug("*******")
        # Open the file in write mode
        with open(filepath, "w") as f:
            # Write each item to the file, one item per line
            for server in object_list:
                f.write(
                    server.hostname
                    + ","
                    + server.defaultuser.replace("\n", "~~").replace("\r", "^^")
                    + ","
                    + server.defaultpass.replace("\n", "~~").replace("\r", "^^")
                    + "\n"
                )
            for server in reonboard_list:
                f.write(
                    server.hostname
                    + ","
                    + server.defaultuser.replace("\n", "~~").replace("\r", "^^")
                    + ","
                    + server.defaultpass.replace("\n", "~~").replace("\r", "^^")
                    + "\n"
                )
        f.close()

        uname = request.POST["username"]
        passwd = request.POST["password"]
        euname = encrypt(uname)
        epasswd = encrypt(passwd)
        # logger.debug(uname,passwd,euname,epasswd)
        # logger.debug(decrypt(euname))
        # logger.debug(decrypt(epasswd))

        with open(prop_file_path + "/" + runid + "_playwrightmetadata.csv", "w") as f:
            f.write("mpaUsername$$" + str(euname) + "\n")
            f.write("mpaPassword$$" + str(epasswd) + "\n")
            f.write("baseUrl$$" + mpa_url + "\n")
            f.write("hostFilePath$$user_files/" + runid + "_host_onboard.csv" + "\n")
            f.write("rebootFilePath$$user_files/" + runid + "_host_reboot.csv" + "\n")
            f.write("ymlFilePath$$user_files/" + runid + "_host_onboard.yml" + "\n")
            f.write("passwordFilePath$$user_files/" + runid + "_withcreds.csv\n")
            f.write("traceFilePath$$user_files/" + runid + "_trace.zip\n")
            f.write("uploadid$$" + uploadid + "\n")
            f.write("runid$$" + runid + "\n")
            f.write("isreboot$$" + isreboot + "\n")
        f.close()
        # Create a background thread
        thread = threading.Thread(
            target=callplaywirght, args=(runid + "_playwrightmetadata.csv",)
        )
        # Start the background thread
        thread.start()
        result = "Request Submitted Successfully- Servers will be ON-BOARDED into ITOPS framework in sometime"
        return HttpResponseRedirect("/trackresult/" + uploadid + "/" + result)
    else:
        result = "Please Enter your BT credentials to Access MPA"
    logger.debug("returning from  playwright action.")
    return render(request, "onboard_response.html", {"result": result})


def download_template(request):
    file_path = "Server_template.xlsx"
    with open(file_path, "rb") as f:
        response = HttpResponse(
            f.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f"attachment; filename=Server_template.xlsx"
        return response
    

def add_application(request):
    if request.method=="POST":
        lot1=request.POST.get("lot").upper()
        appname1=request.POST.get("appname").upper()
        appid1=request.POST.get("appid").upper()
        print("=========================================")
        print(lot1)
        print(appname1)
        print(appid1)
        print("==========================================")


        Instance(lot=lot1,appid=appid1,appname=appname1).save()
        result="Successfully Inserted"
        context={
            "result":result,
        }
        return render(request,"add_instance.html",context)
    else:
        result="Please Enter Application Details"
        context={
            "result":result,
        }
        return render(request,"add_instance.html",context)
    
