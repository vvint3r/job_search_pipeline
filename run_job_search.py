import subprocess
import logging
import sys
import os
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def run_job_search_pipeline(job_title):
    """Run the job search pipeline with the given job title."""
    try:
        logging.info("Starting job search pipeline...")
        logging.info(f"Job title: {job_title}")
        
        # Set up directories
        logging.info("Setting up directories...")
        os.makedirs("job_search_results", exist_ok=True)
        
        # Verify scripts exist
        scripts = ["./job_search.py", "./job_url_details.py"]
        for script in scripts:
            if os.path.exists(script):
                logging.info(f"Found script: {script}")
            else:
                raise FileNotFoundError(f"Script not found: {script}")
        
        # PIPELINE 1: Run job search
        logging.info("PIPELINE 1: Running the JOB SEARCH pipeline:")
        cmd = ['python3', './job_search.py', '--job_title', job_title]
        logging.info(f"Running ./job_search.py with arguments: {cmd}")
        
        logging.info("About to execute subprocess...")
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )

        # Read output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                logging.info(f"Script output: {output.strip()}")

        # Check for errors
        if process.returncode != 0:
            error_output = process.stderr.read()
            logging.error(f"Error executing ./job_search.py: {error_output}")
            logging.error(f"Error output: {error_output}")
            raise subprocess.CalledProcessError(process.returncode, cmd)
            
        logging.info("Job search pipeline completed successfully")
        
    except Exception as e:
        logging.error(f"Main script error: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Run job search pipeline')
    parser.add_argument('--job_title', required=True, help='Job title to search for')
    args = parser.parse_args()
    
    run_job_search_pipeline(args.job_title)

if __name__ == "__main__":
    main() 