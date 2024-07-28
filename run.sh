#!/bin/bash

# Define the path to the Python script and the log file
SCRIPT_PATH="ML-A100/team/mm/zhangge/Vl-Bench/src/main.py"
LOG_PATH="ML-A100/team/mm/zhangge/Vl-Bench/output.log"

# Ensure the script has executable permissions
chmod +x $SCRIPT_PATH

# Run the script using nohup to ensure it runs in the background
nohup python3 $SCRIPT_PATH > $LOG_PATH 2>&1 &