#!/usr/bin/env bash

sudo ip link set  br-ex up
sudo ip route add {{ devstack_floating_ip_range }} dev br-ex
sudo iptables -t nat -A POSTROUTING -o {{ interface_1 }} -j MASQUERADE
#sudo ip li set mtu 1200 dev br-ex
