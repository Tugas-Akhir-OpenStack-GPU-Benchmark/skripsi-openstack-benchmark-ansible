#!/usr/bin/python3
import sys
from pprint import pprint
import netifaces
import psutil


def main(assert_nic_exists: list[str]):
    nic_information = psutil.net_if_addrs()

    nic_information = {
        key: {
            "ipaddr": value[0].address,
            "netmask": value[0].netmask,
            "broadcast": value[0].broadcast,
        }
        for (key, value) in nic_information.items()
        if startswith_any(key, "ens", "eth", "vlan")
    }
    list_of_nic = set(nic_information.keys())
    # assert len(list_of_nic) >= 2, "At least 2 NIC should be installed"

    for nic in assert_nic_exists:
        assert nic in nic_information
    default_gateway = get_default_gateway_linux()
    pprint({
        "gateway": default_gateway,
        "nic": nic_information,
        "interface_1": default_gateway['nic'],
        "interface_2": unpack_set(list_of_nic - {default_gateway['nic']}),
    })


def startswith_any(string: str, *prefixes):
    for prefix in prefixes:
        if string.startswith(prefix):
            return True
    return False


def get_default_gateway_linux():
    default_gateways = netifaces.gateways()['default'].values()
    gateway_ip_address, nic = unpack_set(default_gateways)
    return {
        "ipaddr": gateway_ip_address,
        "nic": nic
    }


def unpack_set(set_: set):
    if len(set_) == 0:
        return None
    sorted_set = sorted(set_)
    return sorted_set[0]


if __name__ == "__main__":
    main(sys.argv[1:])

