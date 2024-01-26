#!/bin/bash

# run with sudo

ansible-galaxy install nvidia.nvidia_driver,v2.3.0

MAIN_SCRIPT="./tasks/benchmark/main.yaml"
INVENTORY="./tasks/benchmark/inventory.txt"

SRVR_FASILKOM_VARS=""
SRVR_FASILKOM_VARS="ansible_password=k0s0ng2024 $SRVR_FASILKOM_VARS"
SRVR_FASILKOM_VARS="ansible_sudo_pass=k0s0ng2024 $SRVR_FASILKOM_VARS"
SRVR_FASILKOM_VARS="ansible_host=10.119.106.22 $SRVR_FASILKOM_VARS"
SRVR_FASILKOM_VARS="ansible_user=admin $SRVR_FASILKOM_VARS"


sudo env ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook "$MAIN_SCRIPT" -i "$INVENTORY" -e "$SRVR_FASILKOM_VARS"




export ANSIBLE_EXTRAVARS="ansible_host=$1 ansible_user=immanuel01 ansible_ssh_private_key_file=~/.ssh/gcp"
#sudo ansible-playbook ./tasks/benchmark/main.yaml -i ./tasks/benchmark/inventory.txt -e "$ANSIBLE_EXTRAVARS"
#sudo ansible-playbook ./tasks/benchmark/main.yaml -i ./tasks/benchmark/inventory.txt -e "$ANSIBLE_EXTRAVARS" --start-at-task="chmod prime-run"