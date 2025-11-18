import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import logging
import subprocess
import glob
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def ensure_jobs_ran_file_exists():
    """Create jobs_ran.csv if it doesn't exist."""
    log_dir = os.path.join("job_search", "job_search_results")
    log_file = os.path.join(log_dir, "jobs_ran.csv")
    
    # Create directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Create file with headers if it doesn't exist
    if not os.path.exists(log_file):
        with open(log_file, 'w') as f:
            f.write("timestamp,job_keyword,search_status\n")
        logging.info(f"Created new jobs_ran.csv file at {log_file}")

def find_latest_csv(job_title, search_folder="job_search/job_search_results"):
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

def record_job_search(job_title, status="completed"):
    """Record a job search in the jobs_ran.csv file."""
    log_file = os.path.join("job_search", "job_search_results", "jobs_ran.csv")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, 'a') as f:
        f.write(f"{timestamp},{job_title},{status}\n")
    logging.info(f"Recorded job search for '{job_title}' with status '{status}'")


def run_job_aggregation_pipeline(job_title):
    """Run the job aggregation pipeline to dedupe and consolidate results."""
    try:
        logging.info("PIPELINE 4: Running the JOB AGGREGATION pipeline:")
        cmd = ['python3', './job_search/job_extraction/job_aggregation.py', '--job_title', job_title]
        logging.info(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            stdin=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            logging.error(f"Pipeline 4 failed with output: {result.stdout}\nError: {result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, cmd)
        else:
            logging.info("Pipeline 4 completed successfully")
            
    except Exception as e:
        logging.error(f"Error in Pipeline 4: {e}")
        raise


def run_job_search_pipeline():
    """Run the complete job search pipeline."""
    try:
        logging.info("Starting job search pipeline...")
        
        # Ensure jobs_ran.csv exists
        ensure_jobs_ran_file_exists()
        
        # Prompt for job title if not provided
        job_title = input("Enter the job title to search for: ").strip()
        
        # PIPELINE 1: Run job search
        logging.info("PIPELINE 1: Running the JOB SEARCH pipeline:")
        cmd = ['python3', './job_search/job_extraction/job_search.py', '--job_title', job_title]
        
        result = subprocess.run(
            cmd,
            stdin=None,
            stdout=None,
            stderr=None,
        )
        
        if result.returncode != 0:
            record_job_search(job_title, "failed")
            raise subprocess.CalledProcessError(result.returncode, cmd)
        
        # Record successful search
        record_job_search(job_title, "completed")
        
        # Get the job title that was used (from the latest run in jobs_ran.csv)
        log_file = os.path.join("job_search", "job_search_results", "jobs_ran.csv")
        logging.info(f"Looking for log file at: {log_file}")
        
        if os.path.exists(log_file):
            logging.info("Found jobs_ran.csv file")
            with open(log_file, 'r') as f:
                lines = f.readlines()
                logging.info(f"Found {len(lines)} lines in jobs_ran.csv")
                if len(lines) > 1:  # Header + at least one entry
                    last_line = lines[-1]
                    logging.info(f"Last line from jobs_ran.csv: {last_line.strip()}")
                    job_title = last_line.split(',')[1]  # Assuming job_keyword is second column
                    logging.info(f"Extracted job title: {job_title}")
                    
                    # Find the latest CSV file for this job title
                    try:
                        latest_csv = find_latest_csv(job_title)
                        logging.info(f"Found latest CSV file: {latest_csv}")
                        
                        # PIPELINE 2: Run URL details collection
                        logging.info("PIPELINE 2: Running the JOB URL DETAILS pipeline:")
                        cmd = ['python3', './job_search/job_extraction/job_url_details.py', '--job_title', job_title, '--filename', latest_csv]
                        logging.info(f"Running command: {' '.join(cmd)}")
                        
                        result = subprocess.run(
                            cmd,
                            stdin=None,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                        
                        if result.returncode != 0:
                            logging.error(f"Pipeline 2 failed with output: {result.stdout}\nError: {result.stderr}")
                            raise subprocess.CalledProcessError(result.returncode, cmd)
                        else:
                            logging.info("Pipeline 2 completed successfully")
                            
                            # PIPELINE 3: Merge job details
                            logging.info("PIPELINE 3: Running the JOB DETAILS MERGE pipeline:")
                            cmd = ['python3', './job_search/job_extraction/merge_job_details.py', '--job_title', job_title]
                            logging.info(f"Running command: {' '.join(cmd)}")
                            
                            result = subprocess.run(
                                cmd,
                                stdin=None,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True
                            )
                            
                            if result.returncode != 0:
                                logging.error(f"Pipeline 3 failed with output: {result.stdout}\nError: {result.stderr}")
                                raise subprocess.CalledProcessError(result.returncode, cmd)
                            else:
                                logging.info("Pipeline 3 completed successfully")
                                
                                # Pipeline 3 already handles aggregation, so we're done
                                logging.info("Job search pipeline completed successfully")
                    except FileNotFoundError as e:
                        logging.error(f"Could not find CSV file: {e}")
                    except Exception as e:
                        logging.error(f"Error in Pipeline 2 or 3: {e}")
                else:
                    logging.error("No job entries found in jobs_ran.csv")
        else:
            logging.error(f"Log file not found at {log_file}")
        
        logging.info("Job search pipeline completed")
        
    except Exception as e:
        logging.error(f"Pipeline error: {e}")
        raise

if __name__ == "__main__":
    run_job_search_pipeline()
