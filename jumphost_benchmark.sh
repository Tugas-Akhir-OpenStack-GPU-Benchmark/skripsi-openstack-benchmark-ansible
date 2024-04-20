#!/bin/bash


ansible-galaxy install nvidia.nvidia_driver,v2.3.0

if [ -z "$1" ]; then
    echo "Please provide SSH host (IP address) of the controller-instance as the first argument"
    exit
fi

ssh_target_destination="${!#}"
unset 'argv[${#argv[@]}-1]'

# Combine the remaining arguments into a string with single space separator
argument_length=$(($#-1))
ssh_jumphosts=${@:1:$argument_length}


# if more than 1 arguments specified
if (( $# > 1 )); then
    ssh_jumphosts="-A -J $ssh_jumphosts"
    echo "jumphost detected"
fi



echo "ssh_target_destination: $ssh_target_destination"
echo "ssh_jumphosts: $ssh_jumphosts"

if [[ $ssh_target_destination != *@* ]]; then
    echo "Error: destination user name is not found. Please specify last argument as USERNAME@DESTINATION_IP"
    exit 1
fi

IFS='@' read -r ansible_ssh_username ansible_ssh_target <<< "$ssh_target_destination"

# Assumption appropriate ssh-key already exists (on the computer which run this ansible script)
# and already set as default (can be configured inside the ~/.ssh/config)
export ANSIBLE_EXTRAVARS="ansible_host=$ansible_ssh_target ansible_user=$ansible_ssh_username"
export ANSIBLE_EXTRAVARS="$ANSIBLE_EXTRAVARS ansible_ssh_common_args=\"$ssh_jumphosts\""

echo "$ANSIBLE_EXTRAVARS"

sudo ansible-playbook ./tasks/benchmark/main.yaml -i ./tasks/benchmark/inventory.txt -e "$ANSIBLE_EXTRAVARS"
