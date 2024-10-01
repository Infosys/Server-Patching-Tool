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

import urllib3
import os
import requests
import pandas as pd
from pydantic import BaseModel
import properties

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

user_name = properties.user_name
password = properties.password

host = properties.host
port = properties.port
protocol = properties.protocol
vault_id = properties.vault_id
omd_ssh_key_cred_id = properties.omd_ssh_key_cred_id
itops_ssh_key_cred_id = properties.itops_ssh_key_cred_id

# master_vault = '/app/var/docker/overlay2/33b5abd3005b2adc5b63f015a1551e6eb2b60d8111698df36eda2b72e65650f0/merged/var' \
#               '/lib/awx/projects/zeroops/Vault/'
master_vault = properties.master_vault



class awx_data(BaseModel):
    host_csv: str
    task: str
    run_id: str


def create_job_template(template_name, inventory_id, project_id, playbook_name, extra_variables):
    print(f"creating a job template for {template_name}")
    url = f"{protocol}://{host}:{port}/api/v2/job_templates/"
    body = {
        "name": template_name, "description": "", "job_type": "run", "inventory": inventory_id, "project": project_id,
        "playbook": playbook_name,
        "scm_branch": "", "forks": 30, "limit": "", "verbosity": 0, "extra_vars": extra_variables, "job_tags": "",
        "force_handlers": "false", "skip_tags": "", "start_at_task": "", "timeout": 0, "use_fact_cache": "false",
        "execution_environment": "", "host_config_key": "", "ask_scm_branch_on_launch": "false",
        "ask_diff_mode_on_launch": "false", "ask_variables_on_launch": "false", "ask_limit_on_launch": "false",
        "ask_tags_on_launch": "false", "ask_skip_tags_on_launch": "false", "ask_job_type_on_launch": "false",
        "ask_verbosity_on_launch": "false", "ask_inventory_on_launch": "false", "ask_credential_on_launch": "true",
        "ask_execution_environment_on_launch": "false", "ask_labels_on_launch": "false", "ask_forks_on_launch": "false",
        "ask_job_slice_count_on_launch": "false", "ask_timeout_on_launch": "false",
        "ask_instance_groups_on_launch": "false",
        "survey_enabled": "false", "become_enabled": "false", "diff_mode": "false", "allow_simultaneous": "false",
        "job_slice_count": 1, "webhook_service": "", "webhook_credential": "",
        "prevent_instance_group_fallback": "false"
    }
    response = requests.post(url=url, auth=(user_name, password), json=body, verify=False).json()
    return response


def get_job_template_data(template_id):
    print(f"Getting template data for : {template_id}")
    url = f"{protocol}://{host}:{port}/api/v2/job_templates/{str(template_id)}/"
    response = requests.get(url=url, auth=(user_name, password), verify=False)
    return response.json()


def update_job_template(template_id, extra_vars):
    print(f"Updating the job template : {template_id} , with vars : {extra_vars}")
    job_template_data = get_job_template_data(template_id)
    url = f"{protocol}://{host}:{port}/api/v2/job_templates/{str(template_id)}/"
    job_template_data['extra_vars'] = extra_vars
    response = requests.put(url=url, auth=(user_name, password), json=job_template_data, verify=False)
    return response.status_code


def launch_job_template(job_template_id):
    print(f"Launching the job for template: {job_template_id}")
    launch_creds = {
        "monitorit": ['get_server_details', 'onboard_hosts', 'onboard_reboot_hosts', 'latest_patch_checker'],
        "itops": ['onboard_check', 'onepatch_execution', 'server_reboot']
    }
    job_template_data = get_job_template_data(job_template_id)
    base_template_name = job_template_data['name']
    parts = base_template_name.split("_2")

    print("Extract the base template name"+ base_template_name+"  split data "+ str(parts))
    template_name = parts[0]
    url = f"{protocol}://{host}:{port}/api/v2/job_templates/{str(job_template_id)}/launch/"
    if template_name in launch_creds["monitorit"]:
        cred_list = [vault_id, omd_ssh_key_cred_id]
    elif template_name in launch_creds["itops"]:
        cred_list = [vault_id, itops_ssh_key_cred_id]
    else:
        cred_list = [vault_id]
    body = {
        # "credentials": [vault_id]
        "credentials": cred_list
    }
    response = requests.post(url=url, auth=(user_name, password), json=body, verify=False).json()
    print(f"launched template, with job ID: {response['id']}")
    return response


def create_inventory(name, inventory_variables):
    print(f"Creating Inventory : {name}")
    inventory_data = {
        "name": name,
        "description": "",
        "organization": "1",
        "kind": "",
        "variables": inventory_variables,
        "prevent_instance_group_fallback": "false"
    }
    url = f"{protocol}://{host}:{port}/api/v2/inventories/"
    response = requests.post(url=url, auth=(user_name, password), json=inventory_data, verify=False)
    return response.json()


