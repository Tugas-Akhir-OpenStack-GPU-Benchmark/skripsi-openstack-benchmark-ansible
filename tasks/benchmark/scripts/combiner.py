#!/usr/bin/python3

import json
import os.path
import sys
from hashlib import md5


def main():
    combine("temp", "cudnn-local-repo-ubuntu2004-8.9.7.29_1.0-1_amd64.deb")


def combine(target_folder, new_file_name):
    if os.path.isfile(new_file_name):
        print(f"File {new_file_name} exists. Skipping...")
        return
    if os.path.isdir(new_file_name):
        throwExceptionAndExit(f"Name {new_file_name} exists as a directory")
    if not os.path.isdir(target_folder):
        throwExceptionAndExit(f"Directory {target_folder} is not found")

    hashes = get_hashes(target_folder)
    with open(new_file_name, "wb") as split_file:
        i = 0
        while True:
            split_filename = os.path.join(target_folder, f"{i}")
            if not os.path.isfile(split_filename):
                break
            with open(split_filename, "rb") as f:
                content = f.read()
                if md5(content).hexdigest() != hashes[i]:
                    split_file.close()
                    os.remove(new_file_name)
                    throwExceptionAndExit(f"Split file {split_filename} has different md5 hash than the expected hash")
                split_file.write(content)
            i += 1


def get_hashes(target_folder):
    hash_filename = os.path.join(target_folder, "hash")
    with open(hash_filename, "r") as hash_fileobj:
        return json.load(hash_fileobj)


def throwExceptionAndExit(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()

