#!/usr/bin/python3

import os
import pprint
import shlex
import subprocess
import json
import sys
from time import sleep

GPU_CONTAINER_NAME = "gpu-container"
IMAGE_NAME = "nvidia/cuda:12.4.1-cudnn-runtime-ubuntu20.04"

def main():
    source_bash_script("/opt/stack/admin-openrc.sh")
    os.environ["OS_PASSWORD"] = sys.argv[1]
    if sys.argv[2] == "gpu":
        create_gpu_container()
    else:
        raise Exception(f"Command not found: {sys.argv[2]}")
    
def create_gpu_container():
    delete_all_current_container_with_given_criteria(image_name=IMAGE_NAME, container_name=GPU_CONTAINER_NAME)
    container_uuid = create_container(GPU_CONTAINER_NAME)
    running_container_with_uuid(container_uuid)
    container_status = show_container_status(container_uuid)
    print(f"GPU container {container_uuid} created with status: {container_status[0]}")
    # print(f"GPU container {container_uuid} created with status: {container_status[0]}")
    # if container_status[0].lower() == "error":
    #     print("Stopped due to error...")
    #     exit(1)

def delete_all_current_container_with_given_criteria(image_name=None, container_name=None):
    output = run_command("openstack appcontainer list --format=json", True)
    for container in output:
        if container['image'] == image_name or container['name'] == container_name:
            name = container['name']
            instance_id = container['uuid']
            print(f"Deleting container {name}: {instance_id}")
            run_command(f"openstack appcontainer delete \"{instance_id}\"")

def get_all_current_container_with_given_criteria(image_name=None, container_name=None):
    ret = []
    output = run_command("openstack appcontainer list --format=json", True)
    for container in output:
        if container['image'] == image_name or container['name'] == container_name:
            ret.append(container)
    return ret

def create_container(container_name, image_name=IMAGE_NAME, allow_error=False):
    output = run_command(f'openstack appcontainer create --name {container_name} --privileged --security-group {get_security_group_id("demo")} {IMAGE_NAME} /bin/bash', True, allow_error)
    if isinstance(output, Error):
        return output
    return output['uuid']
    
def running_container_with_uuid(uuid):
    output = run_command(f"openstack appcontainer start {uuid}", allow_error=True)
    if isinstance(output, Error):
        return output
    return output

# def exec_container_with_uuid(uuid):
#     output = run_command(f"openstack appcontainer exec --interactive {uuid} /bin/bash", allow_error=True)
#     if isinstance(output, Error):
#         return output
#     return output

def get_security_group_id(project_name):
    security_groups = run_command(f'openstack security group list --project="{project_name}" --format=json', True)
    for sec_group in security_groups:
        if sec_group['Name'] == "default":
            return sec_group['ID']
    raise Exception(f"Either project {project_name} does not exist or security group default does not exist")

def show_container_status(container_id):
    for _ in range(200):
        output = run_command(f"openstack appcontainer show {container_id} --format=json", True)
        if output['status'] in ('Error', 'Running'):
            break
        sleep(0.1)
    else:
        raise Exception(f"Timed out waiting instance status to be Error/Running. Stuck state: {output['status']}")
    return output['status'], output['status_reason']
    
def source_bash_script(file_path, *arguments):
    assert ' ' not in file_path
    argument_str = ""
    for arg in arguments:
        assert ' ' not in arg
    argument_str = " ".join(arguments)

    command = shlex.split(f"bash -c 'source {file_path} ${argument_str} && env'")
    proc = subprocess.Popen(command, stdout = subprocess.PIPE)
    for line in proc.stdout:
        if isinstance(line, bytes):
            line = line.decode('utf-8')
        if not line.startswith("OS_"):
            continue
        (key, _, value) = line.partition("=")
        if value.endswith("\n"):  # strip only single character of end line
            value = value[:-1]
        os.environ[key] = value
    proc.communicate()


def run_command(command, is_json=False, allow_error=False):
    assert "'" not in command
    command = shlex.split(f"bash -c '{command}'")
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, stderr = proc.communicate()
    if allow_error and len(stderr) > 0:
        return Error(stderr)
    elif len(stderr) > 0:
        raise Exception(stderr.decode('utf-8'))

    if isinstance(output, bytes):
        output = output.decode('utf-8')
    output = output.split("\n")
    lines = []
    for line in output:
        lines.append(line)
    ret = "\n".join(lines)
    if is_json:
        try:
            ret = json.loads(ret)
        except Exception as e:
            print(ret)
            raise e
    return ret


class Error:
    def __init__(self, msg):
        if isinstance(msg, bytes):
            msg = msg.decode('utf-8')
        self.msg = msg


if __name__ == "__main__":
    main()