#!/bin/bash

# need trailing comma
sudo ansible-playbook auto_turnoff.yaml -i auto_turnoff_inventory.txt -e "ansible_host=$1"