def inventory(inventory_name, extra_vars):
    print("Getting inventory Data")
    url = f"{protocol}://{host}:{port}/api/v2/inventories/"
    response = requests.get(url=url, auth=(user_name, password), verify=False).json()
    if len(response['results']) > 0:
        for i in response['results']:
            if inventory_name == i['name']:
                return i
    else:
        inventory_creation = create_inventory('master_inventory', extra_vars)
        return inventory_creation


def get_all_hosts():
    print("Getting all hosts Details")
    url = f"{protocol}://{host}:{port}/api/v2/hosts/?page_size=100&"
    response = requests.get(url=url, auth=(user_name, password), verify=False).json()
    return response


def create_host(host_name, inventory_id, host_variables):
    print(f"creating host : {host_name}")
    host_data = {
        "name": host_name,
        "description": "",
        "inventory": inventory_id,
        "enabled": "true",
        "instance_id": "",
        "variables": host_variables
    }
    url = f"{protocol}://{host}:{port}/api/v2/hosts/"
    response = requests.post(url=url, auth=(user_name, password), json=host_data, verify=False)
    print(f"Creating host response: {response.json()}")
    return response.json()


def create_host_group(name, inventory_id):
    print(f"Creating host group : {name}")
    group_data = {
        "name": name,
        "description": "",
        "inventory": inventory_id,
        "variables": ""
    }
    url = f"{protocol}://{host}:{port}/api/v2/inventories/{inventory_id}/groups/"
    response = requests.post(url=url, auth=(user_name, password), json=group_data, verify=False).json()
    return response


def add_host_in_group(host_name, group_id):
    print(f"adding {host_name} in {group_id}")
    host_data = {
        "name": host_name,
        "description": "",
        "enabled": "true",
        "instance_id": "",
        "variables": ""
    }
    url = f"{protocol}://{host}:{port}/api/v2/groups/{group_id}/hosts/"
    response = requests.post(url=url, auth=(user_name, password), json=host_data, verify=False)
    return response.status_code


def create_project(name):
    print(f"Creating project: {name}")
    project_body = {
        "name": name,
        "description": "",
        "local_path": name,
        "scm_type": "",
        "scm_url": "",
        "scm_branch": "",
        "scm_refspec": "",
        "scm_clean": "false",
        "scm_track_submodules": "false",
        "scm_delete_on_update": "false",
        "credential": "",
        "timeout": 0,
        "organization": "",
        "scm_update_on_launch": "false",
        "scm_update_cache_timeout": 0,
        "allow_override": "false",
        "default_environment": "",
        "signature_validation_credential": ""
    }
    url = f"{protocol}://{host}:{port}/api/v2/projects/"
    response = requests.post(url=url, auth=(user_name, password), json=project_body, verify=False).json()
    return response


def get_project_details(project_name):
    print("Getting Project Details")
    url = f"{protocol}://{host}:{port}/api/v2/projects/"
    response = requests.get(url=url, auth=(user_name, password), verify=False).json()
    for project in response['results']:
        if project['name'] == project_name:
            return project['id']
    project = create_project(project_name)
    return project['id']


def job_template(template_name, inventory_id, project_id, playbook_name, extra_variables):
    print(f"getting the template {template_name}")
    url = f"{protocol}://{host}:{port}/api/v2/job_templates/"
    response = requests.get(url=url, auth=(user_name, password), verify=False).json()
    if len(response['results']) > 0:
        for i in response['results']:
            if i['name'] == template_name:
                update_job_template(i['id'], extra_variables)
                return i
    create_template = create_job_template(template_name, inventory_id, project_id, playbook_name, extra_variables)
    return create_template


def add_notification_to_template(id: int, template_id):
    url = f"{protocol}://{host}:{port}/api/v2/job_templates/{str(template_id)}/notification_templates_success/"
    notification_body = {"id": id}
    success_notification_response = requests.post(url=url, auth=(user_name, password), json=notification_body,
                                                  verify=False)
    print('***************')
    print(success_notification_response)
    print('***************')
    url = f"{protocol}://{host}:{port}/api/v2/job_templates/{str(template_id)}/notification_templates_error/"
    error_notification_response = requests.post(url=url, auth=(user_name, password), json=notification_body,
                                                verify=False)
    if str(success_notification_response.status_code) and str(error_notification_response.status_code) == "204":
        return f"Added notification successfully for template : {template_id}"
    print(f"Success Notification for template-{template_id} : {success_notification_response.text}")
    print(f"Success Notification for template-{template_id} : {error_notification_response.text}")
    return f"Notification Adding failed for template : {template_id}"


