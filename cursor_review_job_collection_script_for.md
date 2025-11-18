# Review job collection script for location labels
_Exported on 11/16/2025 at 05:01:44 MST from Cursor (2.0.69)_

---

**User**

Can you review the job collection script that starts from @main_get_jobs.py to see why we aren't getting the location type label during extraction? For example, they are typically "Remote", "Hyrid", "Onsite". I've attached an export of the HTML of a sample page that we would parse located in @temp_li_code.txt.  Specifically, it's located in this area of the code:



<div class="job-details-fit-level-preferences">

            <button tabindex="0" class="artdeco-button artdeco-button--secondary artdeco-button--muted" type="button">

              <span aria-hidden="true"><span class="tvm__text tvm__text--low-emphasis"><strong><li-icon aria-hidden="true" type="check" class="v-align-bottom" size="small"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" data-supported-dps="16x16" fill="currentColor" class="mercado-match" width="16" height="16" focusable="false">

      <path d="M12.57 2H15L6 15l-5-5 1.41-1.41 3.31 3.3z"></path>

    </svg></li-icon><span class="white-space-pre"> </span>Remote<!----></strong></span></span><span class="visually-hidden"><!---->Matches your job preferences, workplace type is Remote.<!----></span>

            </button>

            <button tabindex="0" class="artdeco-button artdeco-button--secondary artdeco-button--muted" type="button">

              <span aria-hidden="true"><span class="tvm__text tvm__text--low-emphasis"><strong><li-icon aria-hidden="true" type="check" class="v-align-bottom" size="small"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" data-supported-dps="16x16" fill="currentColor" class="mercado-match" width="16" height="16" focusable="false">

      <path d="M12.57 2H15L6 15l-5-5 1.41-1.41 3.31 3.3z"></path>

    </svg></li-icon><span class="white-space-pre"> </span>Full-time<!----></strong></span></span><span class="visually-hidden"><!---->Matches your job preferences, job type is Full-time.<!----></span>

            </button>

      </div>

---

**Cursor**

Reviewing the job collection pipeline to identify why location type labels aren't being extracted. Examining the relevant files.


Reading the full extraction file and searching the HTML sample for the location type structure:


Checking the exact HTML structure around the location type:


The location type is inside `div.job-details-fit-level-preferences` within a button. The current XPath is too generic and may miss it. Updating the extraction to target that container and extract the location type correctly:


The current XPath selector is too generic and may match other elements or miss the location type. The location type is inside `div.job-details-fit-level-preferences` within a button.

Here's the fix for the `remote_status` extraction in `job_url_details.py`:

```python:job_search/job_extraction/job_url_details.py
            try:
                # Look for the job-details-fit-level-preferences container first
                preferences_container = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.job-details-fit-level-preferences")))
                
                # Find buttons within the container that contain location type text
                buttons = preferences_container.find_elements(By.TAG_NAME, "button")
                remote_status = "Onsite"  # Default fallback
                
                for button in buttons:
                    button_text = button.text.strip()
                    # Check if button contains location type keywords
                    if any(keyword in button_text for keyword in ["Remote", "Hybrid", "Onsite"]):
                        # Extract just the location type (may have other text like "Full-time")
                        if "Remote" in button_text:
                            remote_status = "Remote"
                            break
                        elif "Hybrid" in button_text:
                            remote_status = "Hybrid"
                            break
                        elif "Onsite" in button_text:
                            remote_status = "Onsite"
                            break
                
            except Exception as e:
                logging.warning(f"Could not extract remote status: {e}")
                remote_status = "Onsite"
```

This approach:
1. Targets the specific container `div.job-details-fit-level-preferences`
2. Finds buttons within that container
3. Checks each button for location type keywords
4. Prioritizes "Remote" > "Hybrid" > "Onsite" if multiple are present

Should I apply this change to the file?

```python
            try:
                # Look for the job-details-fit-level-preferences container first
                preferences_container = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.job-details-fit-level-preferences")))
                
                # Find buttons within the container that contain location type text
                buttons = preferences_container.find_elements(By.TAG_NAME, "button")
                remote_status = "Onsite"  # Default fallback
                
                for button in buttons:
                    button_text = button.text.strip()
                    # Check if button contains location type keywords
                    if any(keyword in button_text for keyword in ["Remote", "Hybrid", "Onsite"]):
                        # Extract just the location type (may have other text like "Full-time")
                        if "Remote" in button_text:
                            remote_status = "Remote"
                            break
                        elif "Hybrid" in button_text:
                            remote_status = "Hybrid"
                            break
                        elif "Onsite" in button_text:
                            remote_status = "Onsite"
                            break
                
            except Exception as e:
                logging.warning(f"Could not extract remote status: {e}")
                remote_status = "Onsite"
```

---

**User**

Yes, please.

---

**Cursor**

Applying the fix. Checking the current state of the file:


Applying the fix to target the specific location type container:


```python
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
from job_metrics_tracker import JobMetricsTracker
import uuid
import shutil
from driver_utils import create_driver, cleanup_driver

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
    """Get details for a single job posting."""
    max_retries = 2  # Reduced retries since we're using batch processing
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logging.info(f"Processing URL: {url}")
            
            # Initial page load with delay
            driver.get(url)
            time.sleep(random.uniform(3, 5))
            
            wait = WebDriverWait(driver, 15)
            
            # Initialize variables
            job_title = company_name = job_description = date_posted = location = salary = remote_status = None
            
            # Extract job details with minimal delays
            try:
                show_more_button = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '.feed-shared-inline-show-more-text__see-more-less-toggle')))
                driver.execute_script("arguments[0].click();", show_more_button)
            except Exception as e:
                logging.warning(f"Show more button not found: {e}")
            
            # Extract all fields with appropriate waits
            job_title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1'))).text.strip()
            
            try:
                job_description_element = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-about-the-job-module__description div.feed-shared-inline-show-more-text')))
                job_description = job_description_element.text.replace("-", " ").strip()
                job_description = re.sub(r'\s+', ' ', job_description)
            except:
                job_description = "-"
                
            try:
                company_name = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__company-name a'))).text.strip()
            except:
                company_name = "-"
                
            try:
                date_element = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'span.tvm__text.tvm__text--positive, span.tvm__text.tvm__text--low-emphasis')))
                date_posted = parse_date_posted(date_element.text.strip())
            except:
                date_posted = None
                
            try:
                location = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__primary-description-container span.tvm__text'))).text.strip()
            except:
                location = "-"
                
            try:
                salary = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.job-details-preferences-and-skills__pill span.ui-label.text-body-small"))).text.strip()
            except:
                salary = "-"
                
            try:
                # Look for the job-details-fit-level-preferences container first
                preferences_container = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.job-details-fit-level-preferences")))
                
                # Find buttons within the container that contain location type text
                buttons = preferences_container.find_elements(By.TAG_NAME, "button")
                remote_status = "Onsite"  # Default fallback
                
                for button in buttons:
                    button_text = button.text.strip()
                    # Check if button contains location type keywords
                    if any(keyword in button_text for keyword in ["Remote", "Hybrid", "Onsite"]):
                        # Extract just the location type (may have other text like "Full-time")
                        if "Remote" in button_text:
                            remote_status = "Remote"
                            break
                        elif "Hybrid" in button_text:
                            remote_status = "Hybrid"
                            break
                        elif "Onsite" in button_text:
                            remote_status = "Onsite"
                            break
                
            except Exception as e:
                logging.warning(f"Could not extract remote status: {e}")
                remote_status = "Onsite"
            
            return job_title, company_name, job_description, date_posted, location, remote_status, salary, url
            
        except Exception as e:
            retry_count += 1
            logging.warning(f"Attempt {retry_count} failed for URL {url}: {e}")
            if retry_count < max_retries:
                time.sleep(random.uniform(5, 8))
            else:
                logging.error(f"Failed to retrieve details after {max_retries} attempts")
                return "-", "-", "-", None, "-", "Onsite", "-", url

def parse_date_posted(date_text):
    """Parse the date posted text into a timestamp."""
    try:
        today = pd.Timestamp('today')
        if 'hour' in date_text:
            hours = int(re.search(r'(\d+)\s*hour', date_text).group(1))
            return today - pd.Timedelta(hours=hours)
        elif 'day' in date_text:
            days = int(re.search(r'(\d+)\s*day', date_text).group(1))
            return today - pd.Timedelta(days=days)
        elif 'week' in date_text:
            weeks = int(re.search(r'(\d+)\s*week', date_text).group(1))
            return today - pd.Timedelta(weeks=weeks)
        elif 'month' in date_text:
            months = int(re.search(r'(\d+)\s*month', date_text).group(1))
            return today - pd.DateOffset(months=months)
    except Exception as e:
        logging.warning(f"Could not parse date: {date_text} - {e}")
        return None

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

def generate_unique_id():
    """Generate a unique ID using UUID4."""
    return str(uuid.uuid4())

def save_job_details(df, job_title):
    """Save job details with updated directory and formatting."""
    try:
        # Add unique IDs to each job record
        df['job_id'] = [generate_unique_id() for _ in range(len(df))]
        
        # Clean job title for directory name
        job_title_clean = job_title.lower().replace(' ', '_')
        
        # Create base folder structure with job_details subdirectory
        folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
        os.makedirs(folder_store, exist_ok=True)
        
        # Generate filename with date
        current_date = datetime.now().strftime('%Y%m%d')
        
        # Generate random 5-digit number
        random_number = str(random.randint(10000, 99999))
        
        # Construct the filename (all lowercase) without company name
        base_filename = f"{job_title_clean}_details_{current_date}_{random_number}"
        
        # Reorder columns to have job_id first
        cols = ['job_id'] + [col for col in df.columns if col != 'job_id']
        df = df[cols]
        
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

def process_job_links(links, output_dir, job_title):
    """Process job links in batches with appropriate delays."""
    try:
        # Initialize driver once
        driver = create_driver()
        load_cookies(driver, load_cookie_data())
        
        # Process in small batches
        batch_size = 3
        results = []
        
        for i in range(0, len(links), batch_size):
            batch = links[i:i + batch_size]
            logging.info(f"Processing batch {i//batch_size + 1} of {(len(links) + batch_size - 1)//batch_size}")
            
            # Process each URL in the batch
            for url in batch:
                try:
                    job_details = get_job_details(driver, url)
                    if job_details:
                        results.append(job_details)
                except Exception as e:
                    logging.error(f"Error processing URL {url}: {e}")
                    continue
                
                # Add delay between jobs within batch (5-10 seconds)
                time.sleep(random.uniform(5, 10))
            
            # Add longer delay between batches (20-30 seconds)
            if i + batch_size < len(links):
                delay = random.uniform(20, 30)
                logging.info(f"Taking a break between batches ({delay:.1f} seconds)...")
                time.sleep(delay)
        
        # Create results DataFrame
        df_results = pd.DataFrame(results, columns=[
            'job_title', 'company', 'description', 'date_posted',
            'location', 'remote', 'salary', 'job_url'
        ])
        
        # Save results in job_details directory
        job_title_clean = job_title.lower().replace(' ', '_')
        folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
        os.makedirs(folder_store, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{job_title_clean}_job_details_{timestamp}.csv"
        output_path = os.path.join(folder_store, output_filename)
        
        # Save both CSV and JSON
        df_results.to_csv(output_path, index=False)
        logging.info(f"Results saved to {output_path}")
        
        # Save JSON version
        json_path = output_path.replace('.csv', '.json')
        output_data = {
            "metadata": {
                "job_title": job_title_clean,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_jobs": len(df_results)
            },
            "jobs": df_results.to_dict('records')
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        logging.info(f"Results saved to {json_path}")
        
        return df_results
        
    except Exception as e:
        logging.error(f"Error in process_job_links: {e}")
        return pd.DataFrame()
    finally:
        try:
            cleanup_driver(driver)
        except:
            pass

def main(job_title, input_filename):
    """Main function with cleaned job title."""
    driver = None
    try:
        # Clean job title
        job_title_clean = job_title.lower().replace(' ', '_')
        
        # Initialize metrics tracker
        metrics_tracker = JobMetricsTracker()
        
        # Load job links from input file
        logging.info(f"Loading job links from {input_filename}")
        df, links = load_job_links(input_filename)
        if not links:
            logging.warning("No job links found to process.")
            return

        # Initialize driver
        logging.info("Initializing Chrome driver...")
        driver = create_driver()
        
        try:
            # Load cookies
            logging.info("Loading cookies...")
            cookies = load_cookie_data()
            if cookies:
                load_cookies(driver, cookies)
            else:
                logging.warning("No cookies loaded")
            
            # Process job links and collect detailed information
            logging.info("Starting to process job links...")
            detailed_jobs = []
            for link in links:
                job_details = get_job_details(driver, link)
                if job_details:
                    # Convert tuple to dictionary
                    job_dict = {
                        'job_title': job_details[0],
                        'company': job_details[1],
                        'description': job_details[2],
                        'date_posted': job_details[3],
                        'location': job_details[4],
                        'remote': job_details[5],
                        'salary': job_details[6],
                        'job_url': job_details[7]
                    }
                    detailed_jobs.append(job_dict)
            
            # Create DataFrame from detailed jobs
            if detailed_jobs:
                df_results = pd.DataFrame(detailed_jobs)
                
                # Save to job details directory
                folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
                os.makedirs(folder_store, exist_ok=True)
                
                # Generate filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = f"{job_title_clean}_job_details_{timestamp}.csv"
                output_path = os.path.join(folder_store, output_filename)
                
                # Save CSV
                df_results.to_csv(output_path, index=False)
                logging.info(f"Results saved to {output_path}")
                
                # Save JSON version
                json_path = output_path.replace('.csv', '.json')
                output_data = {
                    "metadata": {
                        "job_title": job_title_clean,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "total_jobs": len(df_results)
                    },
                    "jobs": df_results.to_dict('records')
                }
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                logging.info(f"Results saved to {json_path}")
                
                # Update metrics
                metrics_tracker.update_jobs_aggregation(
                    job_title=job_title,
                    new_jobs=detailed_jobs
                )
            
        finally:
            if driver:
                logging.info("Closing Chrome driver...")
                cleanup_driver(driver)
                
    except Exception as e:
        logging.error(f"Error in main processing: {str(e)}")
        if driver:
            try:
                cleanup_driver(driver)
            except:
                pass
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_title", required=True)
    parser.add_argument("--filename", required=True)
    args = parser.parse_args()
    
    main(args.job_title, args.filename)

```

