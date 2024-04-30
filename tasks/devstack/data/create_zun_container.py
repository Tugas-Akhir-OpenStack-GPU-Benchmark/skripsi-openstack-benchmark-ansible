#!/usr/bin/python3

import os
import pprint
import shlex
import subprocess
import json
import sys
from time import sleep

GPU_CONTAINER_NAME = "gpu-container"
# ANSIBLE_INSTANCE_NAME = "ansible"
IMAGE_NAME = "gpuimage"
PCI_ALIAS = "{{gpu_pci_openstack_alias_name}}"

def main():
    source_bash_script("/opt/stack/admin-openrc.sh")
    os.environ["OS_PASSWORD"] = sys.argv[1]
    if sys.argv[2] == "gpu":
        create_gpu_container()
    # elif sys.argv[2] == "ansible":
    #     create_ansible_container()
    else:
        raise Exception(f"Command not found: {sys.argv[2]}")
    
def create_gpu_container():
    delete_all_current_container_with_given_criteria(image_name=IMAGE_NAME, container_name=GPU_CONTAINER_NAME)
    delete_gpuimage_if_exists()
    create_gpuimage()
    # container_id = create_container(GPU_CONTAINER_NAME)
    # print(f"GPU container {container_id} created")
    # show_container_status(container_id)
    # print(container_status[0])
    # print(container_status[1])
    # if container_status[0].lower() == "error":
    #     print("Stopped due to error...")
    #     exit(1)
    # floating_ip = attach_to_a_floating_ip(container_id)
    # print(f"GPU container {container_id} created with floating IP: {floating_ip}")
    
def create_ansible_container():
    pass

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

def delete_gpuimage_if_exists():
    if get_image_id_if_exists() is None:
        return
    id_ = get_image_id_if_exists()
    run_command(f"openstack image delete {id_}")

def get_image_id_if_exists():
    output = run_command("openstack image list --format=json", True)
    for image in output:
        if image['Name'] == IMAGE_NAME:
            return image['ID']
    return None

def create_gpuimage():
    run_command(f"openstack image create  --file /opt/stack/Dockerfile --disk-format raw --container-format docker --public {IMAGE_NAME}")
    if PCI_ALIAS is not None:
        run_command(f'openstack image set --property "pci_passthrough:alias"="{PCI_ALIAS}:1" {IMAGE_NAME}')

def create_container(container_name, image_name=IMAGE_NAME, allow_error=False):
    output = run_command(f'openstack appcontainer create --name {container_name} --image-driver glance --net network={get_private_network_id()} --security-group {get_security_group_id("demo")} {image_name}', True, allow_error)
    if isinstance(output, Error):
        return output
    return output['uuid']
    
def get_security_group_id(project_name):
    security_groups = run_command(f'openstack security group list --project="{project_name}" --format=json', True)
    for sec_group in security_groups:
        if sec_group['Name'] == "default":
            return sec_group['ID']
    raise Exception(f"Either project {project_name} does not exist or security group default does not exist")

def get_private_network_id():
    return get_network_id("private")

def get_public_network_id():
    return get_network_id("public")

def get_network_id(name):
    network_list = run_command(f'openstack network list --format=json', True)
    for network in network_list:
        if network['Name'] == name:
            return network['ID']
    raise Exception(f"network with name '{name}' is not found")


def show_container_status(container_id):
    for _ in range(200):
        output = run_command(f"openstack appcontainer show {container_id} --format=json", True)
        if output['status'] in ('Error', 'Running'):
            break
        sleep(0.1)
    else:
        raise Exception(f"Timed out waiting instance status to be Error/Running. Stuck state: {output['status']}")
    return output['status'], output['status_reason']
    # print(output)
    
def get_list_of_available_floating_ips():
    return run_command("openstack floating ip list --status DOWN --format json", True)

def get_floating_ip_or_register_one():
    floating_ips = get_list_of_available_floating_ips()
    if len(floating_ips) > 0:
        return floating_ips[0]['Floating IP Address']
    run_command(f"openstack floating ip create {get_public_network_id()}")
    return get_floating_ip_or_register_one()


def attach_to_a_floating_ip(instance_id):
    choosen_floating_ip = get_floating_ip_or_register_one()
    output = run_command(f"openstack server add floating ip {instance_id} {choosen_floating_ip}", allow_error=True)
    if isinstance(output, Error) and 'already has a floating IP' not in output.msg:
        raise Exception(output.msg)
    return choosen_floating_ip

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