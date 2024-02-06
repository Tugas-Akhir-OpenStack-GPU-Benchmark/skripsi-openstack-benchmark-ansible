#!/bin/bash

mkdir -p "temp/installed"
test ! -e "temp/installed/community.general" && ansible-galaxy collection install community.general  # v8.3.0
touch "temp/installed/community.general"

export ANSIBLE_EXTRAVARS="ansible_user=stack ansible_ssh_user=immanuel01 ansible_ssh_private_key_file=~/.ssh/gcp"

#sudo ansible-playbook ./tasks/devstack/main.yaml -i ./tasks/devstack/inventory.txt -e "$ANSIBLE_EXTRAVARS"
sudo ansible-playbook ./tasks/devstack/main.yaml -i ./tasks/devstack/inventory.txt -e "$ANSIBLE_EXTRAVARS" --start-at-task="check current username"