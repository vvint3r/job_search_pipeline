"""
Main script for auto-applying to jobs.
Reads job listings from CSV files and automatically fills out applications.
"""
import sys
import os
import argparse
import logging
import pandas as pd
import time
import random

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from job_search.auto_application.config import load_config, validate_config
from job_search.auto_application.job_board_detector import detect_job_board, get_job_board_info
from job_search.auto_application.application_tracker import ApplicationTracker
from job_search.auto_application.form_fillers import GreenhouseFormFiller, GenericFormFiller
from job_search.job_extraction.driver_utils import create_driver, cleanup_driver

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_form_filler(job_board_type, driver, config):
    """
    Get the appropriate form filler for a job board type.
    
    Args:
        job_board_type: Type of job board (e.g., 'greenhouse', 'workday')
        driver: Selenium WebDriver instance
        config: User configuration
        
    Returns:
        FormFiller instance
    """
    fillers = {
        'greenhouse': GreenhouseFormFiller,
        'generic': GenericFormFiller
    }
    
    filler_class = fillers.get(job_board_type, GenericFormFiller)
    return filler_class(driver, config)

def process_job_application(job_row, driver, config, tracker, auto_submit=False):
    """
    Process a single job application.
    
    Args:
        job_row: Pandas Series with job information
        driver: Selenium WebDriver instance
        config: User configuration
        tracker: ApplicationTracker instance
        auto_submit: Whether to auto-submit applications (default: False)
        
    Returns:
        dict: Result of the application attempt
    """
    job_url = job_row.get('job_url', '')
    job_id = job_row.get('job_id', '')
    
    if not job_url:
        logging.warning("No job URL found in job row")
        return {'success': False, 'message': 'No job URL', 'submitted': False}
    
    # Check if already applied
    if tracker.is_already_applied(job_url, job_id):
        logging.info(f"Already applied to: {job_row.get('job_title', 'Unknown')} at {job_row.get('company', 'Unknown')}")
        return {'success': True, 'message': 'Already applied', 'submitted': False}
    
    # Detect job board type
    job_board_type = detect_job_board(job_url)
    job_board_info = get_job_board_info(job_url)
    
    logging.info(f"Processing application for: {job_row.get('job_title', 'Unknown')} at {job_row.get('company', 'Unknown')}")
    logging.info(f"Job board type: {job_board_type}")
    
    # Get appropriate form filler
    try:
        form_filler = get_form_filler(job_board_type, driver, config)
        
        # Prepare job data
        job_data = {
            'job_id': job_id,
            'job_title': job_row.get('job_title', ''),
            'company': job_row.get('company', ''),
            'job_url': job_url,
            'location': job_row.get('location', ''),
            'description': job_row.get('job_description', '')
        }
        
        # Fill the application
        result = form_filler.fill_application(job_url, job_data)
        
        # Auto-submit if requested (use with caution!)
        if auto_submit and result.get('success') and not result.get('submitted'):
            logging.warning("Auto-submit is enabled. Submitting application...")
            # Note: This would require adding a submit method to form fillers
            # For safety, we'll leave this as a manual step for now
        
        # Log the application
        tracker.log_application(job_data, result, job_board_type)
        
        return result
        
    except Exception as e:
        logging.error(f"Error processing application: {e}")
        error_result = {
            'success': False,
            'message': f'Error: {str(e)}',
            'submitted': False,
            'error': str(e)
        }
        tracker.log_application(
            {
                'job_id': job_id,
                'job_title': job_row.get('job_title', ''),
                'company': job_row.get('company', ''),
                'job_url': job_url
            },
            error_result,
            job_board_type
        )
        return error_result

