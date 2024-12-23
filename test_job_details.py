import argparse
import logging
import os
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

def test_job_details(job_title=None, csv_file=None):
    """Test job_url_details.py with existing CSV file."""
    try:
        # If no CSV file provided, find the latest one
        if not csv_file:
            if not job_title:
                raise ValueError("Either job_title or csv_file must be provided")
            csv_file = find_latest_csv(job_title)
        
        # Verify the CSV file exists
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"CSV file not found: {csv_file}")
            
        logging.info(f"Testing job_url_details.py with file: {csv_file}")
        
        # Run job_url_details.py with the CSV file
        import subprocess
        cmd = [
            'python3',
            './job_extraction/job_url_details.py',
            '--job_title', job_title,
            '--filename', csv_file
        ]
        
        logging.info(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Print output
        if result.stdout:
            logging.info("STDOUT:")
            print(result.stdout)
            
        if result.stderr:
            logging.info("STDERR:")
            print(result.stderr)
            
        if result.returncode != 0:
            logging.error(f"Process failed with return code: {result.returncode}")
        else:
            logging.info("Process completed successfully")
            
    except Exception as e:
        logging.error(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test job_url_details.py with existing CSV file')
    parser.add_argument('--job_title', help='Job title to search for latest CSV')
    parser.add_argument('--csv_file', help='Specific CSV file to use')
    
    args = parser.parse_args()
    
    if not args.job_title and not args.csv_file:
        parser.error("Either --job_title or --csv_file must be provided")
        
    test_job_details(args.job_title, args.csv_file) 