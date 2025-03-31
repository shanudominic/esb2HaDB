#!/bin/bash

. /app/venv/bin/activate
cmd="python /app/esb2ha.py"
echo -e "\n${cmd}\n"
eval $cmd

echo -e "\n\n"
