#!/bin/bash

ENV_DIR="/path/to/python_envs"

if [ $# -eq 0 ]; then
    echo "Error: No environment name provided."
    echo "Usage: ./activate_env.sh <env_name>"
    exit 1
fi

ENV_NAME=$1
ACTIVATE_PATH="$ENV_DIR/$ENV_NAME/bin/activate"

if [ -f "$ACTIVATE_PATH" ]; then
    echo "Activating environment: $ENV_NAME"
    source "$ACTIVATE_PATH"
else
    echo "Error: Environment '$ENV_NAME' does not exist in $ENV_DIR."
    exit 1
fi