def load_jobs_from_csv(csv_path, limit=None, filter_applied=True):
    """
    Load jobs from a CSV file.
    
    Args:
        csv_path: Path to the CSV file
        limit: Maximum number of jobs to process (None for all)
        filter_applied: Whether to filter out already applied jobs
        
    Returns:
        DataFrame: Jobs to process
    """
    try:
        df = pd.read_csv(csv_path)
        logging.info(f"Loaded {len(df)} jobs from {csv_path}")
        
        # Filter out jobs without URLs
        df = df[df['job_url'].notna() & (df['job_url'] != '')]
        logging.info(f"After filtering for URLs: {len(df)} jobs")
        
        # Limit number of jobs if specified
        if limit:
            df = df.head(limit)
            logging.info(f"Limited to {limit} jobs")
        
        return df
    except Exception as e:
        logging.error(f"Error loading jobs from CSV: {e}")
        return pd.DataFrame()

def main():
    """Main function to run the auto-application process."""
    parser = argparse.ArgumentParser(description='Auto-apply to jobs from CSV file')
    parser.add_argument('--csv_file', type=str, required=True,
                       help='Path to CSV file with job listings')
    parser.add_argument('--limit', type=int, default=None,
                       help='Maximum number of jobs to process')
    parser.add_argument('--auto_submit', action='store_true',
                       help='Automatically submit applications (use with caution!)')
    parser.add_argument('--headless', action='store_true', default=False,
                       help='Run browser in headless mode (default: False - visible browser)')
    parser.add_argument('--delay_between', type=float, default=5.0,
                       help='Delay between applications in seconds (default: 5.0)')
    
    args = parser.parse_args()
    
    # Load and validate configuration
    config = load_config()
    if not validate_config(config):
        logging.error("Configuration validation failed. Please fill in required fields in user_config.json")
        return
    
    # Load jobs
    jobs_df = load_jobs_from_csv(args.csv_file, limit=args.limit)
    if jobs_df.empty:
        logging.error("No jobs to process")
        return
    
    # Initialize tracker
    tracker = ApplicationTracker()
    
    # Filter out already applied jobs (always do this)
    original_count = len(jobs_df)
    jobs_df = jobs_df[~jobs_df['job_url'].apply(tracker.is_already_applied)]
    filtered_count = len(jobs_df)
    if original_count != filtered_count:
        logging.info(f"Filtered out {original_count - filtered_count} already applied jobs")
    
    if jobs_df.empty:
        logging.info("No new jobs to apply to")
        return
    
    # Initialize browser driver (visible by default)
    driver = None
    try:
        logging.info("Initializing browser...")
        driver = create_driver(headless=args.headless, profile_name="auto_application")
        
        # Process each job
        total_jobs = len(jobs_df)
        successful = 0
        failed = 0
        
        for idx, (_, job_row) in enumerate(jobs_df.iterrows(), 1):
            logging.info(f"\n{'='*60}")
            logging.info(f"Processing job {idx}/{total_jobs}")
            logging.info(f"{'='*60}")
            
            result = process_job_application(job_row, driver, config, tracker, args.auto_submit)
            
            if result.get('success'):
                successful += 1
            else:
                failed += 1
            
            # Delay between applications (except for the last one)
            if idx < total_jobs:
                delay = args.delay_between + random.uniform(-1, 1)
                logging.info(f"Waiting {delay:.1f} seconds before next application...")
                time.sleep(delay)
        
        # Print summary
        logging.info(f"\n{'='*60}")
        logging.info("APPLICATION SUMMARY")
        logging.info(f"{'='*60}")
        logging.info(f"Total jobs processed: {total_jobs}")
        logging.info(f"Successful fills: {successful}")
        logging.info(f"Failed fills: {failed}")
        
        stats = tracker.get_application_stats()
        logging.info(f"\nOverall application stats:")
        logging.info(f"  Total applications logged: {stats['total']}")
        logging.info(f"  Successful: {stats['successful']}")
        logging.info(f"  Failed: {stats['failed']}")
        logging.info(f"  Submitted: {stats['submitted']}")
        
    except KeyboardInterrupt:
        logging.info("\nProcess interrupted by user")
    except Exception as e:
        logging.error(f"Error in main process: {e}")
    finally:
        if driver:
            cleanup_driver(driver)
            logging.info("Browser closed")

if __name__ == "__main__":
    main()

