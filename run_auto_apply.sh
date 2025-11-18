#!/bin/bash

# Script to run auto-application process
# Usage: ./run_auto_apply.sh [csv_file] [options]

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d "env" ]; then
    source env/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set PYTHONPATH to include the current directory
export PYTHONPATH=$(pwd)

# Default values
CSV_FILE=""
LIMIT=""
DELAY="5.0"
HEADLESS=""
AUTO_SUBMIT=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --csv_file|--csv)
            CSV_FILE="$2"
            shift 2
            ;;
        --limit|-l)
            LIMIT="$2"
            shift 2
            ;;
        --delay|-d)
            DELAY="$2"
            shift 2
            ;;
        --headless)
            HEADLESS="--headless"
            shift
            ;;
        --auto_submit)
            AUTO_SUBMIT="--auto_submit"
            shift
            ;;
        *)
            # If no flag, assume it's the CSV file
            if [ -z "$CSV_FILE" ]; then
                CSV_FILE="$1"
            fi
            shift
            ;;
    esac
done

# Check if CSV file is provided
if [ -z "$CSV_FILE" ]; then
    echo "Error: CSV file is required"
    echo "Usage: $0 --csv_file <path_to_csv> [--limit N] [--delay SECONDS] [--headless] [--auto_submit]"
    echo ""
    echo "Examples:"
    echo "  $0 --csv_file job_search/job_post_details/analytics/job_details/analytics_job_details_20251113_154244.csv"
    echo "  $0 --csv_file jobs.csv --limit 10 --delay 10"
    exit 1
fi

# Check if CSV file exists
if [ ! -f "$CSV_FILE" ]; then
    echo "Error: CSV file not found: $CSV_FILE"
    exit 1
fi

# Build command
CMD="python3 -m job_search.auto_application.main_apply --csv_file \"$CSV_FILE\" --delay_between $DELAY"

if [ ! -z "$LIMIT" ]; then
    CMD="$CMD --limit $LIMIT"
fi

if [ ! -z "$HEADLESS" ]; then
    CMD="$CMD $HEADLESS"
fi

if [ ! -z "$AUTO_SUBMIT" ]; then
    CMD="$CMD $AUTO_SUBMIT"
fi

echo "Running auto-application process..."
echo "CSV File: $CSV_FILE"
echo "Command: $CMD"
echo ""

# Execute the command
eval $CMD

