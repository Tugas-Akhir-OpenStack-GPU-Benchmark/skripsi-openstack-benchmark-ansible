# run with sudo

ansible-galaxy install nvidia.nvidia_driver,2.3.0
#ansible-galaxy role install jedimt.cuda,1.0.2


#sudo ansible-playbook  main.yaml -i inventory.txt
#sudo ansible-playbook  main.yaml -i inventory.txt --start-at-task="chmod prime-run"
sudo ansible-playbook  main.yaml -i inventory.txt --start-at-task="install libfreeimage"
#