Checking for linting errors:


Fix applied. The code now:

1. **Targets the specific container**: Uses `div.job-details-fit-level-preferences` where the location type is located
2. **Finds buttons within the container**: Iterates through buttons in that section
3. **Extracts location type**: Checks each button's text for "Remote", "Hybrid", or "Onsite"
4. **Prioritizes correctly**: If multiple are present, prioritizes Remote > Hybrid > Onsite
5. **Has proper error handling**: Logs warnings if extraction fails and defaults to "Onsite"

This should correctly extract location type labels ("Remote", "Hybrid", "Onsite") from LinkedIn job posting pages based on the HTML structure you provided. The fix replaces the generic XPath that could match elements elsewhere on the page with a targeted approach that specifically looks in the preferences container.

No linting errors found. Ready to test.

---

**User**

Can you also add the extraction of the date posted text located in the follow area of the code - in the example, it says "Reposted 1 day ago":



<div class="job-details-jobs-unified-top-card__primary-description-container">

              <div class="t-black--light mt2 job-details-jobs-unified-top-card__tertiary-description-container">

                <span dir="ltr"><span class="tvm__text tvm__text--low-emphasis"><!---->United States<!----></span><span class="tvm__text tvm__text--low-emphasis"><span class="white-space-pre"> </span>·<span class="white-space-pre"> </span></span><span class="tvm__text tvm__text--low-emphasis"><!---->Reposted<span class="white-space-pre"> </span><span><!---->1 day ago<!----></span></span><span class="tvm__text tvm__text--low-emphasis"><span class="white-space-pre"> </span>·<span class="white-space-pre"> </span></span><span class="tvm__text tvm__text--low-emphasis"><!---->Over 100 applicants<!----></span><p><span class="tvm__text tvm__text--low-emphasis"><!---->Promoted by hirer<!----></span><span class="tvm__text tvm__text--low-emphasis"><span class="white-space-pre"> </span>·<span class="white-space-pre"> </span></span><span class="tvm__text tvm__text--positive"><strong><!---->Actively reviewing applicants<!----></strong></span></p></span>

              </div>

          </div>

---

**Cursor**

Reviewing the current date extraction and updating it to target the correct element:


Checking for other date patterns in the HTML:


Updating the date extraction to target the correct element. The current selector is too generic. Updating it to extract the date text from the tertiary description container:


```python
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
from job_metrics_tracker import JobMetricsTracker
import uuid
import shutil
from driver_utils import create_driver, cleanup_driver

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
    """Get details for a single job posting."""
    max_retries = 2  # Reduced retries since we're using batch processing
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logging.info(f"Processing URL: {url}")
            
            # Initial page load with delay
            driver.get(url)
            time.sleep(random.uniform(3, 5))
            
            wait = WebDriverWait(driver, 15)
            
            # Initialize variables
            job_title = company_name = job_description = date_posted = location = salary = remote_status = None
            
            # Extract job details with minimal delays
            try:
                show_more_button = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '.feed-shared-inline-show-more-text__see-more-less-toggle')))
                driver.execute_script("arguments[0].click();", show_more_button)
            except Exception as e:
                logging.warning(f"Show more button not found: {e}")
            
            # Extract all fields with appropriate waits
            job_title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1'))).text.strip()
            
            try:
                job_description_element = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-about-the-job-module__description div.feed-shared-inline-show-more-text')))
                job_description = job_description_element.text.replace("-", " ").strip()
                job_description = re.sub(r'\s+', ' ', job_description)
            except:
                job_description = "-"
                
            try:
                company_name = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__company-name a'))).text.strip()
            except:
                company_name = "-"
                
            try:
                # Target the tertiary description container where date info is located
                tertiary_container = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__tertiary-description-container')))
                
                # Find spans that contain "Reposted" or "Posted" followed by time information
                date_text = None
                spans = tertiary_container.find_elements(By.CSS_SELECTOR, 'span.tvm__text.tvm__text--low-emphasis')
                
                for span in spans:
                    span_text = span.text.strip()
                    # Check if this span contains date-related keywords
                    if 'Reposted' in span_text or 'Posted' in span_text:
                        # Get the full text including nested spans
                        date_text = span_text
                        break
                
                if date_text:
                    date_posted = parse_date_posted(date_text)
                else:
                    date_posted = None
            except Exception as e:
                logging.warning(f"Could not extract date posted: {e}")
                date_posted = None
                
            try:
                location = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__primary-description-container span.tvm__text'))).text.strip()
            except:
                location = "-"
                
            try:
                salary = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.job-details-preferences-and-skills__pill span.ui-label.text-body-small"))).text.strip()
            except:
                salary = "-"
                
            try:
                # Look for the job-details-fit-level-preferences container first
                preferences_container = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.job-details-fit-level-preferences")))
                
                # Find buttons within the container that contain location type text
                buttons = preferences_container.find_elements(By.TAG_NAME, "button")
                remote_status = "Onsite"  # Default fallback
                
                for button in buttons:
                    button_text = button.text.strip()
                    # Check if button contains location type keywords
                    if any(keyword in button_text for keyword in ["Remote", "Hybrid", "Onsite"]):
                        # Extract just the location type (may have other text like "Full-time")
                        if "Remote" in button_text:
                            remote_status = "Remote"
                            break
                        elif "Hybrid" in button_text:
                            remote_status = "Hybrid"
                            break
                        elif "Onsite" in button_text:
                            remote_status = "Onsite"
                            break
                
            except Exception as e:
                logging.warning(f"Could not extract remote status: {e}")
                remote_status = "Onsite"
            
            return job_title, company_name, job_description, date_posted, location, remote_status, salary, url
            
        except Exception as e:
            retry_count += 1
            logging.warning(f"Attempt {retry_count} failed for URL {url}: {e}")
            if retry_count < max_retries:
                time.sleep(random.uniform(5, 8))
            else:
                logging.error(f"Failed to retrieve details after {max_retries} attempts")
                return "-", "-", "-", None, "-", "Onsite", "-", url

def parse_date_posted(date_text):
    """Parse the date posted text into a timestamp."""
    try:
        today = pd.Timestamp('today')
        if 'hour' in date_text:
            hours = int(re.search(r'(\d+)\s*hour', date_text).group(1))
            return today - pd.Timedelta(hours=hours)
        elif 'day' in date_text:
            days = int(re.search(r'(\d+)\s*day', date_text).group(1))
            return today - pd.Timedelta(days=days)
        elif 'week' in date_text:
            weeks = int(re.search(r'(\d+)\s*week', date_text).group(1))
            return today - pd.Timedelta(weeks=weeks)
        elif 'month' in date_text:
            months = int(re.search(r'(\d+)\s*month', date_text).group(1))
            return today - pd.DateOffset(months=months)
    except Exception as e:
        logging.warning(f"Could not parse date: {date_text} - {e}")
        return None

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

def generate_unique_id():
    """Generate a unique ID using UUID4."""
    return str(uuid.uuid4())

def save_job_details(df, job_title):
    """Save job details with updated directory and formatting."""
    try:
        # Add unique IDs to each job record
        df['job_id'] = [generate_unique_id() for _ in range(len(df))]
        
        # Clean job title for directory name
        job_title_clean = job_title.lower().replace(' ', '_')
        
        # Create base folder structure with job_details subdirectory
        folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
        os.makedirs(folder_store, exist_ok=True)
        
        # Generate filename with date
        current_date = datetime.now().strftime('%Y%m%d')
        
        # Generate random 5-digit number
        random_number = str(random.randint(10000, 99999))
        
        # Construct the filename (all lowercase) without company name
        base_filename = f"{job_title_clean}_details_{current_date}_{random_number}"
        
        # Reorder columns to have job_id first
        cols = ['job_id'] + [col for col in df.columns if col != 'job_id']
        df = df[cols]
        
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

def process_job_links(links, output_dir, job_title):
    """Process job links in batches with appropriate delays."""
    try:
        # Initialize driver once
        driver = create_driver()
        load_cookies(driver, load_cookie_data())
        
        # Process in small batches
        batch_size = 3
        results = []
        
        for i in range(0, len(links), batch_size):
            batch = links[i:i + batch_size]
            logging.info(f"Processing batch {i//batch_size + 1} of {(len(links) + batch_size - 1)//batch_size}")
            
            # Process each URL in the batch
            for url in batch:
                try:
                    job_details = get_job_details(driver, url)
                    if job_details:
                        results.append(job_details)
                except Exception as e:
                    logging.error(f"Error processing URL {url}: {e}")
                    continue
                
                # Add delay between jobs within batch (5-10 seconds)
                time.sleep(random.uniform(5, 10))
            
            # Add longer delay between batches (20-30 seconds)
            if i + batch_size < len(links):
                delay = random.uniform(20, 30)
                logging.info(f"Taking a break between batches ({delay:.1f} seconds)...")
                time.sleep(delay)
        
        # Create results DataFrame
        df_results = pd.DataFrame(results, columns=[
            'job_title', 'company', 'description', 'date_posted',
            'location', 'remote', 'salary', 'job_url'
        ])
        
        # Save results in job_details directory
        job_title_clean = job_title.lower().replace(' ', '_')
        folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
        os.makedirs(folder_store, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{job_title_clean}_job_details_{timestamp}.csv"
        output_path = os.path.join(folder_store, output_filename)
        
        # Save both CSV and JSON
        df_results.to_csv(output_path, index=False)
        logging.info(f"Results saved to {output_path}")
        
        # Save JSON version
        json_path = output_path.replace('.csv', '.json')
        output_data = {
            "metadata": {
                "job_title": job_title_clean,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_jobs": len(df_results)
            },
            "jobs": df_results.to_dict('records')
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        logging.info(f"Results saved to {json_path}")
        
        return df_results
        
    except Exception as e:
        logging.error(f"Error in process_job_links: {e}")
        return pd.DataFrame()
    finally:
        try:
            cleanup_driver(driver)
        except:
            pass

def main(job_title, input_filename):
    """Main function with cleaned job title."""
    driver = None
    try:
        # Clean job title
        job_title_clean = job_title.lower().replace(' ', '_')
        
        # Initialize metrics tracker
        metrics_tracker = JobMetricsTracker()
        
        # Load job links from input file
        logging.info(f"Loading job links from {input_filename}")
        df, links = load_job_links(input_filename)
        if not links:
            logging.warning("No job links found to process.")
            return

        # Initialize driver
        logging.info("Initializing Chrome driver...")
        driver = create_driver()
        
        try:
            # Load cookies
            logging.info("Loading cookies...")
            cookies = load_cookie_data()
            if cookies:
                load_cookies(driver, cookies)
            else:
                logging.warning("No cookies loaded")
            
            # Process job links and collect detailed information
            logging.info("Starting to process job links...")
            detailed_jobs = []
            for link in links:
                job_details = get_job_details(driver, link)
                if job_details:
                    # Convert tuple to dictionary
                    job_dict = {
                        'job_title': job_details[0],
                        'company': job_details[1],
                        'description': job_details[2],
                        'date_posted': job_details[3],
                        'location': job_details[4],
                        'remote': job_details[5],
                        'salary': job_details[6],
                        'job_url': job_details[7]
                    }
                    detailed_jobs.append(job_dict)
            
            # Create DataFrame from detailed jobs
            if detailed_jobs:
                df_results = pd.DataFrame(detailed_jobs)
                
                # Save to job details directory
                folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
                os.makedirs(folder_store, exist_ok=True)
                
                # Generate filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = f"{job_title_clean}_job_details_{timestamp}.csv"
                output_path = os.path.join(folder_store, output_filename)
                
                # Save CSV
                df_results.to_csv(output_path, index=False)
                logging.info(f"Results saved to {output_path}")
                
                # Save JSON version
                json_path = output_path.replace('.csv', '.json')
                output_data = {
                    "metadata": {
                        "job_title": job_title_clean,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "total_jobs": len(df_results)
                    },
                    "jobs": df_results.to_dict('records')
                }
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                logging.info(f"Results saved to {json_path}")
                
                # Update metrics
                metrics_tracker.update_jobs_aggregation(
                    job_title=job_title,
                    new_jobs=detailed_jobs
                )
            
        finally:
            if driver:
                logging.info("Closing Chrome driver...")
                cleanup_driver(driver)
                
    except Exception as e:
        logging.error(f"Error in main processing: {str(e)}")
        if driver:
            try:
                cleanup_driver(driver)
            except:
                pass
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_title", required=True)
    parser.add_argument("--filename", required=True)
    args = parser.parse_args()
    
    main(args.job_title, args.filename)

```

