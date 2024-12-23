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

def find_latest_csv(job_title, search_folder="job_search_results"):
    """Find the latest CSV file for a given job title."""
    try:
        # Clean job title for filename matching
        job_title_clean = job_title.lower().replace(' ', '_')
        
        # Look in the job-specific subdirectory
        job_folder = os.path.join(search_folder, job_title_clean)
        
        # Get all matching CSV files from the subdirectory
        pattern = os.path.join(job_folder, f"{job_title_clean}__*.csv")
        matching_files = glob.glob(pattern)
        
        if not matching_files:
            raise FileNotFoundError(f"No CSV files found for job title: {job_title} in {job_folder}")
            
        # Get the most recent file
        latest_file = max(matching_files, key=os.path.getctime)
        logging.info(f"Found latest CSV file: {latest_file}")
        return latest_file
        
    except Exception as e:
        logging.error(f"Error finding latest CSV: {e}")
        raise

def run_job_search_pipeline(job_title):
    """Run the complete job search pipeline."""
    try:
        logging.info("Starting job search pipeline...")
        
        # PIPELINE 1: Run job search
        logging.info("PIPELINE 1: Running the JOB SEARCH pipeline:")
        cmd = ['python3', './job_extraction/job_search.py', '--job_title', job_title]
        
        result = subprocess.run(
            cmd,
            stdin=None,
            stdout=None,
            stderr=None,
        )
        
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd)
            
        # Find the latest CSV file for this job title
        latest_csv = find_latest_csv(job_title)
        
        # PIPELINE 2: Run URL details collection
        logging.info("PIPELINE 2: Running the JOB URL DETAILS pipeline:")
        cmd = ['python3', './job_extraction/job_url_details.py', '--job_title', job_title, '--filename', latest_csv]
        
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
