#!/bin/bash

sudo nohup ./benchmark_run.sh > "nohup_log $(date '+%F %H:%M:%S').txt" 2>&1 &