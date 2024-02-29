UNDER DEVELOPMENT


1. git clone vgpu unlcoker
   https://github.com/DualCoder/vgpu_unlock

2. Install mdevctl
   https://ubuntu.pkgs.org/20.04/ubuntu-universe-amd64/mdevctl_0.59-1_all.deb.html


3. a
4. a
5. a




resources:
- https://www.youtube.com/watch?v=cPrOoeMxzu0&ab_channel=CraftComputing



##########################################################################



## 0. Pastiin IOMMU aktif dan PCI NVIDIA capable untuk IOMMU
https://documentation.suse.com/soc/9/html/suse-openstack-cloud-crowbar-all/gpu-passthrough.html

Cek juga apakah PCI NVIDIA capable untk SR-IOV pakai `lspci -vvv | nano -` terus find NVIDA, 
terus cari attribute capabilitiesnya (harusnya ada dicantum: ```)

## 1. Matiin Nouveau
https://askubuntu.com/a/951892/1058660

touch /etc/modprobe.d/nouveau-default.conf
isi dengan:
```
blacklist nvidiafb
blacklist nouveau
blacklist nvidia_drm
blacklist nvidia

options nouveau modeset=0
```


## 2. `sudo modprobe -r nouveau`

## 3. make sure noveau not loaded
admin@open2:~$ sudo gpu-manager | grep nouveau
Is nouveau loaded? no
Is nouveau blacklisted? yes

## 4a. Edit compute-node /etc/nova/nova.conf
Tambahkan pada `[pci]` (atau buat baru `[pci]`-nya)
```
passthrough_whitelist = [{ "address": "0000:21:00.0" }]
alias = { "vendor_id":"10de", "product_id":"1eb8", "device_type":"type-PCI", "name":"T4" }
```
Note, untuk versi openstack di bawah Ocata, mungkin beda keyword. Lihat: https://docs.openstack.org/ocata/config-reference/tables/conf-changes/nova.html

Ganti `21:00.0` sesuai output pada `lspci -nn | grep -i nvidia` di paling kirinya
Ganti `10de` dan `1eb8` sesuai output pada `lspci -nn | grep -i nvidia`
Name-nya bebas, tapi konsisten across all nodes.

Contoh di atas itu untuk output `lspci -nn | grep -i nvidia`:
```
21:00.0 3D controller [0302]: NVIDIA Corporation TU104GL [Tesla T4] [10de:1eb8] (rev a1)
23:00.0 3D controller [0302]: NVIDIA Corporation TU104GL [Tesla T4] [10de:1eb8] (rev a1) 
```
(kasus ada 2 GPU nvidia, pilih aja salah satunya yang mau dipake yang mana. Contoh ini pake yang baris pertama)


## 4b. Edit controller-node /etc/nova/nova.conf
Tambahkan pada `[pci]` (atau buat baru `[pci]`-nya)
```
alias = { "vendor_id":"10de", "product_id":"1eb8", "device_type":"type-PCI", "name":"T4" }
```
ini sama kayak `alias` yang di compute-node. Ganti `10de` dan `1eb8`-nya. 


## 5a. Restart compute-node Nova Compute
sudo systemctl restart devstack@n-cpu.service

## 5b. Restart controller-node Nova API
sudo systemctl restart devstack@c-api.service
sudo systemctl restart devstack@c-sch.service


## 6. register new openstack flavor
```
openstack flavor create --ram 2048 --disk 20 --vcpu 1 gpuflavor
openstack flavor set gpuflavor --property "pci_passthrough:alias"="T4:1"
```

## 7. Reboot both controller and compute node
```
sudo reboot`
```

## 7. Create the instance
```
openstack server create --flavor gpuflavor --image Ubuntu2004 --nic net-id=1951cbe2-280d-46c1-a145-eefe11f01f71 --security-group bfd936f3-99b5-4c05-85ff-ca9843ef7c99 --key-name created_by_ansible gpu_real
```


Di adopsi dari:
- https://gist.github.com/claudiok/890ab6dfe76fa45b30081e58038a9215
- https://documentation.suse.com/soc/9/html/suse-openstack-cloud-crowbar-all/gpu-passthrough.html
- https://docs.openstack.org/nova/latest/admin/pci-passthrough.html
