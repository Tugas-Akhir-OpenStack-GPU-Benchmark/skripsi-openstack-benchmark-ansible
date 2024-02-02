#!/usr/bin/python3

import configparser
import sys

def update_config_file(config_file_path, db_password, keystone_host):
    config = configparser.ConfigParser(allow_no_value=True, comment_prefixes="#")

    # Read the existing configuration file
    config.read(config_file_path)

    section_name_db = 'database'
    if section_name_db not in config:
        config.add_section(section_name_db)
    config.set(section_name_db, 'connection', f'mysql+pymysql://keystone:{db_password}@{keystone_host}/keystone')

    section_name_token = 'token'
    if section_name_token not in config:
        config.add_section(section_name_token)
    config.set(section_name_token, 'provider', 'fernet')

    with open(config_file_path, 'w') as configfile:
        config.write(configfile)

if __name__ == "__main__":
    config_file_path = '/etc/keystone/keystone.conf'

    update_config_file(config_file_path, sys.argv[1], sys.argv[2])
    print(f"Configuration file '{config_file_path}' updated successfully.")
