#!/bin/bash

sudo env SUDO_PASS="$SUDO_PASS" nohup ./benchmark_run.sh "$@" 2>&1 > "nohup_log $(date '+%F %H:%M:%S').txt" &