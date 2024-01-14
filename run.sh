# run with sudo

ansible-galaxy install nvidia.nvidia_driver,2.3.0
#sudo ansible-playbook  main.yaml -i inventory.txt
sudo ansible-playbook  main.yaml -i inventory.txt --start-at-task="chmod prime-run"
