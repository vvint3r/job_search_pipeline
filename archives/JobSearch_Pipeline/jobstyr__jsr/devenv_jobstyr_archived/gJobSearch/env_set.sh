#!/bin/bash

# ./run_model.sh rake  # To run RAKE
# ./run_model.sh tfidf  # To run TF-IDF

if [ "$1" == "rake" ]; then
    echo "Activating environment for RAKE..."
    source rake_env/bin/activate
    python rake_script.py
    deactivate
elif [ "$1" == "tfidf" ]; then
    echo "Activating environment for TF-IDF..."
    source tfidf_env/bin/activate
    python tfidf_script.py
    deactivate
else
    echo "Invalid argument. Use 'rake' or 'tfidf'."
    exit 1
fi