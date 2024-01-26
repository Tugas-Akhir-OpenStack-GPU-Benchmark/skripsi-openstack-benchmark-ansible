#!/bin/bash

# run with sudo

ansible-galaxy install nvidia.nvidia_driver,v2.3.0

MAIN_SCRIPT="./tasks/benchmark/main.yaml"
INVENTORY="./tasks/benchmark/inventory.txt"

SERVER_FASILKOM_EXTRAVARS="ansible_host=10.119.106.22 ansible_password=k0s0ng2024"

sudo env ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook "$MAIN_SCRIPT" -i "$INVENTORY" -e "$SERVER_FASILKOM_EXTRAVARS"


export ANSIBLE_EXTRAVARS="ansible_host=$1 ansible_user=immanuel01 ansible_ssh_private_key_file=~/.ssh/gcp"
#sudo ansible-playbook ./tasks/benchmark/main.yaml -i ./tasks/benchmark/inventory.txt -e "$ANSIBLE_EXTRAVARS"
#sudo ansible-playbook ./tasks/benchmark/main.yaml -i ./tasks/benchmark/inventory.txt -e "$ANSIBLE_EXTRAVARS" --start-at-task="chmod prime-run"
