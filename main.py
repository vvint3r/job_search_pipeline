import subprocess
import logging
import sys
import os
from datetime import datetime
import glob

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def run_job_search_pipeline(job_title):
    """Run the complete job search pipeline."""
    try:
        logging.info("Starting job search pipeline...")
        
        # PIPELINE 1: Run job search
        logging.info("PIPELINE 1: Running the JOB SEARCH pipeline:")
        cmd = ['python3', './job_search.py', job_title]
        
        result = subprocess.run(
            cmd,
            stdin=None,
            stdout=None,
            stderr=None,
        )
        
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd)
            
        # Get the most recent CSV file
        csv_files = glob.glob('job_search_results/linkedin_jobs_*.csv')
        if not csv_files:
            raise FileNotFoundError("No CSV files found from Pipeline 1")
            
        latest_csv = max(csv_files, key=os.path.getctime)
        logging.info(f"Found latest CSV file: {latest_csv}")
        
        # PIPELINE 2: Run URL details collection
        logging.info("PIPELINE 2: Running the JOB URL DETAILS pipeline:")
        cmd = ['python3', './job_url_details.py', job_title, latest_csv]
        
        result = subprocess.run(
            cmd,
            stdin=None,
            stdout=None,
            stderr=None,
        )
        
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd)
            
        logging.info("Both pipelines completed successfully")
        
    except Exception as e:
        logging.error(f"Pipeline error: {e}")
        raise

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py 'job title'")
        sys.exit(1)
    
    job_title = sys.argv[1]
    try:
        run_job_search_pipeline(job_title)
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
