#!/usr/bin/python3

# TODO
# NOT USED YET


import configparser
import json
import sys

class Main:
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        config = configparser.ConfigParser(allow_no_value=True, comment_prefixes="#")

        # Read the existing configuration file
        config.read(config_file_path)
        with open(f"{config_file_path}-backup", 'w') as configfile:
            config.write(configfile)
        self.config = config

    def run(self):
        self.set_property('pci', 'device_spec', json.dumps({
            "address": "0000:21:00.0"  # todo
        }))

        self.set_property('pci', 'alias', json.dumps({
            "vendor_id": "8086", "product_id": "154d", "device_type": "type-PF", "name": "a1"
        }))

    def assert_section_exists(self, section_name):
        if section_name not in self.config:
            self.config.add_section(section_name)

    def get_property(self, section_name, key):
        self.assert_section_exists(section_name)
        return self.config.get(section_name, key)

    def set_property(self, section_name, key, value):
        self.assert_section_exists(section_name)
        return self.config.set(section_name, key, value)


if __name__ == "__main__":
    config_file_path = '/etc/keystone/keystone.conf'

    update_config_file(config_file_path, sys.argv[1], sys.argv[2])
    print(f"Configuration file '{config_file_path}' updated successfully.")
