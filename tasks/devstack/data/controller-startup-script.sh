#!/usr/bin/env bash

sudo ip link set  br-ex up
sudo ip route add {{ devstack_floating_ip_range }} dev br-ex