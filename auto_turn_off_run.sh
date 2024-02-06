#!/bin/bash

# need trailing comma
sudo ansible-playbook ./tasks/auto_turnoff/auto_turnoff.yaml -i ./tasks/auto_turnoff/auto_turnoff_inventory.txt -e "ansible_host=$1"