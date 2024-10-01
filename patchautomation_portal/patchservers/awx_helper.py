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

import json
import logging
from django.db.models import Q
import requests
from . import variables

from .models import ServerPatchDetails
from .utility import generate_hostcsv, generte_masteryml

logger = logging.getLogger('awx_helper')

awx_url = variables.awx_url

host_file_path = variables.host_file_path
prop_file_path = variables.prop_file_path




def callget_serverdetails(runid):
    logger.debug("calling the AWX to get server details ")
    filepath = host_file_path + "/" + runid + "_get_server_details"
    object_list = ServerPatchDetails.objects.filter(
        Q(runid__in=[runid])
        & Q(action__icontains="Pipelined")
        & Q(state__icontains="New")
    )

    # Open the file in write mode
    if object_list:
        generate_hostcsv(filepath, object_list)
        generte_masteryml(filepath, object_list)
        data = {
            "host_csv": filepath + ".csv",
            "task": "get_server_details",
            "run_id": str(runid),
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(awx_url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            logger.debug("Success!", response.content)
        else:
            logger.debug("Error:", response.status_code)
    else:
        logger.debug(
            "skipping callonboardchecker "
            + filepath
            + " file creations, as we have no valid records"
        )
    logger.debug("returning from getserver Details action.")

  
  
def callonboardchecker(runid):
    logger.debug("calling the AWX to check if we have ITOPS User")
    filepath = host_file_path + "/" + runid + "_onboard_check"
    object_list = ServerPatchDetails.objects.filter(
        Q(runid__in=[runid])
        & Q(action__icontains="To be Scheduled")
        & Q(state__icontains="ReCheck")
    )

    # Open the file in write mode
    if object_list:
        generate_hostcsv(filepath, object_list)
        generte_masteryml(filepath, object_list)
        data = {
            "host_csv": filepath + ".csv",
            "task": "onboard_check",
            "run_id": str(runid),
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(awx_url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            logger.debug("Success!", response.content)
        else:
            logger.debug("Error:", response.status_code)
    else:
        logger.debug(
            "skipping callonboardchecker "
            + filepath
            + " file creations, as we have no valid records"
        )
    logger.debug("returning from callonboardchecker action.")



