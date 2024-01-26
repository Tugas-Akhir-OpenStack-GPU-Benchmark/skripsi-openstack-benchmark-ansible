#!/bin/bash

# run with sudo

ansible-galaxy install nvidia.nvidia_driver,v2.3.0


sudo env ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook ./tasks/benchmark/main.yaml -i ./tasks/benchmark/inventory.txt \
  -e "ansible_host=10.119.106.22 ansible_password=k0s0ng2024"

#sudo ansible-playbook  ./tasks/benchmark/main.yaml -i ./tasks/benchmark/inventory.txt -e "ansible_host=$1"
#sudo ansible-playbook  ./tasks/benchmark/main.yaml -i ./tasks/benchmark/inventory.txt --start-at-task="chmod prime-run" -e "ansible_host=$1"
