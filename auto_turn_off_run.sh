#!/bin/bash

# need trailing comma

if [ $# -eq 0 ]
then
    echo "No arguments supplied"
    exit
fi

i=0
for var in "$@"
do
    echo "$i setting auto shutdown for $var"
    ((i+=1))
    sudo ansible-playbook ./tasks/auto_turnoff/auto_turnoff.yaml -i ./tasks/auto_turnoff/auto_turnoff_inventory.txt -e "ansible_host=$var"
    echo "$i setting auto shutdown for $var"
done
echo "done"
