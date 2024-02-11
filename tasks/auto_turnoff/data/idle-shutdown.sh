#!/bin/bash
# Add to instance metadata with `gcloud compute instances add-metadata \
#   instance-name --metadata-from-file startup-script=idle-shutdown.sh` and reboot
# NOTE: requires `bc`, eg, sudo apt-get install bc
# Modified from https://stackoverflow.com/questions/30556920/how-can-i-automatically-kill-idle-gce-instances-based-on-cpu-usage
threshold=0.12

printf "Hello, starting up at $(date) \n" >> log.txt

count=0
wait_minutes=50
while true
do

  load=$(uptime | sed -e 's/.*load average: //g' | awk '{ print $1 }') # 1-minute average load
  load="${load//,}" # remove trailing comma
  res=$(echo $load'<'$threshold | bc -l)
  if (( $res ))
  then
    ((count+=1))
  else
    ((count-=5))
  fi

  if [ "$count" -lt "0" ]
  then
    count=0
  fi

  echo "Idle minutes count = $count. Load = $load" >> log.txt

  if (( count>wait_minutes ))
  then
    echo Shutting down >> log.txt
    echo Shutting down
    printf "Queue for shutting down at $(date) \n" >> log.txt
    # wait a little bit more before actually pulling the plug

    sudo wall "System is scheduled to shutdown for about 3 minutes later from now"

    sleep 170
    printf "Hello, shutting down at $(date) \n" >> log.txt
    sudo wall "shutting down..."
    sleep 10
    sudo poweroff &
  fi

  sleep 60
done

printf "Hello, shutting down at $(date) \n" >> log.txt