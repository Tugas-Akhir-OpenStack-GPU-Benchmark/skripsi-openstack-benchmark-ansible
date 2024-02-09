#!/bin/python3
import subprocess
import sys

services = {
    "nova-cpu": "n-cpu.service",
    "cinder-api": "c-api.service",
    "cinder-scheduler": "c-sch.service",
    "cinder-volume": "c-vol.service",
    "dstat": "dstat.service",
    "etcd": "etcd.service",
    "glance-api": "g-api.service",
    "keystone": "keystone.service",
    "nova-api-meta": "n-api-meta.service",
    "nova-api": "n-api.service",
    "nova-cond": "n-cond-cell1.service",
    "nova-cpu": "n-cpu.service",
    "nova-schedule": "n-sch.service",
    "nova-super-cond": "n-super-cond.service",
    "placement": "placement-api.service",
    "neutron-metadata": "q-ovn-metadata-agent",
    "neutron": "q-svc",
}
# systemctl --type=service | grep devstack


def main():
    if len(sys.argv) <= 1:
        print("Please provide service-type as the first argument")
        return exit(1)

    if len(sys.argv) <= 2:
        last_n_minutes = 10
    else:
        last_n_minutes = sys.argv[2]

    if len(sys.argv) <= 3:
        display_mode = "separated"
    else:
        display_mode = sys.argv[3]
    assert display_mode in ("separated", "combined")

    target_system_type = sys.argv[1]
    if target_system_type == "all":
        target_system_type = ""  # empty string is substring for ALL strings

    target_services = []
    for key, systemctl_name in services.items():
        if target_system_type in key:
            target_services.append(f"devstack@{systemctl_name}")
    print_log(target_services, last_n_minutes, display_mode)


def print_log(target_services: list[str], last_n_minutes=10, display_mode="separated"):
    if display_mode == "separated":
        return print_log_separated(target_services, last_n_minutes)
    if display_mode == "combined":
        return print_log_combined(target_services, last_n_minutes)
    raise ValueError(f"Invalid display mode: {display_mode}")


def print_log_separated(target_services: list[str], last_n_minutes):
    for target_service in target_services:
        print()
        print()
        print(f"==================== LOG FOR {target_service}, last {last_n_minutes} minutes ====================")
        print()
        print(get_log_combined([target_service], last_n_minutes=last_n_minutes))


def print_log_combined(target_services: list[str], last_n_minutes):
    print(get_log_combined(target_services, last_n_minutes=last_n_minutes))


def get_log_combined(systemctl_names: list[str], last_n_minutes=10):
    systemctl_names = systemctl_names[:]
    for i in range(len(systemctl_names)-1, -1, -1):  # reverse from N-1, N-2, ..., 0
        systemctl_names.insert(i, "-u")

    command = ["journalctl"] + systemctl_names + ["--since", f"{last_n_minutes}min ago"]
    return subprocess.check_output(command).decode('utf-8')



if __name__ == "__main__":
    main()
