#!/bin/bash

echo "Verifying environment variables"

if [ -z $OS_AUTH_URL ]; then
   echo "Environment variables are not set properly"
   exit 1
fi

deply=`sudo -E rally deployment list | grep rally-auto`
if [ ! -z "$deply" ]; then
	echo "Cleaning up existing deployments"
	sudo -E rally deployment destroy rally-auto
fi
echo "Creating deployment for testing"

uuid=`sudo -E rally deployment create --fromenv --name=rally-auto | grep 'Using deployment' | awk -F": " '{print $2}'`

echo "Rally deployment created with uuid $uuid"

echo "Installing Tempest"

sudo -E rally verify install --deployment $uuid
if [ $? -eq 0 ]; then
	echo "Tempest is ready"
else
	echo "Tempest installation failed"
fi

echo "Executing tempest test cases as requested"
now=$(date +"%Y-%m-%dT%H-%M-%s")
rally_out="rally_$now.out"
cmd="sudo -E rally verify start --deployment $uuid"
if [ $OS_TEST_TARGET == "Component" ]; then
   cmd=$cmd" --set $OS_TEST_TARGET_VALUE"
elif [ $OS_TEST_TARGET == "TestSuite" ]; then
   cmd=$cmd" --regex $OS_TEST_TARGET_VALUE"
fi

$cmd > $rally_out 2>&1
echo "verification output"
sudo -E cat $rally_out | grep -m 1 Verification
echo `sudo -E cat $rally_out | grep -m 1 Verification`
verify_uuid=`sudo -E cat $rally_out | grep -m 1 Verification | awk -F" " '{print $8}'`
echo "Tempest execution completed with ID $verify_uuid"

echo "Capturing data into JSON file"
rally_res=$rally_out
if [ ! -d "/tmp/rally-executions" ]; then
	mkdir /tmp/rally-executions
fi
echo "Rally execution directory verified"
rally_verify="sudo -E rally verify results --json"
if [ ! -z $verify_uuid ]; then
   rally_verify=$rally_verify" --uuid $verify_uuid"
fi
$rally_verify --output-file /tmp/rally-executions/$rally_res
echo "Rally results verification complete"
sudo -E cp /tmp/rally-executions/$rally_res /tmp/rally-executions/output.json

echo "Results are ready at /tmp/rally-executions/$rally_res"

if [ ! -f "/tmp/rally-executions/$rally_res" ]; then
	echo "Results are not captured"
    exit 1
fi

influx_str="rally_execution_stats,"
influx_str=$influx_str"os_version=$OS_RELEASE,"
influx_str=$influx_str"test_name=$OS_TEST_NAME,"
influx_str=$influx_str"test_goal=$OS_TEST_TARGET,"
influx_str=$influx_str"test_target=$OS_TEST_TARGET_VALUE "
influx_str=$influx_str`python -tt <<END
import json
idbClause = ""
with open('/tmp/rally-executions/output.json') as data_file:
  data = json.load(data_file)
  idbClause = idbClause + "tests=" + str(data.get("tests"))
  idbClause = idbClause + ","
  idbClause = idbClause + "time=" + str(data.get("time"))
  idbClause = idbClause + ","
  idbClause = idbClause + "success=" + str(data.get("success"))
  idbClause = idbClause + ","
  idbClause = idbClause + "failures=" + str(data.get("failures"))
  idbClause = idbClause + ","
  idbClause = idbClause + "skipped=" + str(data.get("skipped"))
  idbClause = idbClause + ","
  idbClause = idbClause + "expected_failures=" + str(data.get("expected_failures"))
  idbClause = idbClause + ","
  idbClause = idbClause + "unexpected_success=" + str(data.get("unexpected_success"))
print idbClause
END`

echo "influxDB String : $influx_str"
echo "curl -iv -X POST $INFLUX_URL/write?db=$INFLUX_DB --data-binary '"$influx_str"'"
curl -iv -X POST $INFLUX_URL/write?db=$INFLUX_DB --data-binary ''"$influx_str"''

exit 0
