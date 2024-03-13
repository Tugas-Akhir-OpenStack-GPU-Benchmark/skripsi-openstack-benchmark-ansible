#!/usr/bin/python3
import subprocess
import re
import sys

gpu_pci_vendor_and_product_id = sys.argv[1]
gpu_pci_vendor_and_product_id = gpu_pci_vendor_and_product_id.lower()


def main(text_to_process):
    pci_list = text_to_process.strip().split("\n\n")
    pci_list = list(map(lambda x: extract_informations(x.lower()), pci_list))

    target_gpu_pci_list = list(filter(lambda x: x['vendor-product-id'] == gpu_pci_vendor_and_product_id, pci_list))
    target_iommu_groups = list(map(lambda x: x['iommu-group'], target_gpu_pci_list))
    if len(target_iommu_groups) == 0:
        print(f"ERROR: No PCI bus was found with vendor and product id: {gpu_pci_vendor_and_product_id}.")
        print("Please make sure you provide the correct gpu_pci_vendor_id and gpu_pci_product_id in the ansible script")
        exit(1)

    pci_list_with_such_iommu_group = list(filter(lambda x: x['iommu-group'] in target_iommu_groups, pci_list))

    for i in pci_list_with_such_iommu_group:
        print(i['vendor-product-id'])
        if i['vfio-in-use']:
            continue
        pci_bus = i['pci-bus']
        iommu_group = i['iommu-group']
        print(f"ERROR: PCI bus {pci_bus} has iommu-group {iommu_group} that belongs to the same iommu group as the GPU, "
              + "but this PCI bus is not being used by the vfio-pci")
        exit(1)


vendor_product_id_regex = re.compile('\\[([a-fA-F0-9]+:[a-fA-F0-9]+)\\].*', re.IGNORECASE)
vfio_in_use_regex = re.compile(r'Kernel driver in use.*vfio-pci'.lower(), re.IGNORECASE)
iommu_group_regex = re.compile(r'IOMMU group:\s*(\d+)'.lower(), re.IGNORECASE)
pci_bus_regex = re.compile('[a-fA-F0-9]+:[a-fA-F0-9]+\\.[a-fA-F0-9]+', re.IGNORECASE)


def extract_informations(item):
    if iommu_group_regex.search(item) is None:
        print(item)
    first_line = item.split('\n')[0]

    vendor_product_id = vendor_product_id_regex.search(first_line).group(1)
    assert len(vendor_product_id) > 0, item
    iommu_group = iommu_group_regex.search(item).group(1)
    assert len(iommu_group) > 0, item
    pci_bus = pci_bus_regex.findall(first_line)[0]

    return {
        'raw': item,
        'vendor-product-id': vendor_product_id,
        'vfio-in-use': bool(vfio_in_use_regex.search(item)),
        'iommu-group': iommu_group,
        'pci-bus': pci_bus
    }



def get_iommu_groups(items):
    ret = set()
    for item in items:
        extra_info = extract_informations(item)
        iommu_group = extra_info['iommu-group']
        assert iommu_group != ''
        ret.add(iommu_group )
    return ret



if __name__ == "__main__":
    is_attached_to_tty = sys.stdin.isatty()
    text = sys.stdin.read() if not is_attached_to_tty else None
    if text is None or len(text) == 0:
        text = subprocess.run(["sudo", "lspci", "-nnvvv"], stdout = subprocess.PIPE)
        text = text.stdout
        text = text if not isinstance(text, bytes) else text.decode('utf-8')

    main(text)

