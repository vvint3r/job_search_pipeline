import logging
import subprocess
import os
import sys
from datetime import datetime
import argparse
from job_text_analysis.unique_terms import generate_unique_terms_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def run_text_cleaning(job_title, input_file, python_interpreter):
    """Run the text cleaning process for a specific job title."""
    try:
        logging.info(f"Starting text cleaning for job title: {job_title}")
        
        # Run the text cleaning script with input file
        cmd = [
            python_interpreter,  # Use the specified Python interpreter
            './job_text_analysis/text_preproc/text_cleaning.py', 
            job_title,
            '--input-file',
            input_file
        ]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            logging.error(f"Text cleaning failed with output: {result.stdout}\nError: {result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, cmd)
        else:
            logging.info("Text cleaning completed successfully")
            
    except Exception as e:
        logging.error(f"Error in text cleaning: {e}")
        raise

def run_keyword_extraction(input_file, model_type, python_interpreter):
    """Run the keyword extraction process for a specific job details file."""
    try:
        logging.info(f"Starting keyword extraction for file: {input_file}")
        
        cmd = [
            python_interpreter,  # Use the specified Python interpreter
            './job_text_analysis/text_insights_models/key_terms/keyword_extraction.py',
            input_file,
            '--model',
            model_type
        ]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            logging.error(f"Keyword extraction failed with output: {result.stdout}\nError: {result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, cmd)
        else:
            logging.info("Keyword extraction completed successfully")
            
    except Exception as e:
        logging.error(f"Error in keyword extraction: {e}")
        raise

def main():
    """Main function to run job analysis pipeline."""
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--model', choices=['keybert', 'yake', 'spacy'])
        parser.add_argument('--job-title', help='Job title to analyze')
        parser.add_argument('--input-file', help='Path to job details CSV file')
        parser.add_argument('--python-interpreter', help='Path to the Python interpreter to use')
        args = parser.parse_args()

        # Prompt for missing arguments
        if not args.job_title:
            args.job_title = input("Enter the job title to analyze: ").strip()
        if not args.input_file:
            args.input_file = input("Enter the path to the job details CSV file: ").strip()
        if not args.python_interpreter:
            args.python_interpreter = input("Enter the path to the Python interpreter to use: ").strip()
        if not args.model:
            args.model = input("Enter the keyword extraction model (keybert, yake, spacy): ").strip()

        # Step 1: Run text cleaning
        run_text_cleaning(args.job_title, args.input_file, args.python_interpreter)
        
        # Step 2: Run keyword extraction
        run_keyword_extraction(args.input_file, args.model, args.python_interpreter)
        
        # Step 3: Generate unique terms report
        nostop_file = args.input_file.replace('.csv', '_nostop.csv')
        generate_unique_terms_report(nostop_file)
        
        logging.info("Job analysis pipeline completed successfully")
        
    except Exception as e:
        logging.error(f"Error in analysis pipeline: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
