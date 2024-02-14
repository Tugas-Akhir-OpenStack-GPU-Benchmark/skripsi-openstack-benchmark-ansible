#!/usr/bin/python3
import json
import sys
import ipaddress


def main():
    if len(sys.argv) < 3:
        print("Need at least 2 arguments")
        exit(1)
    cidr = ipaddress.IPv4Interface(sys.argv[1])
    netmask = cidr.netmask

    addition = list(map(int, sys.argv[2:]))
    length = len(addition)
    for i in range(len(addition)):
        addition[i] *= 256**(length - i - 1)

    resulting_ip = cidr.ip + sum(addition)
    resulting_cidr = ipaddress.IPv4Interface(f"{resulting_ip}/{netmask}")
    print(json.dumps({
        'result': resulting_cidr.with_prefixlen,
        'resulting_ip': resulting_ip.__str__(),
        'different_subnet': cidr.network != resulting_cidr.network,
        'network': resulting_cidr.network.with_prefixlen,
    }))




if __name__ == "__main__":
    main()
