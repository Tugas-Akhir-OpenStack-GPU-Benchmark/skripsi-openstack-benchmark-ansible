#!/bin/bash

export ANSIBLE_SSH_RETRIES=8

if [ $# -lt 2 ]
then
    echo "Need at least 2 arguments: CONTROLLER_SSH_IP COMPUTE_SSH_IP"
    exit
fi

ssh_target_compute_node="${!#}"

second_last=$(($#-2))
ssh_target_controller_node="${@:(-2):1}"


# Combine the remaining arguments into a string with single space separator
argument_length=$(($#-2))
ssh_jumphosts=${@:1:$argument_length}

echo "ssh_target_controller_node: $ssh_target_controller_node"
echo "ssh_target_compute_node: $ssh_target_compute_node"
echo "num of jumphosts: $argument_length"


# if more than 1 arguments specified
if (( $argument_length > 0 )); then
    ssh_jumphosts="-o ConnectTimeout=250 -A -J $ssh_jumphosts"
    echo "jumphost detected"
fi

echo "ssh args: $ssh_jumphosts"


if [[ $ssh_target_controller_node != *@* ]]; then
    ssh_target_controller_node_username=immanuel01
    ssh_target_controller_node_ip="$ssh_target_controller_node"
else
    IFS='@' read -r ssh_target_controller_node_username ssh_target_controller_node_ip <<< "$ssh_target_controller_node";
fi
if [[ $ssh_target_compute_node != *@* ]]; then
    ssh_target_compute_node_username=immanuel01
    ssh_target_compute_node_ip="$ssh_target_compute_node"
else
    IFS='@' read -r ssh_target_compute_node_username ssh_target_compute_node_ip <<< "$ssh_target_compute_node";
fi




# Assumption appropriate ssh-key already exists (on the computer which run this ansible script)
# and already set as default (can be configured inside the ~/.ssh/config)

export ANSIBLE_EXTRAVARS=""
#export ANSIBLE_EXTRAVARS="ansible_user=stack"
export ANSIBLE_EXTRAVARS="$ANSIBLE_EXTRAVARS ansible_ssh_common_args=\"$ssh_jumphosts\""
export ANSIBLE_EXTRAVARS="$ANSIBLE_EXTRAVARS CONTROLLER_SSH_USER=$ssh_target_controller_node_username"
export ANSIBLE_EXTRAVARS="$ANSIBLE_EXTRAVARS COMPUTE_SSH_USER=$ssh_target_compute_node_username"
export ANSIBLE_EXTRAVARS="$ANSIBLE_EXTRAVARS CONTROLLER_SSH_IP=$ssh_target_controller_node_ip COMPUTE_SSH_IP=$ssh_target_compute_node_ip"

if [ -n "$SUDO_PASS" ]; then
  ANSIBLE_EXTRAVARS="$ANSIBLE_EXTRAVARS ansible_sudo_pass=\"$SUDO_PASS\""
  echo "detected SUDO_PASS. Will use it for sudo authentication"
else
  echo "var SUDO_PASS is not set. Will assume target hosts don't need password to run sudo commands..."
fi


export ANSIBLE_CACHE_PLUGIN=jsonfile

sudo ansible-playbook ./tasks/devstack/main.yaml -i ./tasks/devstack/inventory.yml -e "$ANSIBLE_EXTRAVARS"
