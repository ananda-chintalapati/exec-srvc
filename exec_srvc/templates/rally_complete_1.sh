#!/bin/bash

echo "Setting environment variables"

export OS_PROJECT_DOMAIN_NAME=default
export OS_USER_DOMAIN_NAME=default
export OS_PROJECT_NAME={{ project }}
export OS_USERNAME={{ user }}
export OS_PASSWORD={{ passwd }}
export OS_AUTH_URL={{ auth_url }}
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2

echo "Creating deployment for testing"

uuid=`sudo -E rally deployment create --fromenv --name=rally-auto | grep 'Using deployment' | awk -F": " '{print $2}'`

echo "Rally deployment created with uuid $uuid"

echo "Installing Tempest"

sudo -E rally verify install --deployment $uuid
sleep 3m
echo "Tempest is ready"

echo "Executing tempest test cases as requested"
rally_out=rally_`$date`.out
sudo -E {{ rally_cmd }} > $rally_out 2>&1
verify_uuid=`sudo -E cat $rally_out | grep Verification | awk -F" " '{print $8}'`
echo "Tempest execution completed with ID $verify_uuid"

echo "Capturing data into JSON file"
rally_res=$rally_out+'.res'
sudo -E rally verify results --json --uuid $verify_uuid --output-file /tmp/rally-executions/$rally_res
echo "Results are ready at /tmp/rally-executions/$rally_res"

