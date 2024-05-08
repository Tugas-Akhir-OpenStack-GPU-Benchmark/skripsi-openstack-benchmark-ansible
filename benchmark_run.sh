#!/bin/bash
# run with sudo

if [ ! -f ./not-first-time-run-benchmark.txt ]; then
    sudo apt update
    sudo apt install ansible -y
    ansible-galaxy install nvidia.nvidia_driver,v2.3.0
    touch not-first-time-run-benchmark.txt
fi




if [ -z "$1" ]; then
    echo "Please provide SSH host (IP address) of the controller-instance as the first argument"
    exit
fi

if [ -z "$ANSIBLE_CONNECTION_FOR_TARGET_HOST" ]; then
  echo "ANSIBLE_CONNECTION_FOR_TARGET_HOST is not set... WIll use ssh as the connection method"
  ANSIBLE_CONNECTION_FOR_TARGET_HOST="ssh"
else
  echo "detected ANSIBLE_CONNECTION_FOR_TARGET_HOST=$ANSIBLE_CONNECTION_FOR_TARGET_HOST"
fi



ansible_ssh_extra_args="-o StrictHostKeyChecking=no"
ansible_ssh_common_args="-o StrictHostKeyChecking=no -o ControlMaster=auto -o ControlPersist=120"

export ANSIBLE_HOST_KEY_CHECKING=False
export ANSIBLE_EXTRAVARS="ansible_host=$1 ansible_ssh_private_key_file=~/.ssh/gcp"
export ANSIBLE_EXTRAVARS="$ANSIBLE_EXTRAVARS ansible_ssh_common_args=\"$ansible_ssh_common_args\""
export ANSIBLE_EXTRAVARS="$ANSIBLE_EXTRAVARS ansible_ssh_extra_args=\"$ansible_ssh_extra_args\""
export ANSIBLE_EXTRAVARS="$ANSIBLE_EXTRAVARS ANSIBLE_CONNECTION_FOR_TARGET_HOST=\"$ANSIBLE_CONNECTION_FOR_TARGET_HOST\""

if [ -n "$SUDO_PASS" ]; then
  ANSIBLE_EXTRAVARS="$ANSIBLE_EXTRAVARS ansible_sudo_pass=\"$SUDO_PASS\""
  echo "detected SUDO_PASS. Will use it for sudo authentication"
else
  echo "var SUDO_PASS is not set. Will assume target hosts don't need password to run sudo commands..."
fi

if [ "$RETRY" = "1" ]; then
  ANSIBLE_EXTRAVARS="$ANSIBLE_EXTRAVARS retry_files_enabled=True retry_files_save_path=./ansible-retry-temp.retry"
  echo "detected RETRY. Will store checkpoints and will  continue latest failing task if detected"
else
  rm -f ./ansible-retry-temp.retry
  echo "RETRY not detected... Will not retry on failing ansible task"
fi

sudo ansible-playbook ./tasks/benchmark/main.yaml -i ./tasks/benchmark/inventory.yml -e "$ANSIBLE_EXTRAVARS"  --verbose
#sudo ansible-playbook ./tasks/benchmark/main.yaml -i ./tasks/benchmark/inventory.yml -e "$ANSIBLE_EXTRAVARS" --verbose --start-at-task="Restart GDM service"
