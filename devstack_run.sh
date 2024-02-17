#!/bin/bash

if [ $# -lt 2 ]
then
    echo "Need 2 arguments: CONTROLLER_SSH_IP COMPUTE_SSH_IP"
    exit
fi

export ANSIBLE_EXTRAVARS="ansible_ssh_user=immanuel01 ansible_ssh_private_key_file=~/.ssh/gcp"
export ANSIBLE_EXTRAVARS="$ANSIBLE_EXTRAVARS CONTROLLER_SSH_IP=$1 COMPUTE_SSH_IP=$2"
export ANSIBLE_CACHE_PLUGIN=jsonfile

sudo ansible-playbook ./tasks/devstack/main.yaml -i ./tasks/devstack/inventory.yml -e "$ANSIBLE_EXTRAVARS"
#sudo ansible-playbook ./tasks-openstack-core/devstack/main.yaml -i ./tasks-openstack-core/devstack/inventory.yml -e "$ANSIBLE_EXTRAVARS" --start-at-task="finalization"