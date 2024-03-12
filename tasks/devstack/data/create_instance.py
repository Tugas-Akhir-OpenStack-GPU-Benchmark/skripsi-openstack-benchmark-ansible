#!/usr/bin/python3

import os
import pprint
import shlex
import subprocess
import json
from time import sleep

FLAVOR_NAME = "gpuflavor"
PCI_ALIAS = "T4"

def main():
    source_bash_script("/opt/stack/admin-openrc.sh")
    os.environ["OS_PASSWORD"] = "{{admin_password}}"
    delete_all_current_instance_with_gpuflavor()
    delete_gpuflavor_if_exists()
    create_gpuflavor()
    instance_id = create_instance("gpuflavor_instance")
    print(show_instance_status(instance_id))


def delete_all_current_instance_with_gpuflavor():
    output = run_command("openstack server list --format=json", True)
    for instance in output:
        if instance['Flavor'] == FLAVOR_NAME:
            name = instance['Name']
            print(f"Deleting {name}")
            run_command(f"openstack server delete \"{name}\"")

def delete_gpuflavor_if_exists():
    if get_gpuflavor_id_if_exists() is None:
        return
    id_ = get_gpuflavor_id_if_exists()
    run_command(f"openstack flavor delete {id_}")


def get_gpuflavor_id_if_exists():
    output = run_command("openstack flavor list --format=json", True)
    for flavor in output:
        if flavor['Name'] == FLAVOR_NAME:
            return flavor['ID']
    return None


def create_gpuflavor():
    run_command(f'openstack flavor create --ram 2048 --disk 30 --vcpu 2 "{FLAVOR_NAME}"')
    run_command(f'openstack flavor set "{FLAVOR_NAME}" --property "pci_passthrough:alias"="{PCI_ALIAS}:1"')
    run_command(f'openstack flavor set --property hw:numa_nodes=1 --property hw:numa_cpus.0=0,1 --property hw:numa_mem.0=2048 "{FLAVOR_NAME}"')


def create_instance(instance_name):
    output = run_command(f'openstack server create --flavor {FLAVOR_NAME} --image Ubuntu2004 --nic net-id={get_private_network_id()} --security-group {get_security_group_id("demo")} --key-name created_by_ansible "{instance_name}" --format=json', True)
    return output['id']



def get_security_group_id(project_name):
    security_groups = run_command(f'openstack security group list --project="{project_name}" --format=json', True)
    for sec_group in security_groups:
        if sec_group['Name'] == "default":
            return sec_group['ID']
    raise Exception(f"Either project {project_name} does not exist or security group default does not exist")


def get_private_network_id():
    network_list = run_command(f'openstack network list --format=json', True)
    for network in network_list:
        if network['Name'] == "private":
            return network['ID']
    raise Exception("private network is not found")


def show_instance_status(instance_id):
    while True:
        output = run_command(f"openstack server show {instance_id} --format=json", True)
        if output['status'] in ('ERROR', 'ACTIVE'):
            break
        sleep(0.1)
    return output['status'], output.get('fault', "-")


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


def run_command(command, is_json=False):
    assert "'" not in command
    command = shlex.split(f"bash -c '{command}'")
    proc = subprocess.Popen(command, stdout = subprocess.PIPE)
    output, *_ = proc.communicate()
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


if __name__ == "__main__":
    main()