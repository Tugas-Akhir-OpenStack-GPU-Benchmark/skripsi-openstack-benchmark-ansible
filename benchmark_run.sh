#!/bin/bash

# run with sudo

ansible-galaxy install nvidia.nvidia_driver,v2.3.0

MAIN_SCRIPT="./tasks/benchmark/main.yaml"
INVENTORY="./tasks/benchmark/inventory.txt"



if [ -z "$1" ]; then
    echo "Please provide SSH host (IP address) of the controller-instance as the first argument"
    exit
fi



ansible_ssh_extra_args="-o StrictHostKeyChecking=no"
ansible_ssh_common_args="-o StrictHostKeyChecking=no"

export ANSIBLE_HOST_KEY_CHECKING=False
export ANSIBLE_EXTRAVARS="ansible_host=$1 ansible_ssh_private_key_file=~/.ssh/gcp"
export ANSIBLE_EXTRAVARS="$ANSIBLE_EXTRAVARS ansible_ssh_common_args=\"$ansible_ssh_common_args\""
export ANSIBLE_EXTRAVARS="$ANSIBLE_EXTRAVARS ansible_ssh_extra_args=\"$ansible_ssh_extra_args\""

if [ -n "$SUDO_PASS" ]; then
  ANSIBLE_EXTRAVARS="$ANSIBLE_EXTRAVARS ansible_sudo_pass=\"$SUDO_PASS\""
  echo "detected SUDO_PASS. Will use it for sudo authentication"
else
  echo "var SUDO_PASS is not set. Will assume target hosts don't need password to run sudo commands..."
fi

sudo ansible-playbook ./tasks/benchmark/main.yaml -i ./tasks/benchmark/inventory.txt -e "$ANSIBLE_EXTRAVARS"  --verbose