Checking if we should also store the raw date text (e.g., "Reposted 1 day ago") in addition to the parsed date. Reviewing the return structure:


Checking if `parse_date_posted` handles the "Reposted" prefix:


The `parse_date_posted` function should handle "Reposted 1 day ago" since it uses regex to extract the time portion. Verifying the extraction captures the full text, including nested spans. Updating to ensure we get the complete text:


Checking for linting errors:


Updated the date extraction. The code now:

1. **Targets the specific container**: Uses `div.job-details-jobs-unified-top-card__tertiary-description-container` where the date information is located
2. **Finds date-related spans**: Searches for spans containing "Reposted" or "Posted"
3. **Extracts the full text**: Captures the complete text like "Reposted 1 day ago" (including nested spans)
4. **Parses the date**: Uses the existing `parse_date_posted` function which extracts the time portion (e.g., "1 day") and converts it to a timestamp

The extraction now correctly finds date text like "Reposted 1 day ago" from the tertiary description container, instead of using a generic selector that might match other elements. The `parse_date_posted` function will handle the "Reposted" prefix since it uses regex to extract the numeric time value.

No linting errors found. Ready to test.

---

**User**

Can you add a separate column in the output that would subtract the date of posting against the date of extraction? Typically, they labels that are used would be "1 week ago", "2 weeks ago", "1 day ago", "2 days ago", etc. So the calculation would be the date today subtracted by the amount of days based on the label that has passed.

---

**Cursor**

Adding a column for days since posting. Checking the current structure to see where to add it:


Checking where the return values are used to update all references:


Checking the error return case:


Adding a function to calculate days since posting and updating all relevant places:


```python
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
from job_metrics_tracker import JobMetricsTracker
import uuid
import shutil
from driver_utils import create_driver, cleanup_driver

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
    """Get details for a single job posting."""
    max_retries = 2  # Reduced retries since we're using batch processing
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logging.info(f"Processing URL: {url}")
            
            # Initial page load with delay
            driver.get(url)
            time.sleep(random.uniform(3, 5))
            
            wait = WebDriverWait(driver, 15)
            
            # Initialize variables
            job_title = company_name = job_description = date_posted = location = salary = remote_status = None
            
            # Extract job details with minimal delays
            try:
                show_more_button = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '.feed-shared-inline-show-more-text__see-more-less-toggle')))
                driver.execute_script("arguments[0].click();", show_more_button)
            except Exception as e:
                logging.warning(f"Show more button not found: {e}")
            
            # Extract all fields with appropriate waits
            job_title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1'))).text.strip()
            
            try:
                job_description_element = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-about-the-job-module__description div.feed-shared-inline-show-more-text')))
                job_description = job_description_element.text.replace("-", " ").strip()
                job_description = re.sub(r'\s+', ' ', job_description)
            except:
                job_description = "-"
                
            try:
                company_name = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__company-name a'))).text.strip()
            except:
                company_name = "-"
                
            try:
                # Target the tertiary description container where date info is located
                tertiary_container = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__tertiary-description-container')))
                
                # Find spans that contain "Reposted" or "Posted" followed by time information
                date_text = None
                spans = tertiary_container.find_elements(By.CSS_SELECTOR, 'span.tvm__text.tvm__text--low-emphasis')
                
                for span in spans:
                    span_text = span.text.strip()
                    # Check if this span contains date-related keywords
                    if 'Reposted' in span_text or 'Posted' in span_text:
                        # Get the full text including nested spans
                        date_text = span_text
                        break
                
                if date_text:
                    date_posted = parse_date_posted(date_text)
                else:
                    date_posted = None
            except Exception as e:
                logging.warning(f"Could not extract date posted: {e}")
                date_posted = None
                
            try:
                location = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__primary-description-container span.tvm__text'))).text.strip()
            except:
                location = "-"
                
            try:
                salary = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.job-details-preferences-and-skills__pill span.ui-label.text-body-small"))).text.strip()
            except:
                salary = "-"
                
            try:
                # Look for the job-details-fit-level-preferences container first
                preferences_container = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.job-details-fit-level-preferences")))
                
                # Find buttons within the container that contain location type text
                buttons = preferences_container.find_elements(By.TAG_NAME, "button")
                remote_status = "Onsite"  # Default fallback
                
                for button in buttons:
                    button_text = button.text.strip()
                    # Check if button contains location type keywords
                    if any(keyword in button_text for keyword in ["Remote", "Hybrid", "Onsite"]):
                        # Extract just the location type (may have other text like "Full-time")
                        if "Remote" in button_text:
                            remote_status = "Remote"
                            break
                        elif "Hybrid" in button_text:
                            remote_status = "Hybrid"
                            break
                        elif "Onsite" in button_text:
                            remote_status = "Onsite"
                            break
                
            except Exception as e:
                logging.warning(f"Could not extract remote status: {e}")
                remote_status = "Onsite"
            
            return job_title, company_name, job_description, date_posted, location, remote_status, salary, url
            
        except Exception as e:
            retry_count += 1
            logging.warning(f"Attempt {retry_count} failed for URL {url}: {e}")
            if retry_count < max_retries:
                time.sleep(random.uniform(5, 8))
            else:
                logging.error(f"Failed to retrieve details after {max_retries} attempts")
                return "-", "-", "-", None, "-", "Onsite", "-", url

def parse_date_posted(date_text):
    """Parse the date posted text into a timestamp."""
    try:
        today = pd.Timestamp('today')
        if 'hour' in date_text:
            hours = int(re.search(r'(\d+)\s*hour', date_text).group(1))
            return today - pd.Timedelta(hours=hours)
        elif 'day' in date_text:
            days = int(re.search(r'(\d+)\s*day', date_text).group(1))
            return today - pd.Timedelta(days=days)
        elif 'week' in date_text:
            weeks = int(re.search(r'(\d+)\s*week', date_text).group(1))
            return today - pd.Timedelta(weeks=weeks)
        elif 'month' in date_text:
            months = int(re.search(r'(\d+)\s*month', date_text).group(1))
            return today - pd.DateOffset(months=months)
    except Exception as e:
        logging.warning(f"Could not parse date: {date_text} - {e}")
        return None

def calculate_days_since_posted(date_posted):
    """Calculate the number of days between the extraction date and the posting date."""
    if date_posted is None:
        return None
    try:
        today = pd.Timestamp('today').normalize()
        posted_date = pd.Timestamp(date_posted).normalize()
        days_diff = (today - posted_date).days
        return days_diff
    except Exception as e:
        logging.warning(f"Could not calculate days since posted: {e}")
        return None

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

def generate_unique_id():
    """Generate a unique ID using UUID4."""
    return str(uuid.uuid4())

def save_job_details(df, job_title):
    """Save job details with updated directory and formatting."""
    try:
        # Add unique IDs to each job record
        df['job_id'] = [generate_unique_id() for _ in range(len(df))]
        
        # Clean job title for directory name
        job_title_clean = job_title.lower().replace(' ', '_')
        
        # Create base folder structure with job_details subdirectory
        folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
        os.makedirs(folder_store, exist_ok=True)
        
        # Generate filename with date
        current_date = datetime.now().strftime('%Y%m%d')
        
        # Generate random 5-digit number
        random_number = str(random.randint(10000, 99999))
        
        # Construct the filename (all lowercase) without company name
        base_filename = f"{job_title_clean}_details_{current_date}_{random_number}"
        
        # Reorder columns to have job_id first
        cols = ['job_id'] + [col for col in df.columns if col != 'job_id']
        df = df[cols]
        
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

def process_job_links(links, output_dir, job_title):
    """Process job links in batches with appropriate delays."""
    try:
        # Initialize driver once
        driver = create_driver()
        load_cookies(driver, load_cookie_data())
        
        # Process in small batches
        batch_size = 3
        results = []
        
        for i in range(0, len(links), batch_size):
            batch = links[i:i + batch_size]
            logging.info(f"Processing batch {i//batch_size + 1} of {(len(links) + batch_size - 1)//batch_size}")
            
            # Process each URL in the batch
            for url in batch:
                try:
                    job_details = get_job_details(driver, url)
                    if job_details:
                        results.append(job_details)
                except Exception as e:
                    logging.error(f"Error processing URL {url}: {e}")
                    continue
                
                # Add delay between jobs within batch (5-10 seconds)
                time.sleep(random.uniform(5, 10))
            
            # Add longer delay between batches (20-30 seconds)
            if i + batch_size < len(links):
                delay = random.uniform(20, 30)
                logging.info(f"Taking a break between batches ({delay:.1f} seconds)...")
                time.sleep(delay)
        
        # Create results DataFrame
        df_results = pd.DataFrame(results, columns=[
            'job_title', 'company', 'description', 'date_posted',
            'location', 'remote', 'salary', 'job_url'
        ])
        
        # Save results in job_details directory
        job_title_clean = job_title.lower().replace(' ', '_')
        folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
        os.makedirs(folder_store, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{job_title_clean}_job_details_{timestamp}.csv"
        output_path = os.path.join(folder_store, output_filename)
        
        # Save both CSV and JSON
        df_results.to_csv(output_path, index=False)
        logging.info(f"Results saved to {output_path}")
        
        # Save JSON version
        json_path = output_path.replace('.csv', '.json')
        output_data = {
            "metadata": {
                "job_title": job_title_clean,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_jobs": len(df_results)
            },
            "jobs": df_results.to_dict('records')
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        logging.info(f"Results saved to {json_path}")
        
        return df_results
        
    except Exception as e:
        logging.error(f"Error in process_job_links: {e}")
        return pd.DataFrame()
    finally:
        try:
            cleanup_driver(driver)
        except:
            pass

def main(job_title, input_filename):
    """Main function with cleaned job title."""
    driver = None
    try:
        # Clean job title
        job_title_clean = job_title.lower().replace(' ', '_')
        
        # Initialize metrics tracker
        metrics_tracker = JobMetricsTracker()
        
        # Load job links from input file
        logging.info(f"Loading job links from {input_filename}")
        df, links = load_job_links(input_filename)
        if not links:
            logging.warning("No job links found to process.")
            return

        # Initialize driver
        logging.info("Initializing Chrome driver...")
        driver = create_driver()
        
        try:
            # Load cookies
            logging.info("Loading cookies...")
            cookies = load_cookie_data()
            if cookies:
                load_cookies(driver, cookies)
            else:
                logging.warning("No cookies loaded")
            
            # Process job links and collect detailed information
            logging.info("Starting to process job links...")
            detailed_jobs = []
            for link in links:
                job_details = get_job_details(driver, link)
                if job_details:
                    # Convert tuple to dictionary
                    job_dict = {
                        'job_title': job_details[0],
                        'company': job_details[1],
                        'description': job_details[2],
                        'date_posted': job_details[3],
                        'location': job_details[4],
                        'remote': job_details[5],
                        'salary': job_details[6],
                        'job_url': job_details[7]
                    }
                    detailed_jobs.append(job_dict)
            
            # Create DataFrame from detailed jobs
            if detailed_jobs:
                df_results = pd.DataFrame(detailed_jobs)
                
                # Save to job details directory
                folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
                os.makedirs(folder_store, exist_ok=True)
                
                # Generate filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = f"{job_title_clean}_job_details_{timestamp}.csv"
                output_path = os.path.join(folder_store, output_filename)
                
                # Save CSV
                df_results.to_csv(output_path, index=False)
                logging.info(f"Results saved to {output_path}")
                
                # Save JSON version
                json_path = output_path.replace('.csv', '.json')
                output_data = {
                    "metadata": {
                        "job_title": job_title_clean,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "total_jobs": len(df_results)
                    },
                    "jobs": df_results.to_dict('records')
                }
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                logging.info(f"Results saved to {json_path}")
                
                # Update metrics
                metrics_tracker.update_jobs_aggregation(
                    job_title=job_title,
                    new_jobs=detailed_jobs
                )
            
        finally:
            if driver:
                logging.info("Closing Chrome driver...")
                cleanup_driver(driver)
                
    except Exception as e:
        logging.error(f"Error in main processing: {str(e)}")
        if driver:
            try:
                cleanup_driver(driver)
            except:
                pass
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_title", required=True)
    parser.add_argument("--filename", required=True)
    args = parser.parse_args()
    
    main(args.job_title, args.filename)

```

