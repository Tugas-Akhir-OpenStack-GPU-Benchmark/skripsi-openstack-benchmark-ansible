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


#sudo env ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook "$MAIN_SCRIPT" -i "$INVENTORY" -e "$SRVR_FASILKOM_VARS"



if [ -z "$1" ]; then
    echo "Please provide SSH host (IP address) of the controller-instance as the first argument"
    exit
fi


ansible_ssh_common_args=''

if [ -n "$2" ]; then
    ansible_ssh_common_args='$ansible_ssh_common_args -J $2'
    echo "jumphost 1 detected"
fi

if [ -n "$3" ]; then
    ansible_ssh_common_args='$ansible_ssh_common_args $3'
    echo "jumphost 2 detected"
fi


export ANSIBLE_EXTRAVARS="ansible_host=$1 ansible_user=immanuel01 ansible_ssh_private_key_file=~/.ssh/gcp"
export ANSIBLE_EXTRAVARS="$ANSIBLE_EXTRAVARS ansible_ssh_common_args=\"$ansible_ssh_common_args\""
sudo ansible-playbook ./tasks/benchmark/main.yaml -i ./tasks/benchmark/inventory.txt -e "$ANSIBLE_EXTRAVARS"
#sudo ansible-playbook ./tasks/benchmark/main.yaml -i ./tasks/benchmark/inventory.txt -e "$ANSIBLE_EXTRAVARS" --start-at-task="chmod prime-run"