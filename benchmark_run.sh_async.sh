#!/bin/bash

if [ -z "$ANSIBLE_CONNECTION_FOR_TARGET_HOST" ]; then
  echo "ANSIBLE_CONNECTION_FOR_TARGET_HOST is not set... WIll use ssh as the connection method"
  ANSIBLE_CONNECTION_FOR_TARGET_HOST="ssh"
else
  echo "detected ANSIBLE_CONNECTION_FOR_TARGET_HOST=$ANSIBLE_CONNECTION_FOR_TARGET_HOST"
fi

sudo env RETRY="$RETRY" ANSIBLE_CONNECTION_FOR_TARGET_HOST="$ANSIBLE_CONNECTION_FOR_TARGET_HOST" SUDO_PASS="$SUDO_PASS" nohup ./benchmark_run.sh "$@" 2>&1 > "nohup_benchmark_log.txt" &