```python
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
from job_metrics_tracker import JobMetricsTracker
import uuid
import shutil
from driver_utils import create_driver, cleanup_driver

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
    """Get details for a single job posting."""
    max_retries = 2  # Reduced retries since we're using batch processing
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logging.info(f"Processing URL: {url}")
            
            # Initial page load with delay
            driver.get(url)
            time.sleep(random.uniform(3, 5))
            
            wait = WebDriverWait(driver, 15)
            
            # Initialize variables
            job_title = company_name = job_description = date_posted = location = salary = remote_status = days_since_posted = None
            
            # Extract job details with minimal delays
            try:
                show_more_button = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '.feed-shared-inline-show-more-text__see-more-less-toggle')))
                driver.execute_script("arguments[0].click();", show_more_button)
            except Exception as e:
                logging.warning(f"Show more button not found: {e}")
            
            # Extract all fields with appropriate waits
            job_title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1'))).text.strip()
            
            try:
                job_description_element = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-about-the-job-module__description div.feed-shared-inline-show-more-text')))
                job_description = job_description_element.text.replace("-", " ").strip()
                job_description = re.sub(r'\s+', ' ', job_description)
            except:
                job_description = "-"
                
            try:
                company_name = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__company-name a'))).text.strip()
            except:
                company_name = "-"
                
            try:
                # Target the tertiary description container where date info is located
                tertiary_container = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__tertiary-description-container')))
                
                # Find spans that contain "Reposted" or "Posted" followed by time information
                date_text = None
                spans = tertiary_container.find_elements(By.CSS_SELECTOR, 'span.tvm__text.tvm__text--low-emphasis')
                
                for span in spans:
                    span_text = span.text.strip()
                    # Check if this span contains date-related keywords
                    if 'Reposted' in span_text or 'Posted' in span_text:
                        # Get the full text including nested spans
                        date_text = span_text
                        break
                
                if date_text:
                    date_posted = parse_date_posted(date_text)
                else:
                    date_posted = None
            except Exception as e:
                logging.warning(f"Could not extract date posted: {e}")
                date_posted = None
                
            try:
                location = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__primary-description-container span.tvm__text'))).text.strip()
            except:
                location = "-"
                
            try:
                salary = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.job-details-preferences-and-skills__pill span.ui-label.text-body-small"))).text.strip()
            except:
                salary = "-"
                
            try:
                # Look for the job-details-fit-level-preferences container first
                preferences_container = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.job-details-fit-level-preferences")))
                
                # Find buttons within the container that contain location type text
                buttons = preferences_container.find_elements(By.TAG_NAME, "button")
                remote_status = "Onsite"  # Default fallback
                
                for button in buttons:
                    button_text = button.text.strip()
                    # Check if button contains location type keywords
                    if any(keyword in button_text for keyword in ["Remote", "Hybrid", "Onsite"]):
                        # Extract just the location type (may have other text like "Full-time")
                        if "Remote" in button_text:
                            remote_status = "Remote"
                            break
                        elif "Hybrid" in button_text:
                            remote_status = "Hybrid"
                            break
                        elif "Onsite" in button_text:
                            remote_status = "Onsite"
                            break
                
            except Exception as e:
                logging.warning(f"Could not extract remote status: {e}")
                remote_status = "Onsite"
            
            return job_title, company_name, job_description, date_posted, location, remote_status, salary, url
            
        except Exception as e:
            retry_count += 1
            logging.warning(f"Attempt {retry_count} failed for URL {url}: {e}")
            if retry_count < max_retries:
                time.sleep(random.uniform(5, 8))
            else:
                logging.error(f"Failed to retrieve details after {max_retries} attempts")
                return "-", "-", "-", None, "-", "Onsite", "-", url

def parse_date_posted(date_text):
    """Parse the date posted text into a timestamp."""
    try:
        today = pd.Timestamp('today')
        if 'hour' in date_text:
            hours = int(re.search(r'(\d+)\s*hour', date_text).group(1))
            return today - pd.Timedelta(hours=hours)
        elif 'day' in date_text:
            days = int(re.search(r'(\d+)\s*day', date_text).group(1))
            return today - pd.Timedelta(days=days)
        elif 'week' in date_text:
            weeks = int(re.search(r'(\d+)\s*week', date_text).group(1))
            return today - pd.Timedelta(weeks=weeks)
        elif 'month' in date_text:
            months = int(re.search(r'(\d+)\s*month', date_text).group(1))
            return today - pd.DateOffset(months=months)
    except Exception as e:
        logging.warning(f"Could not parse date: {date_text} - {e}")
        return None

def calculate_days_since_posted(date_posted):
    """Calculate the number of days between the extraction date and the posting date."""
    if date_posted is None:
        return None
    try:
        today = pd.Timestamp('today').normalize()
        posted_date = pd.Timestamp(date_posted).normalize()
        days_diff = (today - posted_date).days
        return days_diff
    except Exception as e:
        logging.warning(f"Could not calculate days since posted: {e}")
        return None

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

def generate_unique_id():
    """Generate a unique ID using UUID4."""
    return str(uuid.uuid4())

def save_job_details(df, job_title):
    """Save job details with updated directory and formatting."""
    try:
        # Add unique IDs to each job record
        df['job_id'] = [generate_unique_id() for _ in range(len(df))]
        
        # Clean job title for directory name
        job_title_clean = job_title.lower().replace(' ', '_')
        
        # Create base folder structure with job_details subdirectory
        folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
        os.makedirs(folder_store, exist_ok=True)
        
        # Generate filename with date
        current_date = datetime.now().strftime('%Y%m%d')
        
        # Generate random 5-digit number
        random_number = str(random.randint(10000, 99999))
        
        # Construct the filename (all lowercase) without company name
        base_filename = f"{job_title_clean}_details_{current_date}_{random_number}"
        
        # Reorder columns to have job_id first
        cols = ['job_id'] + [col for col in df.columns if col != 'job_id']
        df = df[cols]
        
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

def process_job_links(links, output_dir, job_title):
    """Process job links in batches with appropriate delays."""
    try:
        # Initialize driver once
        driver = create_driver()
        load_cookies(driver, load_cookie_data())
        
        # Process in small batches
        batch_size = 3
        results = []
        
        for i in range(0, len(links), batch_size):
            batch = links[i:i + batch_size]
            logging.info(f"Processing batch {i//batch_size + 1} of {(len(links) + batch_size - 1)//batch_size}")
            
            # Process each URL in the batch
            for url in batch:
                try:
                    job_details = get_job_details(driver, url)
                    if job_details:
                        results.append(job_details)
                except Exception as e:
                    logging.error(f"Error processing URL {url}: {e}")
                    continue
                
                # Add delay between jobs within batch (5-10 seconds)
                time.sleep(random.uniform(5, 10))
            
            # Add longer delay between batches (20-30 seconds)
            if i + batch_size < len(links):
                delay = random.uniform(20, 30)
                logging.info(f"Taking a break between batches ({delay:.1f} seconds)...")
                time.sleep(delay)
        
        # Create results DataFrame
        df_results = pd.DataFrame(results, columns=[
            'job_title', 'company', 'description', 'date_posted',
            'location', 'remote', 'salary', 'job_url'
        ])
        
        # Save results in job_details directory
        job_title_clean = job_title.lower().replace(' ', '_')
        folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
        os.makedirs(folder_store, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{job_title_clean}_job_details_{timestamp}.csv"
        output_path = os.path.join(folder_store, output_filename)
        
        # Save both CSV and JSON
        df_results.to_csv(output_path, index=False)
        logging.info(f"Results saved to {output_path}")
        
        # Save JSON version
        json_path = output_path.replace('.csv', '.json')
        output_data = {
            "metadata": {
                "job_title": job_title_clean,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_jobs": len(df_results)
            },
            "jobs": df_results.to_dict('records')
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        logging.info(f"Results saved to {json_path}")
        
        return df_results
        
    except Exception as e:
        logging.error(f"Error in process_job_links: {e}")
        return pd.DataFrame()
    finally:
        try:
            cleanup_driver(driver)
        except:
            pass

def main(job_title, input_filename):
    """Main function with cleaned job title."""
    driver = None
    try:
        # Clean job title
        job_title_clean = job_title.lower().replace(' ', '_')
        
        # Initialize metrics tracker
        metrics_tracker = JobMetricsTracker()
        
        # Load job links from input file
        logging.info(f"Loading job links from {input_filename}")
        df, links = load_job_links(input_filename)
        if not links:
            logging.warning("No job links found to process.")
            return

        # Initialize driver
        logging.info("Initializing Chrome driver...")
        driver = create_driver()
        
        try:
            # Load cookies
            logging.info("Loading cookies...")
            cookies = load_cookie_data()
            if cookies:
                load_cookies(driver, cookies)
            else:
                logging.warning("No cookies loaded")
            
            # Process job links and collect detailed information
            logging.info("Starting to process job links...")
            detailed_jobs = []
            for link in links:
                job_details = get_job_details(driver, link)
                if job_details:
                    # Convert tuple to dictionary
                    job_dict = {
                        'job_title': job_details[0],
                        'company': job_details[1],
                        'description': job_details[2],
                        'date_posted': job_details[3],
                        'location': job_details[4],
                        'remote': job_details[5],
                        'salary': job_details[6],
                        'job_url': job_details[7]
                    }
                    detailed_jobs.append(job_dict)
            
            # Create DataFrame from detailed jobs
            if detailed_jobs:
                df_results = pd.DataFrame(detailed_jobs)
                
                # Save to job details directory
                folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
                os.makedirs(folder_store, exist_ok=True)
                
                # Generate filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = f"{job_title_clean}_job_details_{timestamp}.csv"
                output_path = os.path.join(folder_store, output_filename)
                
                # Save CSV
                df_results.to_csv(output_path, index=False)
                logging.info(f"Results saved to {output_path}")
                
                # Save JSON version
                json_path = output_path.replace('.csv', '.json')
                output_data = {
                    "metadata": {
                        "job_title": job_title_clean,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "total_jobs": len(df_results)
                    },
                    "jobs": df_results.to_dict('records')
                }
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                logging.info(f"Results saved to {json_path}")
                
                # Update metrics
                metrics_tracker.update_jobs_aggregation(
                    job_title=job_title,
                    new_jobs=detailed_jobs
                )
            
        finally:
            if driver:
                logging.info("Closing Chrome driver...")
                cleanup_driver(driver)
                
    except Exception as e:
        logging.error(f"Error in main processing: {str(e)}")
        if driver:
            try:
                cleanup_driver(driver)
            except:
                pass
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_title", required=True)
    parser.add_argument("--filename", required=True)
    args = parser.parse_args()
    
    main(args.job_title, args.filename)

```

