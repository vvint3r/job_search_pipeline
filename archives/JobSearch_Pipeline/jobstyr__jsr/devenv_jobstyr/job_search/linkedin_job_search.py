from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import random
import urllib.parse
from datetime import datetime
import os

# vasily@growthstyr.com
# 6269c9ff8f58c433

# SETTINGS
### LOCATION = Remote # REMOTE = geoId=103644278
### SALARY MIN = $140,000 # SALARY 140000 _SB=6 OR 160000 _SB=7
### SEARCH TYPE = Exact Match ("") # EXACT = %22%22
### JOB TYPE = Full-time OR Contract

# https://www.linkedin.com/jobs/search/?currentJobId=4056010437&f_SB2=6&geoId=103644278&keywords=%22growth%20marketing%22&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true


job_titles = {
    "marketing analytics": {
        "job_type": "full_time",
        "salary_range": 140000,
        "search_type": "exact",
        "remote_status": True,
    },
    # Add more job titles as needed...
}

def generate_linkedin_job_url(job_title: str, settings: dict) -> str:
    # Base URL for LinkedIn job search
    base_url = "https://www.linkedin.com/jobs/search/"

    # Set a reasonable range for currentJobId to make it look realistic
    current_job_id = random.randint(4056010000, 4056010999)

    # Encode the job title to handle spaces and special characters
    keywords = urllib.parse.quote(job_title.lower())

    # Add quotes around keywords if search type is "exact"
    if settings.get("search_type") == "exact":
        keywords = f"%22{keywords}%22"

    # Construct the URL with dynamic salary range, remote status, and job type
    salary_param = f"&f_SB2=6" if settings.get("salary_range") >= 140000 else f"&f_SB2=7"
    remote_param = "&geoId=103644278" if settings.get("remote_status") else ""
    url = (
        f"{base_url}?keywords={keywords}"
        f"{remote_param}"
        f"{salary_param}"
        f"&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true"
    )

    # Add currentJobId only if necessary
    if current_job_id:
        url += f"&currentJobId={current_job_id}"

    return url

# Generate a list of URLs to be scraped
urls = [generate_linkedin_job_url(job_title, settings) for job_title, settings in job_titles.items()]

# Set up Selenium WebDriver options
options = Options()
options.add_argument('--log-level=3')
options.add_argument('--no-sandbox')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')
options.add_argument('--enable-unsafe-swiftshader')

# Initialize the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Disable WebDriver detection by modifying properties
script_to_disable_webdriver = "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': script_to_disable_webdriver})

# Function to login to LinkedIn
def linkedin_login(driver):
    driver.get("https://www.linkedin.com/login")
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "username")))
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")

        ActionChains(driver).move_to_element(username_field).click().send_keys("vasily.souzdenkov@gmail.com").perform()
        ActionChains(driver).move_to_element(password_field).click().send_keys("Dennisport23!").perform()

        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        ActionChains(driver).move_to_element(login_button).click().perform()
        WebDriverWait(driver, 15).until(EC.presence_of_element_located(
            (By.ID, "global-nav")))  # Wait until the main page loads
    except Exception as e:
        print(f"Error during login: {e}")

# Login to LinkedIn
linkedin_login(driver)

# Function to scrape job data from a given URL
def scrape_job_data(url):
    job_data = []
    driver.get(url)
    page = 1
    max_pages = 5  # Set the maximum number of pages to scrape

    while page <= max_pages:
        try:
            # Wait until the job cards are visible
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".job-card-container--clickable"))
            )
            
            # Find all job cards on the page
            jobs_list = driver.find_elements(By.CSS_SELECTOR, ".job-card-container--clickable")
            total_jobs = len(jobs_list)
            print(f"Found {total_jobs} job listings on page {page}.")

            if not jobs_list:
                print(f"No jobs found on page {page} of URL {url}")
                break

            for job_index in range(total_jobs):
                retries = 3  # Number of times to retry fetching the job element
                while retries > 0:
                    try:
                        # Find the specific job listing again to avoid stale reference
                        jobs_list = driver.find_elements(By.CSS_SELECTOR, ".job-card-container--clickable")
                        job = jobs_list[job_index]

                        # Scroll the job listing into view to avoid issues with dynamic loading
                        driver.execute_script("arguments[0].scrollIntoView(true);", job)
                        time.sleep(1)  # Allow some time for the scrolling effect

                        # Extracting company name
                        company_name = job.find_element(By.CSS_SELECTOR, "span.nptHuPmjxcxCgXcXpNBLrWMmFRWtqoaWeY").text.strip()
                        # Extracting job title and job URL
                        job_title_tag = job.find_element(By.CSS_SELECTOR, "a.job-card-list__title--link")
                        job_title = job_title_tag.text.strip()
                        job_url = "https://www.linkedin.com" + job_title_tag.get_attribute("href")
                        # Extracting location
                        location = job.find_element(By.CSS_SELECTOR, "div.artdeco-entity-lockup__caption span").text.strip()
                        # Extracting salary range if available
                        try:
                            salary_tag = job.find_element(By.CSS_SELECTOR, "div.artdeco-entity-lockup__metadata span")
                            salary_range = salary_tag.text.strip()
                        except:
                            salary_range = "N/A"

                        # Appending the job data to our list
                        job_data.append({
                            "company_title": company_name,
                            "job_title": job_title,
                            "job_url": job_url,
                            "salary_range": salary_range,
                            "location": location
                        })
                        break  # Exit while loop after successful extraction

                    except StaleElementReferenceException:
                        retries -= 1
                        if retries == 0:
                            print(f"Stale element reference for job {job_index + 1} on page {page}, moving to the next job.")
                            break
                        time.sleep(1)  # Short wait before retrying
                    except Exception as e:
                        print(f"Error extracting data for job {job_index + 1} on page {page}: {e}")
                        break

            # Check if next page is available
            try:
                next_page_button = driver.find_element(By.CLASS_NAME, "artdeco-pagination__button--next")
                if next_page_button.is_enabled():
                    next_page_button.click()
                    page += 1
                    time.sleep(2)  # Adding delay to avoid being blocked
                else:
                    print(f"No more pages available after page {page}.")
                    break
            except NoSuchElementException:
                print(f"No next page button found on page {page}. Assuming no more pages.")
                break
            except Exception as e:
                print(f"Error navigating to the next page: {e}")
                break

        except Exception as e:
            print(f"Error on page {page} of URL {url}: {e}")
            break

    return job_data

# Main function to scrape all URLs and save to CSV
def main():
    all_jobs = []
    for job_title, settings in job_titles.items():
        url = generate_linkedin_job_url(job_title, settings)
        jobs = scrape_job_data(url)
        all_jobs.extend(jobs)

        # Creating directory and file path for saving results
        folder_name = job_title.replace(" ", "_")
        save_dir = os.path.join("job_search_results", folder_name)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Creating filename with current date
        current_date = datetime.now().strftime("%Y%m%d")
        filename = f"{job_title}_{current_date}.csv"
        save_path = os.path.join(save_dir, filename)

        # Creating a DataFrame and saving the data to CSV
        df = pd.DataFrame(jobs)
        df.to_csv(save_path, index=False)
        print(f"Data saved to {save_path}")

if __name__ == "__main__":
    main()