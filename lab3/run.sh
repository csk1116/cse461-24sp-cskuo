#!/bin/bash

# Check if a port number is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <port>"
  exit 1
fi

# Get the port number from the first argument
PORT=$1

# Run the Python proxy server
python3 test.py $PORT