```python
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
from job_metrics_tracker import JobMetricsTracker
import uuid
import shutil
from driver_utils import create_driver, cleanup_driver

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
    """Get details for a single job posting."""
    max_retries = 2  # Reduced retries since we're using batch processing
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logging.info(f"Processing URL: {url}")
            
            # Initial page load with delay
            driver.get(url)
            time.sleep(random.uniform(3, 5))
            
            wait = WebDriverWait(driver, 15)
            
            # Initialize variables
            job_title = company_name = job_description = date_posted = location = salary = remote_status = days_since_posted = None
            
            # Extract job details with minimal delays
            try:
                show_more_button = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '.feed-shared-inline-show-more-text__see-more-less-toggle')))
                driver.execute_script("arguments[0].click();", show_more_button)
            except Exception as e:
                logging.warning(f"Show more button not found: {e}")
            
            # Extract all fields with appropriate waits
            job_title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1'))).text.strip()
            
            try:
                job_description_element = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-about-the-job-module__description div.feed-shared-inline-show-more-text')))
                job_description = job_description_element.text.replace("-", " ").strip()
                job_description = re.sub(r'\s+', ' ', job_description)
            except:
                job_description = "-"
                
            try:
                company_name = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__company-name a'))).text.strip()
            except:
                company_name = "-"
                
            try:
                # Target the tertiary description container where date info is located
                tertiary_container = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__tertiary-description-container')))
                
                # Find spans that contain "Reposted" or "Posted" followed by time information
                date_text = None
                spans = tertiary_container.find_elements(By.CSS_SELECTOR, 'span.tvm__text.tvm__text--low-emphasis')
                
                for span in spans:
                    span_text = span.text.strip()
                    # Check if this span contains date-related keywords
                    if 'Reposted' in span_text or 'Posted' in span_text:
                        # Get the full text including nested spans
                        date_text = span_text
                        break
                
                if date_text:
                    date_posted = parse_date_posted(date_text)
                    # Calculate days since posted
                    days_since_posted = calculate_days_since_posted(date_posted)
                else:
                    date_posted = None
                    days_since_posted = None
            except Exception as e:
                logging.warning(f"Could not extract date posted: {e}")
                date_posted = None
                days_since_posted = None
                
            try:
                location = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__primary-description-container span.tvm__text'))).text.strip()
            except:
                location = "-"
                
            try:
                salary = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.job-details-preferences-and-skills__pill span.ui-label.text-body-small"))).text.strip()
            except:
                salary = "-"
                
            try:
                # Look for the job-details-fit-level-preferences container first
                preferences_container = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.job-details-fit-level-preferences")))
                
                # Find buttons within the container that contain location type text
                buttons = preferences_container.find_elements(By.TAG_NAME, "button")
                remote_status = "Onsite"  # Default fallback
                
                for button in buttons:
                    button_text = button.text.strip()
                    # Check if button contains location type keywords
                    if any(keyword in button_text for keyword in ["Remote", "Hybrid", "Onsite"]):
                        # Extract just the location type (may have other text like "Full-time")
                        if "Remote" in button_text:
                            remote_status = "Remote"
                            break
                        elif "Hybrid" in button_text:
                            remote_status = "Hybrid"
                            break
                        elif "Onsite" in button_text:
                            remote_status = "Onsite"
                            break
                
            except Exception as e:
                logging.warning(f"Could not extract remote status: {e}")
                remote_status = "Onsite"
            
            return job_title, company_name, job_description, date_posted, location, remote_status, salary, url
            
        except Exception as e:
            retry_count += 1
            logging.warning(f"Attempt {retry_count} failed for URL {url}: {e}")
            if retry_count < max_retries:
                time.sleep(random.uniform(5, 8))
            else:
                logging.error(f"Failed to retrieve details after {max_retries} attempts")
                return "-", "-", "-", None, "-", "Onsite", "-", url

def parse_date_posted(date_text):
    """Parse the date posted text into a timestamp."""
    try:
        today = pd.Timestamp('today')
        if 'hour' in date_text:
            hours = int(re.search(r'(\d+)\s*hour', date_text).group(1))
            return today - pd.Timedelta(hours=hours)
        elif 'day' in date_text:
            days = int(re.search(r'(\d+)\s*day', date_text).group(1))
            return today - pd.Timedelta(days=days)
        elif 'week' in date_text:
            weeks = int(re.search(r'(\d+)\s*week', date_text).group(1))
            return today - pd.Timedelta(weeks=weeks)
        elif 'month' in date_text:
            months = int(re.search(r'(\d+)\s*month', date_text).group(1))
            return today - pd.DateOffset(months=months)
    except Exception as e:
        logging.warning(f"Could not parse date: {date_text} - {e}")
        return None

def calculate_days_since_posted(date_posted):
    """Calculate the number of days between the extraction date and the posting date."""
    if date_posted is None:
        return None
    try:
        today = pd.Timestamp('today').normalize()
        posted_date = pd.Timestamp(date_posted).normalize()
        days_diff = (today - posted_date).days
        return days_diff
    except Exception as e:
        logging.warning(f"Could not calculate days since posted: {e}")
        return None

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

def generate_unique_id():
    """Generate a unique ID using UUID4."""
    return str(uuid.uuid4())

def save_job_details(df, job_title):
    """Save job details with updated directory and formatting."""
    try:
        # Add unique IDs to each job record
        df['job_id'] = [generate_unique_id() for _ in range(len(df))]
        
        # Clean job title for directory name
        job_title_clean = job_title.lower().replace(' ', '_')
        
        # Create base folder structure with job_details subdirectory
        folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
        os.makedirs(folder_store, exist_ok=True)
        
        # Generate filename with date
        current_date = datetime.now().strftime('%Y%m%d')
        
        # Generate random 5-digit number
        random_number = str(random.randint(10000, 99999))
        
        # Construct the filename (all lowercase) without company name
        base_filename = f"{job_title_clean}_details_{current_date}_{random_number}"
        
        # Reorder columns to have job_id first
        cols = ['job_id'] + [col for col in df.columns if col != 'job_id']
        df = df[cols]
        
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

def process_job_links(links, output_dir, job_title):
    """Process job links in batches with appropriate delays."""
    try:
        # Initialize driver once
        driver = create_driver()
        load_cookies(driver, load_cookie_data())
        
        # Process in small batches
        batch_size = 3
        results = []
        
        for i in range(0, len(links), batch_size):
            batch = links[i:i + batch_size]
            logging.info(f"Processing batch {i//batch_size + 1} of {(len(links) + batch_size - 1)//batch_size}")
            
            # Process each URL in the batch
            for url in batch:
                try:
                    job_details = get_job_details(driver, url)
                    if job_details:
                        results.append(job_details)
                except Exception as e:
                    logging.error(f"Error processing URL {url}: {e}")
                    continue
                
                # Add delay between jobs within batch (5-10 seconds)
                time.sleep(random.uniform(5, 10))
            
            # Add longer delay between batches (20-30 seconds)
            if i + batch_size < len(links):
                delay = random.uniform(20, 30)
                logging.info(f"Taking a break between batches ({delay:.1f} seconds)...")
                time.sleep(delay)
        
        # Create results DataFrame
        df_results = pd.DataFrame(results, columns=[
            'job_title', 'company', 'description', 'date_posted',
            'location', 'remote', 'salary', 'job_url'
        ])
        
        # Save results in job_details directory
        job_title_clean = job_title.lower().replace(' ', '_')
        folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
        os.makedirs(folder_store, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{job_title_clean}_job_details_{timestamp}.csv"
        output_path = os.path.join(folder_store, output_filename)
        
        # Save both CSV and JSON
        df_results.to_csv(output_path, index=False)
        logging.info(f"Results saved to {output_path}")
        
        # Save JSON version
        json_path = output_path.replace('.csv', '.json')
        output_data = {
            "metadata": {
                "job_title": job_title_clean,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_jobs": len(df_results)
            },
            "jobs": df_results.to_dict('records')
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        logging.info(f"Results saved to {json_path}")
        
        return df_results
        
    except Exception as e:
        logging.error(f"Error in process_job_links: {e}")
        return pd.DataFrame()
    finally:
        try:
            cleanup_driver(driver)
        except:
            pass

def main(job_title, input_filename):
    """Main function with cleaned job title."""
    driver = None
    try:
        # Clean job title
        job_title_clean = job_title.lower().replace(' ', '_')
        
        # Initialize metrics tracker
        metrics_tracker = JobMetricsTracker()
        
        # Load job links from input file
        logging.info(f"Loading job links from {input_filename}")
        df, links = load_job_links(input_filename)
        if not links:
            logging.warning("No job links found to process.")
            return

        # Initialize driver
        logging.info("Initializing Chrome driver...")
        driver = create_driver()
        
        try:
            # Load cookies
            logging.info("Loading cookies...")
            cookies = load_cookie_data()
            if cookies:
                load_cookies(driver, cookies)
            else:
                logging.warning("No cookies loaded")
            
            # Process job links and collect detailed information
            logging.info("Starting to process job links...")
            detailed_jobs = []
            for link in links:
                job_details = get_job_details(driver, link)
                if job_details:
                    # Convert tuple to dictionary
                    job_dict = {
                        'job_title': job_details[0],
                        'company': job_details[1],
                        'description': job_details[2],
                        'date_posted': job_details[3],
                        'location': job_details[4],
                        'remote': job_details[5],
                        'salary': job_details[6],
                        'job_url': job_details[7]
                    }
                    detailed_jobs.append(job_dict)
            
            # Create DataFrame from detailed jobs
            if detailed_jobs:
                df_results = pd.DataFrame(detailed_jobs)
                
                # Save to job details directory
                folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
                os.makedirs(folder_store, exist_ok=True)
                
                # Generate filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = f"{job_title_clean}_job_details_{timestamp}.csv"
                output_path = os.path.join(folder_store, output_filename)
                
                # Save CSV
                df_results.to_csv(output_path, index=False)
                logging.info(f"Results saved to {output_path}")
                
                # Save JSON version
                json_path = output_path.replace('.csv', '.json')
                output_data = {
                    "metadata": {
                        "job_title": job_title_clean,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "total_jobs": len(df_results)
                    },
                    "jobs": df_results.to_dict('records')
                }
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                logging.info(f"Results saved to {json_path}")
                
                # Update metrics
                metrics_tracker.update_jobs_aggregation(
                    job_title=job_title,
                    new_jobs=detailed_jobs
                )
            
        finally:
            if driver:
                logging.info("Closing Chrome driver...")
                cleanup_driver(driver)
                
    except Exception as e:
        logging.error(f"Error in main processing: {str(e)}")
        if driver:
            try:
                cleanup_driver(driver)
            except:
                pass
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_title", required=True)
    parser.add_argument("--filename", required=True)
    args = parser.parse_args()
    
    main(args.job_title, args.filename)

```

