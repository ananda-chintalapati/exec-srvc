#!/bin/bash

sudo apt-get install software-properties-common
sudo apt-add-repository ppa:ansible/ansible -y
sudo apt-get update
sudo apt-get install ansible -y

ansible --version

if [ $? -eq 0 ]; then
    echo "OK"
else
    echo "FAIL"
fi

#ansible-playbook -i inventory main.yml --private-key=/home/ubuntu/centos.pem -vvvv