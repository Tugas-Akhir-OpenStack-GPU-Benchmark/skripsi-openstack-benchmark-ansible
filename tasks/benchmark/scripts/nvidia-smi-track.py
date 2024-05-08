#!/usr/bin/python3

import json
import os.path
import shlex
import subprocess
import sys
from xml.etree import cElementTree as ET
from time import sleep
from random import random

PERIOD = 2  # second
MAX_INACTIVE_DURATION = 600  # 600 secs
MAX_INACTIVE_LOOP = MAX_INACTIVE_DURATION / PERIOD


def main(mode, resulting_file_name):
    assert mode in ('START', 'STOP')
    temporary_file = os.path.join(os.path.dirname(resulting_file_name), "." + os.path.basename(resulting_file_name))

    if mode == 'STOP':
        stop(temporary_file, resulting_file_name)
        return
    start(temporary_file, resulting_file_name)
    print("Stopped")


def start(temporary_file, resulting_file_name):
    if os.path.isfile(resulting_file_name):
        os.remove(resulting_file_name)

    # key: process name, value: dict consist of sample count, gpu util sum, gpu memory util sum
    process_to_total_utilization_mapping = {}

    inactive_limit = MAX_INACTIVE_LOOP
    while True:
        result = get_stats()
        inactive_limit -= 1
        if not all_gpu_inactive(result, 10):
            inactive_limit = MAX_INACTIVE_LOOP

        process_to_utilization_mapping = get_process_to_utilization_mapping(result)
        for process, (gpu_util, memory_util) in process_to_utilization_mapping.items():
            if process not in process_to_total_utilization_mapping:
                process_to_total_utilization_mapping[process] = {'gpu-sum': 0, 'gpu-mem-sum': 0, 'count': 0}
            utilization = process_to_total_utilization_mapping[process]
            utilization['gpu-sum'] += gpu_util
            utilization['gpu-mem-sum'] += memory_util
            utilization['count'] += 1
            utilization['gpu-avg'] = utilization['gpu-sum'] / utilization['count']
            utilization['gpu-mem-avg'] = utilization['gpu-mem-sum'] / utilization['count']
        write_to_json_file(temporary_file, process_to_total_utilization_mapping)

        sleep(PERIOD)
        if inactive_limit < 0:
            stop(temporary_file, resulting_file_name)
            return
        if not os.path.isfile(temporary_file):
            return


def get_process_to_utilization_mapping(nvidia_smi_result: dict):
    process_to_utilization_mapping = {}
    for gpu_id, (gpu_util, memory_util, process_list) in nvidia_smi_result.items():
        for process in process_list:
            if process not in process_to_utilization_mapping:
                process_to_utilization_mapping[process] = [0, 0]
            utilization = process_to_utilization_mapping[process]
            utilization[0] = max(utilization[0], gpu_util)
            utilization[1] = max(utilization[1], memory_util)
    return process_to_utilization_mapping


def write_to_json_file(filepath, obj):
    with open(filepath, 'w') as f:
        try:
            json.dump(obj, f)
        except:
            pass


def stop(temporary_file, resulting_file_name):
    for _ in range(5):
        try:
            os.rename(temporary_file, resulting_file_name)
            with open(resulting_file_name, 'r') as f:
                print(f.read())
            return
        except Exception as e:
            print(f"Error when trying to rename file {temporary_file}, {repr(e)}. Retrying again...", file=sys.stderr)
            sleep(2 + random())
    assert False


# gpu_stats ==> dict[str, tuple[int, int, list[str]]]
def all_gpu_inactive(gpu_stats: dict, threshold: int):
    for gpu_id, (gpu_util, memory_util, _) in gpu_stats.items():
        if gpu_util > threshold:
            return False
        if memory_util > threshold:
            return False
    return True


# return ==> dict[str, tuple[int, int, list[str]]]
def get_stats() -> dict:
    nvidia_smi_xml = run_command("nvidia-smi -x -q")
    root = ET.fromstring(nvidia_smi_xml)
    gpus = list(filter(lambda x: x.tag == 'gpu', root))
    ret = {}
    for gpu in gpus:
        id = gpu.attrib['id']
        utlization = list(filter(lambda x: x.tag == 'utilization', gpu))[0]
        gpu_util = int(list(filter(lambda x: x.tag == 'gpu_util', utlization))[0].text.replace('%', ''))
        memory_util = int(list(filter(lambda x: x.tag == 'memory_util', utlization))[0].text.replace('%', ''))

        processes_eltree = list(filter(lambda x: x.tag == 'processes', gpu))[0]
        processes_list = get_processes(processes_eltree)
        ret[id] = (gpu_util, memory_util, processes_list)
    return ret


# return ==> list[str]
def get_processes(processes_xml_element) -> list:
    ret = []
    for process in processes_xml_element:
        process_name = list(filter(lambda x: x.tag == 'process_name', process))[0].text
        ret.append(process_name)
    return ret





def run_command(command, is_json=False, allow_error=False):
    assert "'" not in command
    command = shlex.split(command)
    # command = shlex.split(f"bash -c '{command}'")
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, stderr = proc.communicate()
    if allow_error and len(stderr) > 0:
        return Error(stderr)
    elif len(stderr) > 0:
        raise Exception(stderr.decode('utf-8'))

    if isinstance(output, bytes):
        output = output.decode('utf-8')
    output = output.split("\n")
    lines = []
    for line in output:
        lines.append(line)
    ret = "\n".join(lines)
    if is_json:
        try:
            ret = json.loads(ret)
        except Exception as e:
            print(ret)
            raise e
    return ret


class Error:
    def __init__(self, msg):
        if isinstance(msg, bytes):
            msg = msg.decode('utf-8')
        self.msg = msg


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])