```python
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
from job_metrics_tracker import JobMetricsTracker
import uuid
import shutil
from driver_utils import create_driver, cleanup_driver

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
    """Get details for a single job posting."""
    max_retries = 2  # Reduced retries since we're using batch processing
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logging.info(f"Processing URL: {url}")
            
            # Initial page load with delay
            driver.get(url)
            time.sleep(random.uniform(3, 5))
            
            wait = WebDriverWait(driver, 15)
            
            # Initialize variables
            job_title = company_name = job_description = date_posted = location = salary = remote_status = days_since_posted = None
            
            # Extract job details with minimal delays
            try:
                show_more_button = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '.feed-shared-inline-show-more-text__see-more-less-toggle')))
                driver.execute_script("arguments[0].click();", show_more_button)
            except Exception as e:
                logging.warning(f"Show more button not found: {e}")
            
            # Extract all fields with appropriate waits
            job_title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1'))).text.strip()
            
            try:
                job_description_element = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-about-the-job-module__description div.feed-shared-inline-show-more-text')))
                job_description = job_description_element.text.replace("-", " ").strip()
                job_description = re.sub(r'\s+', ' ', job_description)
            except:
                job_description = "-"
                
            try:
                company_name = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__company-name a'))).text.strip()
            except:
                company_name = "-"
                
            try:
                # Target the tertiary description container where date info is located
                tertiary_container = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__tertiary-description-container')))
                
                # Find spans that contain "Reposted" or "Posted" followed by time information
                date_text = None
                spans = tertiary_container.find_elements(By.CSS_SELECTOR, 'span.tvm__text.tvm__text--low-emphasis')
                
                for span in spans:
                    span_text = span.text.strip()
                    # Check if this span contains date-related keywords
                    if 'Reposted' in span_text or 'Posted' in span_text:
                        # Get the full text including nested spans
                        date_text = span_text
                        break
                
                if date_text:
                    date_posted = parse_date_posted(date_text)
                    # Calculate days since posted
                    days_since_posted = calculate_days_since_posted(date_posted)
                else:
                    date_posted = None
                    days_since_posted = None
            except Exception as e:
                logging.warning(f"Could not extract date posted: {e}")
                date_posted = None
                days_since_posted = None
                
            try:
                location = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__primary-description-container span.tvm__text'))).text.strip()
            except:
                location = "-"
                
            try:
                salary = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.job-details-preferences-and-skills__pill span.ui-label.text-body-small"))).text.strip()
            except:
                salary = "-"
                
            try:
                # Look for the job-details-fit-level-preferences container first
                preferences_container = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.job-details-fit-level-preferences")))
                
                # Find buttons within the container that contain location type text
                buttons = preferences_container.find_elements(By.TAG_NAME, "button")
                remote_status = "Onsite"  # Default fallback
                
                for button in buttons:
                    button_text = button.text.strip()
                    # Check if button contains location type keywords
                    if any(keyword in button_text for keyword in ["Remote", "Hybrid", "Onsite"]):
                        # Extract just the location type (may have other text like "Full-time")
                        if "Remote" in button_text:
                            remote_status = "Remote"
                            break
                        elif "Hybrid" in button_text:
                            remote_status = "Hybrid"
                            break
                        elif "Onsite" in button_text:
                            remote_status = "Onsite"
                            break
                
            except Exception as e:
                logging.warning(f"Could not extract remote status: {e}")
                remote_status = "Onsite"
            
            return job_title, company_name, job_description, date_posted, location, remote_status, salary, url, days_since_posted
            
        except Exception as e:
            retry_count += 1
            logging.warning(f"Attempt {retry_count} failed for URL {url}: {e}")
            if retry_count < max_retries:
                time.sleep(random.uniform(5, 8))
            else:
                logging.error(f"Failed to retrieve details after {max_retries} attempts")
                return "-", "-", "-", None, "-", "Onsite", "-", url

def parse_date_posted(date_text):
    """Parse the date posted text into a timestamp."""
    try:
        today = pd.Timestamp('today')
        if 'hour' in date_text:
            hours = int(re.search(r'(\d+)\s*hour', date_text).group(1))
            return today - pd.Timedelta(hours=hours)
        elif 'day' in date_text:
            days = int(re.search(r'(\d+)\s*day', date_text).group(1))
            return today - pd.Timedelta(days=days)
        elif 'week' in date_text:
            weeks = int(re.search(r'(\d+)\s*week', date_text).group(1))
            return today - pd.Timedelta(weeks=weeks)
        elif 'month' in date_text:
            months = int(re.search(r'(\d+)\s*month', date_text).group(1))
            return today - pd.DateOffset(months=months)
    except Exception as e:
        logging.warning(f"Could not parse date: {date_text} - {e}")
        return None

def calculate_days_since_posted(date_posted):
    """Calculate the number of days between the extraction date and the posting date."""
    if date_posted is None:
        return None
    try:
        today = pd.Timestamp('today').normalize()
        posted_date = pd.Timestamp(date_posted).normalize()
        days_diff = (today - posted_date).days
        return days_diff
    except Exception as e:
        logging.warning(f"Could not calculate days since posted: {e}")
        return None

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

def generate_unique_id():
    """Generate a unique ID using UUID4."""
    return str(uuid.uuid4())

def save_job_details(df, job_title):
    """Save job details with updated directory and formatting."""
    try:
        # Add unique IDs to each job record
        df['job_id'] = [generate_unique_id() for _ in range(len(df))]
        
        # Clean job title for directory name
        job_title_clean = job_title.lower().replace(' ', '_')
        
        # Create base folder structure with job_details subdirectory
        folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
        os.makedirs(folder_store, exist_ok=True)
        
        # Generate filename with date
        current_date = datetime.now().strftime('%Y%m%d')
        
        # Generate random 5-digit number
        random_number = str(random.randint(10000, 99999))
        
        # Construct the filename (all lowercase) without company name
        base_filename = f"{job_title_clean}_details_{current_date}_{random_number}"
        
        # Reorder columns to have job_id first
        cols = ['job_id'] + [col for col in df.columns if col != 'job_id']
        df = df[cols]
        
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

def process_job_links(links, output_dir, job_title):
    """Process job links in batches with appropriate delays."""
    try:
        # Initialize driver once
        driver = create_driver()
        load_cookies(driver, load_cookie_data())
        
        # Process in small batches
        batch_size = 3
        results = []
        
        for i in range(0, len(links), batch_size):
            batch = links[i:i + batch_size]
            logging.info(f"Processing batch {i//batch_size + 1} of {(len(links) + batch_size - 1)//batch_size}")
            
            # Process each URL in the batch
            for url in batch:
                try:
                    job_details = get_job_details(driver, url)
                    if job_details:
                        results.append(job_details)
                except Exception as e:
                    logging.error(f"Error processing URL {url}: {e}")
                    continue
                
                # Add delay between jobs within batch (5-10 seconds)
                time.sleep(random.uniform(5, 10))
            
            # Add longer delay between batches (20-30 seconds)
            if i + batch_size < len(links):
                delay = random.uniform(20, 30)
                logging.info(f"Taking a break between batches ({delay:.1f} seconds)...")
                time.sleep(delay)
        
        # Create results DataFrame
        df_results = pd.DataFrame(results, columns=[
            'job_title', 'company', 'description', 'date_posted',
            'location', 'remote', 'salary', 'job_url'
        ])
        
        # Save results in job_details directory
        job_title_clean = job_title.lower().replace(' ', '_')
        folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
        os.makedirs(folder_store, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{job_title_clean}_job_details_{timestamp}.csv"
        output_path = os.path.join(folder_store, output_filename)
        
        # Save both CSV and JSON
        df_results.to_csv(output_path, index=False)
        logging.info(f"Results saved to {output_path}")
        
        # Save JSON version
        json_path = output_path.replace('.csv', '.json')
        output_data = {
            "metadata": {
                "job_title": job_title_clean,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_jobs": len(df_results)
            },
            "jobs": df_results.to_dict('records')
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        logging.info(f"Results saved to {json_path}")
        
        return df_results
        
    except Exception as e:
        logging.error(f"Error in process_job_links: {e}")
        return pd.DataFrame()
    finally:
        try:
            cleanup_driver(driver)
        except:
            pass

def main(job_title, input_filename):
    """Main function with cleaned job title."""
    driver = None
    try:
        # Clean job title
        job_title_clean = job_title.lower().replace(' ', '_')
        
        # Initialize metrics tracker
        metrics_tracker = JobMetricsTracker()
        
        # Load job links from input file
        logging.info(f"Loading job links from {input_filename}")
        df, links = load_job_links(input_filename)
        if not links:
            logging.warning("No job links found to process.")
            return

        # Initialize driver
        logging.info("Initializing Chrome driver...")
        driver = create_driver()
        
        try:
            # Load cookies
            logging.info("Loading cookies...")
            cookies = load_cookie_data()
            if cookies:
                load_cookies(driver, cookies)
            else:
                logging.warning("No cookies loaded")
            
            # Process job links and collect detailed information
            logging.info("Starting to process job links...")
            detailed_jobs = []
            for link in links:
                job_details = get_job_details(driver, link)
                if job_details:
                    # Convert tuple to dictionary
                    job_dict = {
                        'job_title': job_details[0],
                        'company': job_details[1],
                        'description': job_details[2],
                        'date_posted': job_details[3],
                        'location': job_details[4],
                        'remote': job_details[5],
                        'salary': job_details[6],
                        'job_url': job_details[7]
                    }
                    detailed_jobs.append(job_dict)
            
            # Create DataFrame from detailed jobs
            if detailed_jobs:
                df_results = pd.DataFrame(detailed_jobs)
                
                # Save to job details directory
                folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
                os.makedirs(folder_store, exist_ok=True)
                
                # Generate filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = f"{job_title_clean}_job_details_{timestamp}.csv"
                output_path = os.path.join(folder_store, output_filename)
                
                # Save CSV
                df_results.to_csv(output_path, index=False)
                logging.info(f"Results saved to {output_path}")
                
                # Save JSON version
                json_path = output_path.replace('.csv', '.json')
                output_data = {
                    "metadata": {
                        "job_title": job_title_clean,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "total_jobs": len(df_results)
                    },
                    "jobs": df_results.to_dict('records')
                }
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                logging.info(f"Results saved to {json_path}")
                
                # Update metrics
                metrics_tracker.update_jobs_aggregation(
                    job_title=job_title,
                    new_jobs=detailed_jobs
                )
            
        finally:
            if driver:
                logging.info("Closing Chrome driver...")
                cleanup_driver(driver)
                
    except Exception as e:
        logging.error(f"Error in main processing: {str(e)}")
        if driver:
            try:
                cleanup_driver(driver)
            except:
                pass
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_title", required=True)
    parser.add_argument("--filename", required=True)
    args = parser.parse_args()
    
    main(args.job_title, args.filename)

```

```python
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
from job_metrics_tracker import JobMetricsTracker
import uuid
import shutil
from driver_utils import create_driver, cleanup_driver

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
    """Get details for a single job posting."""
    max_retries = 2  # Reduced retries since we're using batch processing
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logging.info(f"Processing URL: {url}")
            
            # Initial page load with delay
            driver.get(url)
            time.sleep(random.uniform(3, 5))
            
            wait = WebDriverWait(driver, 15)
            
            # Initialize variables
            job_title = company_name = job_description = date_posted = location = salary = remote_status = days_since_posted = None
            
            # Extract job details with minimal delays
            try:
                show_more_button = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '.feed-shared-inline-show-more-text__see-more-less-toggle')))
                driver.execute_script("arguments[0].click();", show_more_button)
            except Exception as e:
                logging.warning(f"Show more button not found: {e}")
            
            # Extract all fields with appropriate waits
            job_title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1'))).text.strip()
            
            try:
                job_description_element = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-about-the-job-module__description div.feed-shared-inline-show-more-text')))
                job_description = job_description_element.text.replace("-", " ").strip()
                job_description = re.sub(r'\s+', ' ', job_description)
            except:
                job_description = "-"
                
            try:
                company_name = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__company-name a'))).text.strip()
            except:
                company_name = "-"
                
            try:
                # Target the tertiary description container where date info is located
                tertiary_container = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__tertiary-description-container')))
                
                # Find spans that contain "Reposted" or "Posted" followed by time information
                date_text = None
                spans = tertiary_container.find_elements(By.CSS_SELECTOR, 'span.tvm__text.tvm__text--low-emphasis')
                
                for span in spans:
                    span_text = span.text.strip()
                    # Check if this span contains date-related keywords
                    if 'Reposted' in span_text or 'Posted' in span_text:
                        # Get the full text including nested spans
                        date_text = span_text
                        break
                
                if date_text:
                    date_posted = parse_date_posted(date_text)
                    # Calculate days since posted
                    days_since_posted = calculate_days_since_posted(date_posted)
                else:
                    date_posted = None
                    days_since_posted = None
            except Exception as e:
                logging.warning(f"Could not extract date posted: {e}")
                date_posted = None
                days_since_posted = None
                
            try:
                location = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__primary-description-container span.tvm__text'))).text.strip()
            except:
                location = "-"
                
            try:
                salary = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.job-details-preferences-and-skills__pill span.ui-label.text-body-small"))).text.strip()
            except:
                salary = "-"
                
            try:
                # Look for the job-details-fit-level-preferences container first
                preferences_container = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.job-details-fit-level-preferences")))
                
                # Find buttons within the container that contain location type text
                buttons = preferences_container.find_elements(By.TAG_NAME, "button")
                remote_status = "Onsite"  # Default fallback
                
                for button in buttons:
                    button_text = button.text.strip()
                    # Check if button contains location type keywords
                    if any(keyword in button_text for keyword in ["Remote", "Hybrid", "Onsite"]):
                        # Extract just the location type (may have other text like "Full-time")
                        if "Remote" in button_text:
                            remote_status = "Remote"
                            break
                        elif "Hybrid" in button_text:
                            remote_status = "Hybrid"
                            break
                        elif "Onsite" in button_text:
                            remote_status = "Onsite"
                            break
                
            except Exception as e:
                logging.warning(f"Could not extract remote status: {e}")
                remote_status = "Onsite"
            
            return job_title, company_name, job_description, date_posted, location, remote_status, salary, url, days_since_posted
            
        except Exception as e:
            retry_count += 1
            logging.warning(f"Attempt {retry_count} failed for URL {url}: {e}")
            if retry_count < max_retries:
                time.sleep(random.uniform(5, 8))
            else:
                logging.error(f"Failed to retrieve details after {max_retries} attempts")
                return "-", "-", "-", None, "-", "Onsite", "-", url, None

def parse_date_posted(date_text):
    """Parse the date posted text into a timestamp."""
    try:
        today = pd.Timestamp('today')
        if 'hour' in date_text:
            hours = int(re.search(r'(\d+)\s*hour', date_text).group(1))
            return today - pd.Timedelta(hours=hours)
        elif 'day' in date_text:
            days = int(re.search(r'(\d+)\s*day', date_text).group(1))
            return today - pd.Timedelta(days=days)
        elif 'week' in date_text:
            weeks = int(re.search(r'(\d+)\s*week', date_text).group(1))
            return today - pd.Timedelta(weeks=weeks)
        elif 'month' in date_text:
            months = int(re.search(r'(\d+)\s*month', date_text).group(1))
            return today - pd.DateOffset(months=months)
    except Exception as e:
        logging.warning(f"Could not parse date: {date_text} - {e}")
        return None

def calculate_days_since_posted(date_posted):
    """Calculate the number of days between the extraction date and the posting date."""
    if date_posted is None:
        return None
    try:
        today = pd.Timestamp('today').normalize()
        posted_date = pd.Timestamp(date_posted).normalize()
        days_diff = (today - posted_date).days
        return days_diff
    except Exception as e:
        logging.warning(f"Could not calculate days since posted: {e}")
        return None

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

def generate_unique_id():
    """Generate a unique ID using UUID4."""
    return str(uuid.uuid4())

def save_job_details(df, job_title):
    """Save job details with updated directory and formatting."""
    try:
        # Add unique IDs to each job record
        df['job_id'] = [generate_unique_id() for _ in range(len(df))]
        
        # Clean job title for directory name
        job_title_clean = job_title.lower().replace(' ', '_')
        
        # Create base folder structure with job_details subdirectory
        folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
        os.makedirs(folder_store, exist_ok=True)
        
        # Generate filename with date
        current_date = datetime.now().strftime('%Y%m%d')
        
        # Generate random 5-digit number
        random_number = str(random.randint(10000, 99999))
        
        # Construct the filename (all lowercase) without company name
        base_filename = f"{job_title_clean}_details_{current_date}_{random_number}"
        
        # Reorder columns to have job_id first
        cols = ['job_id'] + [col for col in df.columns if col != 'job_id']
        df = df[cols]
        
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

def process_job_links(links, output_dir, job_title):
    """Process job links in batches with appropriate delays."""
    try:
        # Initialize driver once
        driver = create_driver()
        load_cookies(driver, load_cookie_data())
        
        # Process in small batches
        batch_size = 3
        results = []
        
        for i in range(0, len(links), batch_size):
            batch = links[i:i + batch_size]
            logging.info(f"Processing batch {i//batch_size + 1} of {(len(links) + batch_size - 1)//batch_size}")
            
            # Process each URL in the batch
            for url in batch:
                try:
                    job_details = get_job_details(driver, url)
                    if job_details:
                        results.append(job_details)
                except Exception as e:
                    logging.error(f"Error processing URL {url}: {e}")
                    continue
                
                # Add delay between jobs within batch (5-10 seconds)
                time.sleep(random.uniform(5, 10))
            
            # Add longer delay between batches (20-30 seconds)
            if i + batch_size < len(links):
                delay = random.uniform(20, 30)
                logging.info(f"Taking a break between batches ({delay:.1f} seconds)...")
                time.sleep(delay)
        
        # Create results DataFrame
        df_results = pd.DataFrame(results, columns=[
            'job_title', 'company', 'description', 'date_posted',
            'location', 'remote', 'salary', 'job_url'
        ])
        
        # Save results in job_details directory
        job_title_clean = job_title.lower().replace(' ', '_')
        folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
        os.makedirs(folder_store, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{job_title_clean}_job_details_{timestamp}.csv"
        output_path = os.path.join(folder_store, output_filename)
        
        # Save both CSV and JSON
        df_results.to_csv(output_path, index=False)
        logging.info(f"Results saved to {output_path}")
        
        # Save JSON version
        json_path = output_path.replace('.csv', '.json')
        output_data = {
            "metadata": {
                "job_title": job_title_clean,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_jobs": len(df_results)
            },
            "jobs": df_results.to_dict('records')
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        logging.info(f"Results saved to {json_path}")
        
        return df_results
        
    except Exception as e:
        logging.error(f"Error in process_job_links: {e}")
        return pd.DataFrame()
    finally:
        try:
            cleanup_driver(driver)
        except:
            pass

def main(job_title, input_filename):
    """Main function with cleaned job title."""
    driver = None
    try:
        # Clean job title
        job_title_clean = job_title.lower().replace(' ', '_')
        
        # Initialize metrics tracker
        metrics_tracker = JobMetricsTracker()
        
        # Load job links from input file
        logging.info(f"Loading job links from {input_filename}")
        df, links = load_job_links(input_filename)
        if not links:
            logging.warning("No job links found to process.")
            return

        # Initialize driver
        logging.info("Initializing Chrome driver...")
        driver = create_driver()
        
        try:
            # Load cookies
            logging.info("Loading cookies...")
            cookies = load_cookie_data()
            if cookies:
                load_cookies(driver, cookies)
            else:
                logging.warning("No cookies loaded")
            
            # Process job links and collect detailed information
            logging.info("Starting to process job links...")
            detailed_jobs = []
            for link in links:
                job_details = get_job_details(driver, link)
                if job_details:
                    # Convert tuple to dictionary
                    job_dict = {
                        'job_title': job_details[0],
                        'company': job_details[1],
                        'description': job_details[2],
                        'date_posted': job_details[3],
                        'location': job_details[4],
                        'remote': job_details[5],
                        'salary': job_details[6],
                        'job_url': job_details[7]
                    }
                    detailed_jobs.append(job_dict)
            
            # Create DataFrame from detailed jobs
            if detailed_jobs:
                df_results = pd.DataFrame(detailed_jobs)
                
                # Save to job details directory
                folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
                os.makedirs(folder_store, exist_ok=True)
                
                # Generate filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = f"{job_title_clean}_job_details_{timestamp}.csv"
                output_path = os.path.join(folder_store, output_filename)
                
                # Save CSV
                df_results.to_csv(output_path, index=False)
                logging.info(f"Results saved to {output_path}")
                
                # Save JSON version
                json_path = output_path.replace('.csv', '.json')
                output_data = {
                    "metadata": {
                        "job_title": job_title_clean,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "total_jobs": len(df_results)
                    },
                    "jobs": df_results.to_dict('records')
                }
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                logging.info(f"Results saved to {json_path}")
                
                # Update metrics
                metrics_tracker.update_jobs_aggregation(
                    job_title=job_title,
                    new_jobs=detailed_jobs
                )
            
        finally:
            if driver:
                logging.info("Closing Chrome driver...")
                cleanup_driver(driver)
                
    except Exception as e:
        logging.error(f"Error in main processing: {str(e)}")
        if driver:
            try:
                cleanup_driver(driver)
            except:
                pass
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_title", required=True)
    parser.add_argument("--filename", required=True)
    args = parser.parse_args()
    
    main(args.job_title, args.filename)

```

