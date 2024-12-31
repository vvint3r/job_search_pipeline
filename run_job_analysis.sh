#!/bin/bash

# Set error handling
set -e

# Print start message
echo "Starting Job Analysis Pipeline..."
echo "--------------------------------"
date

# Static job details
JOB_TITLE="SEO Manager"
JOB_FILE="/home/wynt3r/JobSearch/job_search/job_post_details/seo_manager/seo_manager_details_20241230_26185.csv"

# Verify input file exists
if [ ! -f "$JOB_FILE" ]; then
    echo "Error: Job details file not found at $JOB_FILE"
    exit 1
fi

# Function to setup environment if it doesn't exist
setup_env() {
    local env_name=$1
    local setup_cmd=$2
    
    if [ ! -d "$env_name" ]; then
        echo "Creating new $env_name environment..."
        python3 -m venv $env_name
        source $env_name/bin/activate
        # Upgrade pip first
        pip install --upgrade pip
        eval "$setup_cmd"
        deactivate
    else
        echo "Using existing $env_name environment..."
    fi
}

# Setup commands for each environment
KEYBERT_SETUP="pip install -q \
    torch \
    transformers \
    nltk \
    pandas \
    scikit-learn \
    keybert"
YAKE_SETUP="pip install -q yake nltk pandas scikit-learn"
SPACY_SETUP="pip install -q spacy nltk pandas scikit-learn && python -m spacy download en_core_web_sm"

# Select model type
echo "Select keyword extraction model:"
echo "1) KeyBERT"
echo "2) YAKE"
echo "3) SpaCy"
read -p "Enter choice (1-3): " model_choice

# Get absolute path to the selected environment's Python
get_env_python() {
    local env_name=$1
    echo "$(pwd)/$env_name/bin/python3"
}

# Setup and run with appropriate environment
case $model_choice in
    1)
        setup_env "venv_keybert" "$KEYBERT_SETUP"
        ENV_PYTHON=$(get_env_python "venv_keybert")
        export MODEL_TYPE="keybert"
        ;;
    2)
        setup_env "venv_yake" "$YAKE_SETUP"
        ENV_PYTHON=$(get_env_python "venv_yake")
        export MODEL_TYPE="yake"
        ;;
    3)
        setup_env "venv_spacy" "$SPACY_SETUP"
        ENV_PYTHON=$(get_env_python "venv_spacy")
        export MODEL_TYPE="spacy"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

# Print environment info for debugging
echo "Using Python interpreter: $ENV_PYTHON"
$ENV_PYTHON -c "import sys; print(f'Python path: {sys.executable}')"

# Check if pandas is installed in the environment
$ENV_PYTHON -c "import pandas; print(f'Pandas version: {pandas.__version__}')"

# Run the job analysis script with static parameters using the environment's Python
echo "Running job analysis script..."
$ENV_PYTHON main_analyze_jobs.py --model $MODEL_TYPE --job-title "$JOB_TITLE" --input-file "$JOB_FILE" --python-interpreter "$ENV_PYTHON"

# Check the exit status
if [ $? -eq 0 ]; then
    echo "--------------------------------"
    echo "Job analysis completed successfully!"
    date
else
    echo "--------------------------------"
    echo "Error: Job analysis failed!"
    date
    exit 1
fi

# Optional cleanup only if explicitly requested
read -p "Do you want to remove the virtual environments? (y/n) " cleanup
if [ "$cleanup" = "y" ]; then
    read -p "Are you sure? This will delete all model environments. (y/n) " confirm
    if [ "$confirm" = "y" ]; then
        rm -rf venv_*
        echo "Cleaned up virtual environments"
    else
        echo "Keeping virtual environments for future use"
    fi
fi

exit 0