import time
import random
import pandas as pd
import re
import json
import logging
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import argparse
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import subprocess
from utils import load_cookie_data
from pyvirtualdisplay import Display



# Set up logging
logging.basicConfig(
    level=logging.INFO,  # Set to INFO to suppress DEBUG messages
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def random_delay(base=1, variance=1):
    time.sleep(base + random.uniform(0, variance))

def get_chrome_version():
    """Get the version of Chrome installed on the system."""
    try:
        version = subprocess.check_output(['google-chrome', '--version'])
        return version.decode().strip().split()[-1]
    except:
        return None

def setup_driver():
    """Initialize and return Chrome driver in headless mode."""
    try:
        logging.info("Starting Chrome driver setup...")
        
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--headless=new')  # New headless mode
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        logging.info("Getting Chrome version...")
        chrome_version = get_chrome_version()
        logging.info(f"Chrome version detected: {chrome_version}")
        
        driver = uc.Chrome(
            options=options,
            version_main=int(chrome_version.split('.')[0]) if chrome_version else None,
            use_subprocess=True
        )
        
        return driver
        
    except Exception as e:
        logging.error(f"Error in setup_driver: {str(e)}")
        raise

def parse_cookies(raw_cookie_data):
    try:
        return json.loads(raw_cookie_data)
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON: {e}")
        return None

def load_cookies(driver, cookies):
    if not cookies:
        logging.warning("No cookies to load.")
        return

    driver.get("https://www.linkedin.com/feed/")
    for cookie in cookies:
        try:
            driver.add_cookie({
                "name": cookie["name"],
                "value": cookie["value"],
                "domain": cookie["domain"],
                "path": cookie.get("path", "/"),
                "secure": cookie.get("secure", False),
                "httpOnly": cookie.get("httpOnly", False),
            })
        except KeyError as e:
            logging.error(f"Skipping cookie due to missing field: {e}")
    driver.refresh()


def get_job_details(driver, url):
    random_delay(2, 3)
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 25)
        
        job_title = company_name = job_description = date_posted = location = salary = remote_status = None
        
        time.sleep(random.uniform(5, 10))
        
        # Expand job description if available
        try:
            show_more_button = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '.feed-shared-inline-show-more-text__see-more-less-toggle')))
            ActionChains(driver).move_to_element(show_more_button).click().perform()
            time.sleep(2)
        except Exception as e:
            print(f"Show more button not found or could not be clicked: {e}")
            time.sleep(2)  # Retry after a brief wait
            try:
                show_more_button = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '.feed-shared-inline-show-more-text__see-more-less-toggle')))
                ActionChains(driver).move_to_element(show_more_button).click().perform()
                time.sleep(2)
            except Exception as e:
                print(f"Retry failed to click show more button: {e}")

        # Extract job title
        try:
            job_title_element = driver.find_element(By.CSS_SELECTOR, 'h1')
            job_title = job_title_element.text.strip()
        except Exception as e:
            print(f"Job title not found: {e}")
            job_title = "-"
        
        # Extract job description
        try:
            # Updated CSS selector to match the HTML provided
            job_description_element = driver.find_element(By.CSS_SELECTOR, 'div.job-details-about-the-job-module__description div.feed-shared-inline-show-more-text')
            
            # Replace dashes with spaces
            job_description = job_description_element.text.replace("-", " ").strip()
            
            # Replace multiple spaces with a single space
            job_description = re.sub(r'\s+', ' ', job_description)
            
            # Remove non-alphanumeric characters
            # job_description = re.sub(r'[^\w\s]', '', job_description)
        except Exception as e:
            print(f"Job description not found: {e}")
            job_description = "-"

        # Extract company name
        try:
            company_name_element = driver.find_element(
                By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__company-name a')
            company_name = company_name_element.text.strip()
        except Exception as e:
            print(f"Company name not found: {e}")
            company_name = "-"

        # Extract date posted
        try:
            # Wait for either of the possible date elements to load
            try:
                date_posted_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'span.tvm__text.tvm__text--positive'))
                )
            except:
                date_posted_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'span.tvm__text.tvm__text--low-emphasis'))
                )
            
            # Extract and clean the date text
            date_posted_text = date_posted_element.text.strip()
            
            # Calculate the date posted
            today = pd.Timestamp('today')
            if 'hour' in date_posted_text:
                hours_ago = int(re.search(r'(\d+)\s*hour', date_posted_text).group(1))
                date_posted = today - pd.Timedelta(hours=hours_ago)
            elif 'day' in date_posted_text:
                days_ago = int(re.search(r'(\d+)\s*day', date_posted_text).group(1))
                date_posted = today - pd.Timedelta(days=days_ago)
            elif 'week' in date_posted_text:
                weeks_ago = int(re.search(r'(\d+)\s*week', date_posted_text).group(1))
                date_posted = today - pd.Timedelta(weeks=weeks_ago)
            elif 'month' in date_posted_text:
                months_ago = int(re.search(r'(\d+)\s*month', date_posted_text).group(1))
                date_posted = today - pd.DateOffset(months=months_ago)
            else:
                date_posted = None
        except Exception as e:
            print(f"Date posted not found or could not be parsed...")
            date_posted = None
            
        # Extract location
        try:
            # Wait for the primary description container
            primary_description_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__primary-description-container'))
            )
            # Locate the first span element with the expected class
            location_element = primary_description_container.find_element(
                By.XPATH, './/span[contains(@class, "tvm__text")]'
            )
            location = location_element.text.strip()
        except Exception as e:
            print(f"Location not found...")
            location = "-"
            
        # Extract salary
        try:
            # Wait for the salary element to be present
            salary_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.job-details-preferences-and-skills__pill span.ui-label.text-body-small"))
            )
            salary = salary_element.text.strip()
        except Exception as e:
            print(f"Salary not found: {e}")
            salary = "-"

        try:
            # Wait for the remote status element
            remote_status_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Remote') or contains(text(), 'Onsite') or contains(text(), 'Hybrid')]"))
            )
            remote_status = remote_status_element.text.strip()
        except Exception as e:
            print(f"Remote status not found, assuming Onsite")
            remote_status = 'Onsite'

        return job_title, company_name, job_description, date_posted, location, remote_status, salary, url
    except Exception as e:
        print(f"Failed to retrieve details from {url}: {e}")
        return "-", "-", "-", "-", "-", "Onsite", "-", url

