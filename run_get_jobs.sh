#!/bin/bash

# Activate virtual environment
source env/bin/activate

# Set PYTHONPATH to include the current directory
export PYTHONPATH=$(pwd)

# Run the main pipeline script
echo "Running Job Search Pipeline..."
python3 main_get_jobs.py