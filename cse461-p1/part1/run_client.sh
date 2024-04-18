#!/bin/sh

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <server_name> <port>"
    exit 1
fi

dname=$(dirname ${BASH_SOURCE[0]})
SERVER_NAME=$1
PORT=$2

python3 $dname/client.py $SERVER_NAME $PORT