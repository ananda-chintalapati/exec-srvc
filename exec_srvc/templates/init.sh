#!/bin/bash

ROLE_PATH=/opt/css_deploy/roles
sudo git clone {{ repo_url }} /opt
cat > $ROLE_PATH/requirements.yml <<EOF
{{ ansible_requirement }}
EOF

if [ -d $ROLE_PATH ]; then
	exit 1
fi

export ANSIBLE_ROLE_PATH=$ROLE_PATH

sudo apt-get update
sudo apt-get install ansible -y

ansible-galaxy install -r $ROLE_PATH/requirements.yml