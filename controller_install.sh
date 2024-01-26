#!/bin/bash

if [ -z "$1" ]; then
    echo "Please provide SSH host (IP address) of the controller-instance as the first argument"
    exit
fi

#sudo ansible-playbook ./tasks/openstack/compute-node/main.yaml -i ./tasks/openstack/inventory.txt -e "ansible_host=$1"
sudo ansible-playbook ./tasks/openstack/compute-node/main.yaml -i ./tasks/openstack/inventory.txt -e "ansible_host=$1"  --start-at-task="Populate the Identity service database"