```python
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
from job_metrics_tracker import JobMetricsTracker
import uuid
import shutil
from driver_utils import create_driver, cleanup_driver

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
    """Get details for a single job posting."""
    max_retries = 2  # Reduced retries since we're using batch processing
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logging.info(f"Processing URL: {url}")
            
            # Initial page load with delay
            driver.get(url)
            time.sleep(random.uniform(3, 5))
            
            wait = WebDriverWait(driver, 15)
            
            # Initialize variables
            job_title = company_name = job_description = date_posted = location = salary = remote_status = days_since_posted = None
            
            # Extract job details with minimal delays
            try:
                show_more_button = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '.feed-shared-inline-show-more-text__see-more-less-toggle')))
                driver.execute_script("arguments[0].click();", show_more_button)
            except Exception as e:
                logging.warning(f"Show more button not found: {e}")
            
            # Extract all fields with appropriate waits
            job_title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1'))).text.strip()
            
            try:
                job_description_element = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-about-the-job-module__description div.feed-shared-inline-show-more-text')))
                job_description = job_description_element.text.replace("-", " ").strip()
                job_description = re.sub(r'\s+', ' ', job_description)
            except:
                job_description = "-"
                
            try:
                company_name = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__company-name a'))).text.strip()
            except:
                company_name = "-"
                
            try:
                # Target the tertiary description container where date info is located
                tertiary_container = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__tertiary-description-container')))
                
                # Find spans that contain "Reposted" or "Posted" followed by time information
                date_text = None
                spans = tertiary_container.find_elements(By.CSS_SELECTOR, 'span.tvm__text.tvm__text--low-emphasis')
                
                for span in spans:
                    span_text = span.text.strip()
                    # Check if this span contains date-related keywords
                    if 'Reposted' in span_text or 'Posted' in span_text:
                        # Get the full text including nested spans
                        date_text = span_text
                        break
                
                if date_text:
                    date_posted = parse_date_posted(date_text)
                    # Calculate days since posted
                    days_since_posted = calculate_days_since_posted(date_posted)
                else:
                    date_posted = None
                    days_since_posted = None
            except Exception as e:
                logging.warning(f"Could not extract date posted: {e}")
                date_posted = None
                days_since_posted = None
                
            try:
                location = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__primary-description-container span.tvm__text'))).text.strip()
            except:
                location = "-"
                
            try:
                salary = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.job-details-preferences-and-skills__pill span.ui-label.text-body-small"))).text.strip()
            except:
                salary = "-"
                
            try:
                # Look for the job-details-fit-level-preferences container first
                preferences_container = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.job-details-fit-level-preferences")))
                
                # Find buttons within the container that contain location type text
                buttons = preferences_container.find_elements(By.TAG_NAME, "button")
                remote_status = "Onsite"  # Default fallback
                
                for button in buttons:
                    button_text = button.text.strip()
                    # Check if button contains location type keywords
                    if any(keyword in button_text for keyword in ["Remote", "Hybrid", "Onsite"]):
                        # Extract just the location type (may have other text like "Full-time")
                        if "Remote" in button_text:
                            remote_status = "Remote"
                            break
                        elif "Hybrid" in button_text:
                            remote_status = "Hybrid"
                            break
                        elif "Onsite" in button_text:
                            remote_status = "Onsite"
                            break
                
            except Exception as e:
                logging.warning(f"Could not extract remote status: {e}")
                remote_status = "Onsite"
            
            return job_title, company_name, job_description, date_posted, location, remote_status, salary, url, days_since_posted
            
        except Exception as e:
            retry_count += 1
            logging.warning(f"Attempt {retry_count} failed for URL {url}: {e}")
            if retry_count < max_retries:
                time.sleep(random.uniform(5, 8))
            else:
                logging.error(f"Failed to retrieve details after {max_retries} attempts")
                return "-", "-", "-", None, "-", "Onsite", "-", url, None

def parse_date_posted(date_text):
    """Parse the date posted text into a timestamp."""
    try:
        today = pd.Timestamp('today')
        if 'hour' in date_text:
            hours = int(re.search(r'(\d+)\s*hour', date_text).group(1))
            return today - pd.Timedelta(hours=hours)
        elif 'day' in date_text:
            days = int(re.search(r'(\d+)\s*day', date_text).group(1))
            return today - pd.Timedelta(days=days)
        elif 'week' in date_text:
            weeks = int(re.search(r'(\d+)\s*week', date_text).group(1))
            return today - pd.Timedelta(weeks=weeks)
        elif 'month' in date_text:
            months = int(re.search(r'(\d+)\s*month', date_text).group(1))
            return today - pd.DateOffset(months=months)
    except Exception as e:
        logging.warning(f"Could not parse date: {date_text} - {e}")
        return None

def calculate_days_since_posted(date_posted):
    """Calculate the number of days between the extraction date and the posting date."""
    if date_posted is None:
        return None
    try:
        today = pd.Timestamp('today').normalize()
        posted_date = pd.Timestamp(date_posted).normalize()
        days_diff = (today - posted_date).days
        return days_diff
    except Exception as e:
        logging.warning(f"Could not calculate days since posted: {e}")
        return None

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

def generate_unique_id():
    """Generate a unique ID using UUID4."""
    return str(uuid.uuid4())

def save_job_details(df, job_title):
    """Save job details with updated directory and formatting."""
    try:
        # Add unique IDs to each job record
        df['job_id'] = [generate_unique_id() for _ in range(len(df))]
        
        # Clean job title for directory name
        job_title_clean = job_title.lower().replace(' ', '_')
        
        # Create base folder structure with job_details subdirectory
        folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
        os.makedirs(folder_store, exist_ok=True)
        
        # Generate filename with date
        current_date = datetime.now().strftime('%Y%m%d')
        
        # Generate random 5-digit number
        random_number = str(random.randint(10000, 99999))
        
        # Construct the filename (all lowercase) without company name
        base_filename = f"{job_title_clean}_details_{current_date}_{random_number}"
        
        # Reorder columns to have job_id first
        cols = ['job_id'] + [col for col in df.columns if col != 'job_id']
        df = df[cols]
        
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

def process_job_links(links, output_dir, job_title):
    """Process job links in batches with appropriate delays."""
    try:
        # Initialize driver once
        driver = create_driver()
        load_cookies(driver, load_cookie_data())
        
        # Process in small batches
        batch_size = 3
        results = []
        
        for i in range(0, len(links), batch_size):
            batch = links[i:i + batch_size]
            logging.info(f"Processing batch {i//batch_size + 1} of {(len(links) + batch_size - 1)//batch_size}")
            
            # Process each URL in the batch
            for url in batch:
                try:
                    job_details = get_job_details(driver, url)
                    if job_details:
                        results.append(job_details)
                except Exception as e:
                    logging.error(f"Error processing URL {url}: {e}")
                    continue
                
                # Add delay between jobs within batch (5-10 seconds)
                time.sleep(random.uniform(5, 10))
            
            # Add longer delay between batches (20-30 seconds)
            if i + batch_size < len(links):
                delay = random.uniform(20, 30)
                logging.info(f"Taking a break between batches ({delay:.1f} seconds)...")
                time.sleep(delay)
        
        # Create results DataFrame
        df_results = pd.DataFrame(results, columns=[
            'job_title', 'company', 'description', 'date_posted',
            'location', 'remote', 'salary', 'job_url', 'days_since_posted'
        ])
        
        # Save results in job_details directory
        job_title_clean = job_title.lower().replace(' ', '_')
        folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
        os.makedirs(folder_store, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{job_title_clean}_job_details_{timestamp}.csv"
        output_path = os.path.join(folder_store, output_filename)
        
        # Save both CSV and JSON
        df_results.to_csv(output_path, index=False)
        logging.info(f"Results saved to {output_path}")
        
        # Save JSON version
        json_path = output_path.replace('.csv', '.json')
        output_data = {
            "metadata": {
                "job_title": job_title_clean,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_jobs": len(df_results)
            },
            "jobs": df_results.to_dict('records')
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        logging.info(f"Results saved to {json_path}")
        
        return df_results
        
    except Exception as e:
        logging.error(f"Error in process_job_links: {e}")
        return pd.DataFrame()
    finally:
        try:
            cleanup_driver(driver)
        except:
            pass

def main(job_title, input_filename):
    """Main function with cleaned job title."""
    driver = None
    try:
        # Clean job title
        job_title_clean = job_title.lower().replace(' ', '_')
        
        # Initialize metrics tracker
        metrics_tracker = JobMetricsTracker()
        
        # Load job links from input file
        logging.info(f"Loading job links from {input_filename}")
        df, links = load_job_links(input_filename)
        if not links:
            logging.warning("No job links found to process.")
            return

        # Initialize driver
        logging.info("Initializing Chrome driver...")
        driver = create_driver()
        
        try:
            # Load cookies
            logging.info("Loading cookies...")
            cookies = load_cookie_data()
            if cookies:
                load_cookies(driver, cookies)
            else:
                logging.warning("No cookies loaded")
            
            # Process job links and collect detailed information
            logging.info("Starting to process job links...")
            detailed_jobs = []
            for link in links:
                job_details = get_job_details(driver, link)
                if job_details:
                    # Convert tuple to dictionary
                    job_dict = {
                        'job_title': job_details[0],
                        'company': job_details[1],
                        'description': job_details[2],
                        'date_posted': job_details[3],
                        'location': job_details[4],
                        'remote': job_details[5],
                        'salary': job_details[6],
                        'job_url': job_details[7]
                    }
                    detailed_jobs.append(job_dict)
            
            # Create DataFrame from detailed jobs
            if detailed_jobs:
                df_results = pd.DataFrame(detailed_jobs)
                
                # Save to job details directory
                folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
                os.makedirs(folder_store, exist_ok=True)
                
                # Generate filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = f"{job_title_clean}_job_details_{timestamp}.csv"
                output_path = os.path.join(folder_store, output_filename)
                
                # Save CSV
                df_results.to_csv(output_path, index=False)
                logging.info(f"Results saved to {output_path}")
                
                # Save JSON version
                json_path = output_path.replace('.csv', '.json')
                output_data = {
                    "metadata": {
                        "job_title": job_title_clean,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "total_jobs": len(df_results)
                    },
                    "jobs": df_results.to_dict('records')
                }
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                logging.info(f"Results saved to {json_path}")
                
                # Update metrics
                metrics_tracker.update_jobs_aggregation(
                    job_title=job_title,
                    new_jobs=detailed_jobs
                )
            
        finally:
            if driver:
                logging.info("Closing Chrome driver...")
                cleanup_driver(driver)
                
    except Exception as e:
        logging.error(f"Error in main processing: {str(e)}")
        if driver:
            try:
                cleanup_driver(driver)
            except:
                pass
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_title", required=True)
    parser.add_argument("--filename", required=True)
    args = parser.parse_args()
    
    main(args.job_title, args.filename)

```

