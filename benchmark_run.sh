#!/bin/bash

# run with sudo

ansible-galaxy install nvidia.nvidia_driver,2.3.0

sudo ansible-playbook  ./tasks/benchmark/main.yaml -i ./tasks/benchmark/inventory.txt -e "ansible_host=$1"
#sudo ansible-playbook  ./tasks/benchmark/main.yaml -i ./tasks/benchmark/inventory.txt --start-at-task="chmod prime-run" -e "ansible_host=$1"
#sudo ansible-playbook  ./tasks/benchmark/main.yaml -i ./tasks/benchmark/inventory.txt --start-at-task="install libfreeimage" -e "ansible_host=$1"