def load_job_links(filename):
    """Load job links from the CSV file."""
    try:
        # Check if input file exists
        if not os.path.exists(filename):
            logging.warning(f"Input file {filename[:25]} does not exist.")
            return pd.DataFrame(), []  # Return empty DataFrame and list
            
        # Load the CSV file
        df = pd.read_csv(filename)
        links = df['job_url'].tolist() if 'job_url' in df.columns else []
        logging.info(f"Successfully loaded {len(links)} job links from {filename[:25]}")
        return df, links
        
    except Exception as e:
        logging.error(f"Error loading job links: {e}")
        return pd.DataFrame(), []  # Return empty DataFrame and list on error

def save_job_details(df, job_title):
    """Save job details with updated directory and formatting."""
    try:
        # Clean job title for directory name
        job_title_clean = job_title.lower().replace(' ', '_')
        
        # Create base folder structure
        folder_store = f"./job_search/job_post_details/{job_title_clean}"
        os.makedirs(folder_store, exist_ok=True)
        
        # Generate filename with date
        current_date = datetime.now().strftime('%Y%m%d')
        
        # Generate random 5-digit number
        random_number = str(random.randint(10000, 99999))
        
        # Construct the filename (all lowercase) without company name
        base_filename = f"{job_title_clean}_details_{current_date}_{random_number}"
        
        # Save both CSV and JSON versions
        csv_path = os.path.join(folder_store, f"{base_filename}.csv")
        json_path = os.path.join(folder_store, f"{base_filename}.json")
        
        df.to_csv(csv_path, index=False)
        logging.info(f"Results saved to {csv_path}")
        
        # Convert NaT to None or a string
        df = df.where(pd.notnull(df), None)
        
        # Convert datetime columns to strings
        for col in df.select_dtypes(include=['datetime64[ns]']).columns:
            df[col] = df[col].astype(str)
        
        # Save as JSON with metadata (keeping company in metadata only)
        company_name = df['company'].iloc[0] if not df.empty else 'unknown'
        company_name_clean = company_name.lower().replace(' ', '_').replace(',', '').replace('.', '')
        
        output_data = {
            "metadata": {
                "job_title": job_title_clean,
                "company": company_name_clean,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "file_id": random_number
            },
            "jobs": df.to_dict('records')
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        logging.info(f"Results saved to {json_path}")
        
        return csv_path
        
    except Exception as e:
        logging.error(f"Error saving job details: {e}")
        raise

def process_job_links(driver, links, job_title):
    """Process job links with updated column structure."""
    results = []
    for url in links:
        try:
            logging.info(f"Processing URL: {url[:50]}")
            job_details = get_job_details(driver, url)
            if job_details[0] != "-":  # Only add if we got valid details
                results.append(job_details)
        except Exception as e:
            logging.error(f"Error processing URL {url[:50]}: {e}")
            continue
    
    if not results:
        logging.warning("No valid job details were collected")
        return
    
    # Create DataFrame with updated columns including URL
    df = pd.DataFrame(results, columns=[
        'job_title', 'company', 'description', 'date_posted', 
        'location', 'remote', 'salary', 'job_url'
    ])
    
    # Clean job title for saving
    job_title_clean = job_title.lower().replace(' ', '_')
    save_job_details(df, job_title_clean)

def main(job_title, input_filename):
    """Main function with cleaned job title."""
    driver = None
    try:
        # Clean job title
        job_title_clean = job_title.lower().replace(' ', '_')
        
        # Load job links from input file
        logging.info(f"Loading job links from {input_filename}")
        df, links = load_job_links(input_filename)
        if not links:
            logging.warning("No job links found to process.")
            return

        # Initialize driver
        logging.info("Initializing Chrome driver...")
        driver = setup_driver()
        
        try:
            # Load cookies
            logging.info("Loading cookies...")
            cookies = load_cookie_data()
            if cookies:
                load_cookies(driver, cookies)
            else:
                logging.warning("No cookies loaded")
            
            # Process job links with cleaned job title
            logging.info("Starting to process job links...")
            process_job_links(driver, links, job_title_clean)
            
        finally:
            if driver:
                logging.info("Closing Chrome driver...")
                driver.quit()
                
    except Exception as e:
        logging.error(f"Error in main processing: {str(e)}")
        if driver:
            try:
                driver.quit()
            except:
                pass
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_title", required=True)
    parser.add_argument("--filename", required=True)
    args = parser.parse_args()
    
    main(args.job_title, args.filename)
