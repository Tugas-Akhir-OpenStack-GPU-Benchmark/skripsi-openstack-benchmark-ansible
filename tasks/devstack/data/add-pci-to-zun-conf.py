#!/usr/bin/python3
import os.path
import sys

from configupdater import ConfigUpdater


class Main:
    def __init__(self, vendor_id, product_id, device_type, alias_name, filename):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.device_type = device_type
        assert self.device_type in ('type-PF', 'type-VF', 'type-PCI'), "device_type should be either type-PF, type-VF, or type-PCI"
        self.alias_name = alias_name
        self.filename = filename

        self.updater = ConfigUpdater()
        self.changes = {}

    def make_sure_file_is_ended_with_newline(self):
        assert os.path.isfile(self.filename), f"{self.filename} does not exist"
        with open(self.filename) as f:
            last_char = f.read()[-1]
            if last_char == "\n":
                return
        with open(self.filename, "a") as f:
            f.write("\n\n")

    def run(self, compute_node):
        self.make_sure_file_is_ended_with_newline()
        self.updater.read(self.filename)
        if compute_node:
            self.make_changes_compute_node()
        else:
            self.make_changes_controller_node()

        # backup
        if len(self.changes) == 0:
            return
        print("modified")
        with open(get_backup_file_name(self.filename), 'w') as f:
            self.updater.write(f)
        self.apply_changes(self.updater)
        self.updater.update_file()

    def add_new_change(self, section, key, value):
        if section not in self.changes:
            self.changes[section] = {}
        self.changes[section][key] = value

    def make_changes_controller_node(self):
        self.make_changes_for_alias()
        self.make_changes_for_enabled_filters()
        self.make_changes_for_available_filters()

    def make_changes_compute_node(self):
        self.make_changes_for_alias()
        self.make_changes_for_passthrough_whitelist()
        self.make_changes_for_device_spec()
        self.make_changes_for_enabled_filters()
        self.make_changes_for_available_filters()


    def make_changes_for_alias(self):
        section = 'pci'
        key = 'alias'
        value = (f"{{ \"vendor_id\":\"{self.vendor_id}\", \"product_id\":\"{self.product_id}\", "
                        f"\"device_type\":\"{self.device_type}\", \"name\":\"{self.alias_name}\" }}")
        if (section in self.updater
            and key in self.updater[section]
            and self.updater[section][key].value == value
        ):
            return
        self.add_new_change(section, key, value)

    def make_changes_for_passthrough_whitelist(self):
        section = 'pci'
        key = 'passthrough_whitelist'
        value = f"{{ \"vendor_id\":\"{self.vendor_id}\", \"product_id\":\"{self.product_id}\"}}"

        if (section in self.updater
                and key in self.updater[section]
                and self.updater[section][key].value == value):
            return
        self.add_new_change(section, key, value)

    def make_changes_for_device_spec(self):
        section = 'pci'
        key = 'device_spec'
        value = f"{{ \"vendor_id\":\"{self.vendor_id}\", \"product_id\":\"{self.product_id}\"}}"

        if (section in self.updater
                and key in self.updater[section]
                and self.updater[section][key].value == value):
            return
        self.add_new_change(section, key, value)

    def make_changes_for_available_filters(self):
        section = 'filter_scheduler'
        key = 'available_filters'
        value = f"zun.scheduler.filters.all_filters"

        if (section in self.updater
                and key in self.updater[section]
                and self.updater[section][key].value == value):
            return
        self.add_new_change(section, key, value)

    def make_changes_for_enabled_filters(self):
        section = 'filter_scheduler'
        key = 'enabled_filters'
        value_to_be_added = 'PciPassthroughFilter'
        current_value = []

        if section in self.updater and key in self.updater[section]:
            current_value = self.updater[section][key].value.split(",")
        if value_to_be_added in current_value:
            return
        current_value.append(value_to_be_added)
        self.add_new_change(section, key, ",".join(current_value))

    def apply_changes(self, config_updater: ConfigUpdater):
        for section in self.changes:
            if section not in config_updater:
                config_updater.add_section(section)
            for key, value in self.changes[section].items():
                config_updater[section][key] = value



def get_backup_file_name(filename):
    filename, ext = os.path.splitext(filename)
    i = 0
    while True:
        path = f"{filename}{ext}.bak ({i})"
        if not os.path.isfile(path) and not os.path.isdir(path):
            return path
        i += 1


COMPUTE = "compute"
CONTROLLER = "controller"


if __name__ == "__main__":
    vendor_id = sys.argv[1]
    product_id = sys.argv[2]
    device_type = sys.argv[3]
    alias_name = sys.argv[4]
    target_file = sys.argv[5]
    node_type = sys.argv[6].lower()
    assert node_type in (COMPUTE, CONTROLLER)
    Main(vendor_id, product_id, device_type, alias_name, target_file).run(node_type == COMPUTE)