def check_file(file_name):
    return os.path.exists(file_name)


def get_notification_id(task):
    if task == "onboard_hosts" or task == "onboard_check":
        return 2
    elif task == "onboard_reboot_hosts":
        return 3
    else:
        return 1


def awx_handler(data):
    print(f"AWX Handler Invoked with data: {data}")
    host_csv = data.host_csv
    task = data.task
    run_id = data.run_id
    if not check_file(host_csv):
        print(f"host csv not found: {host_csv}")
        return f"{host_csv} not found"
    notification_template_id = get_notification_id(task)
    file_name = str(host_csv.split('/')[-1]).split('.')[0]
    print(file_name)
    host_data = pd.read_csv(host_csv)
    print(host_data['host'].values)
    project_id = get_project_details("zeroops")
    inventory_id = inventory('master_inventory', "")['id']
    host_group = create_host_group(f"{task}_{file_name}_group", inventory_id)
    if "already exists" in str(host_group):
        print("Host Group ALready Exists")
        return "Host Group Already Exists"
    print(f"host_group ID : {host_group['id']}")

    # if task != 'onepatch_execution' and task != 'server_reboot':
    if task == 'onboard_hosts' or task == 'onboard_reboot_hosts':
        host_yml = str(host_csv.split('.')[0] + ".yml").strip()

        host_csv_data = ''
        with open(host_yml, 'r') as host_file:
            host_csv_data = host_file.read()
        print("Fetched data from yml")

        with open(master_vault + file_name + ".yml", 'w') as vault_file:
            print("Vault written")
            vault_file.write(host_csv_data)

        host_csv_content = ''
        with open(host_csv, 'r') as csv_file:
            host_csv_content = csv_file.read()
        print("Fetched data from yml")

        with open("/tmp/test_" + file_name + ".csv", 'w') as temp_csv:
            print("Vault written")
            temp_csv.write(host_csv_content)

    extra_vars = '{"encryptedPasswordFile": "Vault/' + file_name + '.yml", "run_id":"' + run_id + '", "host_group":"' + \
                 host_group["name"] + '"}'
    # template_details = job_template(f"{task}_job_template", inventory_id, project_id, f"{task}.yml", extra_vars)
    print("creating template")
    template_details = create_job_template(f"{task}_{file_name}_job_template", inventory_id, project_id, f"{task}.yml",
                                           extra_vars)
    print(template_details)
    print(add_notification_to_template(notification_template_id, template_details['id']))
    host_list = get_all_hosts()
    print("Host details Collected")
    print(host_data)
    for hosts in host_data['host']:
        print(hosts)
        try:
            if task != 'latest_patch_checker':
                create_host_resp = create_host(hosts, inventory_id, '{"ansible_host":"' + hosts + '"}')
        except urllib3.error.HTTPError as e:
            if '__all__' in create_host_resp:
                print(f"{hosts} already exists")
            else:
                print("Error: ", e)
        print(f"adding host {hosts} in group {task}_{file_name}_group")
        add_host_in_group(hosts, host_group['id'])
    #        if hosts in str(host_list):
    #            print(f"{hosts} already exists")
    #        else:
    #            print(create_host(hosts, inventory_id, '{"ansible_host":"' + hosts + '"}')["id"])
    #        print(f"adding host in group: {add_host_in_group(hosts, host_group['id'])}")
    launch_response = launch_job_template(template_details['id'])
    print(f"Job Template Launched with response: {launch_response}")
    return "Successful"


def generate_runid(upload_id):
    json_body = {"uploadid": str(upload_id)}
    url = '<url for generate runid>'
    response = requests.post(url=url, json=json_body)
    return response.json()['run_id']


def awx_patch_handler(patch_enabled_hosts, task):
    if len(patch_enabled_hosts) <= 0:
        return "No hosts available"
    run_id = generate_runid(patch_enabled_hosts[0][1])
    print(f"new run_id: {run_id}")
    patch_enabled_hosts = pd.DataFrame(patch_enabled_hosts)

    host_list = []
    for index, hosts in patch_enabled_hosts.iterrows():
        host_list.append(hosts[0])
    patch_data = awx_data
    patch_data.task, patch_data.run_id, patch_data.host_csv = task, run_id, master_vault + f'{run_id}_{task}.csv'
    pd.DataFrame(host_list).to_csv(master_vault + f'{run_id}_{task}.csv', header=['host'], index=False)
    pd.DataFrame(host_list).to_csv('/apps/zeroops/playwright/user_files/' + f'{run_id}_{task}.csv', header=['host'],
                                   index=False)
    awx_handler(patch_data)
    print(patch_data.task, patch_data.run_id, patch_data.host_csv)
    return "successful"