```python
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
from job_metrics_tracker import JobMetricsTracker
import uuid
import shutil
from driver_utils import create_driver, cleanup_driver

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
    """Get details for a single job posting."""
    max_retries = 2  # Reduced retries since we're using batch processing
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logging.info(f"Processing URL: {url}")
            
            # Initial page load with delay
            driver.get(url)
            time.sleep(random.uniform(3, 5))
            
            wait = WebDriverWait(driver, 15)
            
            # Initialize variables
            job_title = company_name = job_description = date_posted = location = salary = remote_status = days_since_posted = None
            
            # Extract job details with minimal delays
            try:
                show_more_button = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '.feed-shared-inline-show-more-text__see-more-less-toggle')))
                driver.execute_script("arguments[0].click();", show_more_button)
            except Exception as e:
                logging.warning(f"Show more button not found: {e}")
            
            # Extract all fields with appropriate waits
            job_title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1'))).text.strip()
            
            try:
                job_description_element = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-about-the-job-module__description div.feed-shared-inline-show-more-text')))
                job_description = job_description_element.text.replace("-", " ").strip()
                job_description = re.sub(r'\s+', ' ', job_description)
            except:
                job_description = "-"
                
            try:
                company_name = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__company-name a'))).text.strip()
            except:
                company_name = "-"
                
            try:
                # Target the tertiary description container where date info is located
                tertiary_container = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__tertiary-description-container')))
                
                # Find spans that contain "Reposted" or "Posted" followed by time information
                date_text = None
                spans = tertiary_container.find_elements(By.CSS_SELECTOR, 'span.tvm__text.tvm__text--low-emphasis')
                
                for span in spans:
                    span_text = span.text.strip()
                    # Check if this span contains date-related keywords
                    if 'Reposted' in span_text or 'Posted' in span_text:
                        # Get the full text including nested spans
                        date_text = span_text
                        break
                
                if date_text:
                    date_posted = parse_date_posted(date_text)
                    # Calculate days since posted
                    days_since_posted = calculate_days_since_posted(date_posted)
                else:
                    date_posted = None
                    days_since_posted = None
            except Exception as e:
                logging.warning(f"Could not extract date posted: {e}")
                date_posted = None
                days_since_posted = None
                
            try:
                location = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.job-details-jobs-unified-top-card__primary-description-container span.tvm__text'))).text.strip()
            except:
                location = "-"
                
            try:
                salary = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.job-details-preferences-and-skills__pill span.ui-label.text-body-small"))).text.strip()
            except:
                salary = "-"
                
            try:
                # Look for the job-details-fit-level-preferences container first
                preferences_container = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.job-details-fit-level-preferences")))
                
                # Find buttons within the container that contain location type text
                buttons = preferences_container.find_elements(By.TAG_NAME, "button")
                remote_status = "Onsite"  # Default fallback
                
                for button in buttons:
                    button_text = button.text.strip()
                    # Check if button contains location type keywords
                    if any(keyword in button_text for keyword in ["Remote", "Hybrid", "Onsite"]):
                        # Extract just the location type (may have other text like "Full-time")
                        if "Remote" in button_text:
                            remote_status = "Remote"
                            break
                        elif "Hybrid" in button_text:
                            remote_status = "Hybrid"
                            break
                        elif "Onsite" in button_text:
                            remote_status = "Onsite"
                            break
                
            except Exception as e:
                logging.warning(f"Could not extract remote status: {e}")
                remote_status = "Onsite"
            
            return job_title, company_name, job_description, date_posted, location, remote_status, salary, url, days_since_posted
            
        except Exception as e:
            retry_count += 1
            logging.warning(f"Attempt {retry_count} failed for URL {url}: {e}")
            if retry_count < max_retries:
                time.sleep(random.uniform(5, 8))
            else:
                logging.error(f"Failed to retrieve details after {max_retries} attempts")
                return "-", "-", "-", None, "-", "Onsite", "-", url, None

def parse_date_posted(date_text):
    """Parse the date posted text into a timestamp."""
    try:
        today = pd.Timestamp('today')
        if 'hour' in date_text:
            hours = int(re.search(r'(\d+)\s*hour', date_text).group(1))
            return today - pd.Timedelta(hours=hours)
        elif 'day' in date_text:
            days = int(re.search(r'(\d+)\s*day', date_text).group(1))
            return today - pd.Timedelta(days=days)
        elif 'week' in date_text:
            weeks = int(re.search(r'(\d+)\s*week', date_text).group(1))
            return today - pd.Timedelta(weeks=weeks)
        elif 'month' in date_text:
            months = int(re.search(r'(\d+)\s*month', date_text).group(1))
            return today - pd.DateOffset(months=months)
    except Exception as e:
        logging.warning(f"Could not parse date: {date_text} - {e}")
        return None

def calculate_days_since_posted(date_posted):
    """Calculate the number of days between the extraction date and the posting date."""
    if date_posted is None:
        return None
    try:
        today = pd.Timestamp('today').normalize()
        posted_date = pd.Timestamp(date_posted).normalize()
        days_diff = (today - posted_date).days
        return days_diff
    except Exception as e:
        logging.warning(f"Could not calculate days since posted: {e}")
        return None

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

def generate_unique_id():
    """Generate a unique ID using UUID4."""
    return str(uuid.uuid4())

def save_job_details(df, job_title):
    """Save job details with updated directory and formatting."""
    try:
        # Add unique IDs to each job record
        df['job_id'] = [generate_unique_id() for _ in range(len(df))]
        
        # Clean job title for directory name
        job_title_clean = job_title.lower().replace(' ', '_')
        
        # Create base folder structure with job_details subdirectory
        folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
        os.makedirs(folder_store, exist_ok=True)
        
        # Generate filename with date
        current_date = datetime.now().strftime('%Y%m%d')
        
        # Generate random 5-digit number
        random_number = str(random.randint(10000, 99999))
        
        # Construct the filename (all lowercase) without company name
        base_filename = f"{job_title_clean}_details_{current_date}_{random_number}"
        
        # Reorder columns to have job_id first
        cols = ['job_id'] + [col for col in df.columns if col != 'job_id']
        df = df[cols]
        
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

def process_job_links(links, output_dir, job_title):
    """Process job links in batches with appropriate delays."""
    try:
        # Initialize driver once
        driver = create_driver()
        load_cookies(driver, load_cookie_data())
        
        # Process in small batches
        batch_size = 3
        results = []
        
        for i in range(0, len(links), batch_size):
            batch = links[i:i + batch_size]
            logging.info(f"Processing batch {i//batch_size + 1} of {(len(links) + batch_size - 1)//batch_size}")
            
            # Process each URL in the batch
            for url in batch:
                try:
                    job_details = get_job_details(driver, url)
                    if job_details:
                        results.append(job_details)
                except Exception as e:
                    logging.error(f"Error processing URL {url}: {e}")
                    continue
                
                # Add delay between jobs within batch (5-10 seconds)
                time.sleep(random.uniform(5, 10))
            
            # Add longer delay between batches (20-30 seconds)
            if i + batch_size < len(links):
                delay = random.uniform(20, 30)
                logging.info(f"Taking a break between batches ({delay:.1f} seconds)...")
                time.sleep(delay)
        
        # Create results DataFrame
        df_results = pd.DataFrame(results, columns=[
            'job_title', 'company', 'description', 'date_posted',
            'location', 'remote', 'salary', 'job_url', 'days_since_posted'
        ])
        
        # Save results in job_details directory
        job_title_clean = job_title.lower().replace(' ', '_')
        folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
        os.makedirs(folder_store, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{job_title_clean}_job_details_{timestamp}.csv"
        output_path = os.path.join(folder_store, output_filename)
        
        # Save both CSV and JSON
        df_results.to_csv(output_path, index=False)
        logging.info(f"Results saved to {output_path}")
        
        # Save JSON version
        json_path = output_path.replace('.csv', '.json')
        output_data = {
            "metadata": {
                "job_title": job_title_clean,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_jobs": len(df_results)
            },
            "jobs": df_results.to_dict('records')
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        logging.info(f"Results saved to {json_path}")
        
        return df_results
        
    except Exception as e:
        logging.error(f"Error in process_job_links: {e}")
        return pd.DataFrame()
    finally:
        try:
            cleanup_driver(driver)
        except:
            pass

def main(job_title, input_filename):
    """Main function with cleaned job title."""
    driver = None
    try:
        # Clean job title
        job_title_clean = job_title.lower().replace(' ', '_')
        
        # Initialize metrics tracker
        metrics_tracker = JobMetricsTracker()
        
        # Load job links from input file
        logging.info(f"Loading job links from {input_filename}")
        df, links = load_job_links(input_filename)
        if not links:
            logging.warning("No job links found to process.")
            return

        # Initialize driver
        logging.info("Initializing Chrome driver...")
        driver = create_driver()
        
        try:
            # Load cookies
            logging.info("Loading cookies...")
            cookies = load_cookie_data()
            if cookies:
                load_cookies(driver, cookies)
            else:
                logging.warning("No cookies loaded")
            
            # Process job links and collect detailed information
            logging.info("Starting to process job links...")
            detailed_jobs = []
            for link in links:
                job_details = get_job_details(driver, link)
                if job_details:
                    # Convert tuple to dictionary
                    job_dict = {
                        'job_title': job_details[0],
                        'company': job_details[1],
                        'description': job_details[2],
                        'date_posted': job_details[3],
                        'location': job_details[4],
                        'remote': job_details[5],
                        'salary': job_details[6],
                        'job_url': job_details[7],
                        'days_since_posted': job_details[8]
                    }
                    detailed_jobs.append(job_dict)
            
            # Create DataFrame from detailed jobs
            if detailed_jobs:
                df_results = pd.DataFrame(detailed_jobs)
                
                # Save to job details directory
                folder_store = f"./job_search/job_post_details/{job_title_clean}/job_details"
                os.makedirs(folder_store, exist_ok=True)
                
                # Generate filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = f"{job_title_clean}_job_details_{timestamp}.csv"
                output_path = os.path.join(folder_store, output_filename)
                
                # Save CSV
                df_results.to_csv(output_path, index=False)
                logging.info(f"Results saved to {output_path}")
                
                # Save JSON version
                json_path = output_path.replace('.csv', '.json')
                output_data = {
                    "metadata": {
                        "job_title": job_title_clean,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "total_jobs": len(df_results)
                    },
                    "jobs": df_results.to_dict('records')
                }
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                logging.info(f"Results saved to {json_path}")
                
                # Update metrics
                metrics_tracker.update_jobs_aggregation(
                    job_title=job_title,
                    new_jobs=detailed_jobs
                )
            
        finally:
            if driver:
                logging.info("Closing Chrome driver...")
                cleanup_driver(driver)
                
    except Exception as e:
        logging.error(f"Error in main processing: {str(e)}")
        if driver:
            try:
                cleanup_driver(driver)
            except:
                pass
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_title", required=True)
    parser.add_argument("--filename", required=True)
    args = parser.parse_args()
    
    main(args.job_title, args.filename)

```

Checking for linting errors:


Added the `days_since_posted` column. Changes:

1. **Added a helper function** `calculate_days_since_posted()` that:
   - Takes the parsed `date_posted` timestamp
   - Calculates the difference in days between today and the posting date
   - Returns `None` if the date is invalid

2. **Updated the extraction logic** to:
   - Calculate `days_since_posted` immediately after parsing the date
   - Include it in the return tuple (now 9 values instead of 8)

3. **Updated all references**:
   - Added `days_since_posted` to the DataFrame columns in `process_job_links()`
   - Added `days_since_posted` to the dictionary mapping in `main()`
   - Updated the error return case to include `None` for `days_since_posted`

The new column will show the number of days between the extraction date and the posting date. For example:
- "1 day ago" → `days_since_posted = 1`
- "2 weeks ago" → `days_since_posted = 14`
- "1 month ago" → `days_since_posted = ~30` (depending on the month)

The column will be included in all output CSV and JSON files. No linting errors found. Ready to test.

