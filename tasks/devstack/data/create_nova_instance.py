#!/usr/bin/python3

import os
import pprint
import shlex
import subprocess
import json
import sys
from time import sleep

GPU_INSTANCE_NAME = "gpu-benchmark"
ANSIBLE_INSTANCE_NAME = "ansible"
FLAVOR_NAME = "gpuflavor"
PCI_ALIAS = "{{gpu_pci_openstack_alias_name}}"


def main():
    source_bash_script("/opt/stack/admin-openrc.sh")
    os.environ["OS_PASSWORD"] = sys.argv[1]
    if sys.argv[2] == "gpu":
        create_gpu_instance()
    elif sys.argv[2] == "ansible":
        create_ansible_instance()
    else:
        raise Exception(f"Command not found: {sys.argv[2]}")



def create_gpu_instance():
    delete_all_current_instance_with_given_criteria(flavor_name=FLAVOR_NAME, instance_name=GPU_INSTANCE_NAME)
    delete_gpuflavor_if_exists()
    create_gpuflavor()
    instance_id = create_instance(GPU_INSTANCE_NAME)
    instance_status = show_instance_status(instance_id)
    print(instance_status[0])
    print(instance_status[1])
    if instance_status[0].lower() == "error":
        print("Stopped due to error...")
        exit(1)
    floating_ip = attach_to_a_floating_ip(instance_id)
    print(f"GPU instance {instance_id} created with floating IP: {floating_ip}")


def create_ansible_instance():
    instances = get_all_current_instance_with_given_criteria(instance_name=ANSIBLE_INSTANCE_NAME)
    if len(instances) > 0:
        print(f"ALREADY EXIST: Ansible instance {instances[0]['ID']}")
        return
    instance_id = create_instance(ANSIBLE_INSTANCE_NAME, "m1.small", allow_error=True)  # allow error if duplicate already exists
    if isinstance(instance_id, Error):
        print(instance_id.msg)
    floating_ip = attach_to_a_floating_ip(instance_id)
    print(f"Ansible instance {instance_id} created with floating IP: {floating_ip}")


def delete_all_current_instance_with_given_criteria(flavor_name=None, instance_name=None):
    output = run_command("openstack server list --format=json", True)
    for instance in output:
        if instance['Flavor'] == flavor_name or instance['Name'] == instance_name:
            name = instance['Name']
            instance_id = instance['ID']
            print(f"Deleting {name}: {instance_id}")
            run_command(f"openstack server delete \"{instance_id}\"")


def get_all_current_instance_with_given_criteria(flavor_name=None, instance_name=None):
    ret = []
    output = run_command("openstack server list --format=json", True)
    for instance in output:
        if instance['Flavor'] == flavor_name or instance['Name'] == instance_name:
            ret.append(instance)
    return ret


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
    run_command(f'openstack flavor create --ram 4096 --disk 40 --vcpu 6 "{FLAVOR_NAME}"')
    if PCI_ALIAS is not None:
        run_command(f'openstack flavor set "{FLAVOR_NAME}" --property "pci_passthrough:alias"="{PCI_ALIAS}:1"')
    #run_command(f'openstack flavor set --property hw:numa_nodes=1 --property hw:numa_cpus.0=0,1 --property hw:numa_mem.0=2048 "{FLAVOR_NAME}"')


def create_instance(instance_name, flavor=FLAVOR_NAME, allow_error=False):
    output = run_command(f'openstack server create --flavor {flavor} --image Ubuntu2004 --nic net-id={get_private_network_id()} --security-group {get_security_group_id("demo")} --key-name created_by_ansible "{instance_name}" --format=json',
                         True, allow_error=allow_error)
    if isinstance(output, Error):
        return output
    return output['id']



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


def show_instance_status(instance_id):
    for i in range(200):
        output = run_command(f"openstack server show {instance_id} --format=json", True)
        if output['status'] in ('ERROR', 'ACTIVE'):
            break
        sleep(0.1)
    else:
        raise Exception(f"Timed out waiting instance status to be ACTIVE/ERROR. Stuck state: {output['status']}")
    return output['status'], output.get('fault', "-")


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