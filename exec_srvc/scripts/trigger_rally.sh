#!/bin/bash
host=$1
username=$2
passwd=$3
action=$4
rallycmd=$5

cmd=``
if [ $host == 'localhost' ]; then
    cmd="ssh $host"
else
    cmd="sshpass -p $passwd ssh -o StrictHostKeyChecking=no $username@$host"
fi

`$cmd` <<EOF
    `$rallycmd`
EOF
