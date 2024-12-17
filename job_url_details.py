import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import random
import pandas as pd
import re
import json
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def random_delay(base=1, variance=1):
    time.sleep(base + random.uniform(0, variance))

# Initialize undetected ChromeDriver options
options = uc.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')
options.add_argument('--disable-extensions')
options.add_argument('--disable-gpu')
options.add_argument('start-maximized')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36')
# options.add_argument('--headless=new')  # Enables headless mode

# Start undetected ChromeDriver
driver = uc.Chrome(options=options)

# Disable WebDriver detection
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

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

        return job_title, company_name, job_description, date_posted, location, remote_status, salary
    except Exception as e:
        print(f"Failed to retrieve details from {url}: {e}")
        return "-", "-", "-", "-", "-", "Onsite", "-"

def load_job_links(filepath):
    try:
        logging.info(f"Loading job URLs from {filepath}")
        df = pd.read_csv(filepath)
        return df, df['job_url'].tolist()
    except Exception as e:
        logging.error(f"Error loading job links: {e}")
        return None, []

if __name__ == "__main__":
    try:
        folder_store = "./job_results"  # Specify the folder to store the results
        os.makedirs(folder_store, exist_ok=True)
        filename = "seo_job_details.csv"
        raw_cookies = raw_cookies = """[
        {
            "domain": ".linkedin.com",
            "expirationDate": 1741383904.36598,
            "hostOnly": false,
            "httpOnly": false,
            "name": "li_sugr",
            "path": "/",
            "sameSite": "no_restriction",
            "secure": true,
            "session": false,
            "storeId": "0",
            "value": "c20e8f8c-5f72-42f3-ad0b-678bb65c18bf",
            "index": 0,
            "isSearch": false
        },
        {
            "domain": ".linkedin.com",
            "expirationDate": 1765143904.366038,
            "hostOnly": false,
            "httpOnly": false,
            "name": "bcookie",
            "path": "/",
            "sameSite": "no_restriction",
            "secure": true,
            "session": false,
            "storeId": "0",
            "value": "\\"v=2&fa999eb5-94ad-46ef-8730-f53e1e3feec2\\"",
            "index": 1,
            "isSearch": false
        },
        {
            "domain": ".www.linkedin.com",
            "expirationDate": 1765142659.398183,
            "hostOnly": false,
            "httpOnly": true,
            "name": "bscookie",
            "path": "/",
            "sameSite": "no_restriction",
            "secure": true,
            "session": false,
            "storeId": "0",
            "value": "\\"v=1&20241104201120b5a13ddb-f552-473c-8a60-ae7321b60f7bAQEJuEVt9O1O-HbieYteOnQUOgk2u-qC\\"",
            "index": 2,
            "isSearch": false
        },
        {
            "domain": ".linkedin.com",
            "hostOnly": false,
            "httpOnly": false,
            "name": "lang",
            "path": "/",
            "sameSite": "no_restriction",
            "secure": true,
            "session": true,
            "storeId": "0",
            "value": "v=2&lang=en-us",
            "index": 3,
            "isSearch": false
        },
        {
            "domain": ".linkedin.com",
            "hostOnly": false,
            "httpOnly": false,
            "name": "AMCVS_14215E3D5995C57C0A495C55%40AdobeOrg",
            "path": "/",
            "sameSite": "unspecified",
            "secure": false,
            "session": true,
            "storeId": "0",
            "value": "1",
            "index": 4,
            "isSearch": false
        },
        {
            "domain": ".linkedin.com",
            "expirationDate": 1736199905,
            "hostOnly": false,
            "httpOnly": false,
            "name": "aam_uuid",
            "path": "/",
            "sameSite": "unspecified",
            "secure": false,
            "session": false,
            "storeId": "0",
            "value": "30910866105047617252535806206296647870",
            "index": 5,
            "isSearch": false
        },
        {
            "domain": "www.linkedin.com",
            "expirationDate": 1749158643,
            "hostOnly": true,
            "httpOnly": false,
            "name": "g_state",
            "path": "/",
            "sameSite": "unspecified",
            "secure": false,
            "session": false,
            "storeId": "0",
            "value": "{\\"i_l\\":0}",
            "index": 6,
            "isSearch": false
        },
        {
            "domain": "www.linkedin.com",
            "expirationDate": 1749158643,
            "hostOnly": true,
            "httpOnly": false,
            "name": "g_state",
            "path": "/",
            "sameSite": "unspecified",
            "secure": false,
            "session": false,
            "storeId": "0",
            "value": "{\\"i_l\\":0}",
            "index": 6,
            "isSearch": false
        },
        {
            "domain": ".linkedin.com",
            "expirationDate": 1741382655.29172,
            "hostOnly": false,
            "httpOnly": false,
            "name": "liap",
            "path": "/",
            "sameSite": "no_restriction",
            "secure": true,
            "session": false,
            "storeId": "0",
            "value": "true",
            "index": 7,
            "isSearch": false
        },
        {
            "domain": ".www.linkedin.com",
            "expirationDate": 1765142655.291731,
            "hostOnly": false,
            "httpOnly": true,
            "name": "li_at",
            "path": "/",
            "sameSite": "no_restriction",
            "secure": true,
            "session": false,
            "storeId": "0",
            "value": "AQEDAQ0wUFwBmUY7AAABk6MCRlIAAAGTxw7KUk0ACB7oe6JKdQtHgS7_3cl3f57BKeM5KYs557H-bIyKBAzB8879W4iZoji8FmR_gIV8mw0XgUVBt7cL_4Us4Ikx3X3HeRjmO9Em52ALtPy3sXiIDfRd",
            "index": 8,
            "isSearch": false
        },
        {
            "domain": ".www.linkedin.com",
            "expirationDate": 1741382655.291739,
            "hostOnly": false,
            "httpOnly": false,
            "name": "JSESSIONID",
            "path": "/",
            "sameSite": "no_restriction",
            "secure": true,
            "session": false,
            "storeId": "0",
            "value": "\\"ajax:0111097221632539464\\"",
            "index": 9,
            "isSearch": false
        },
        {
            "domain": ".www.linkedin.com",
            "expirationDate": 1734817502,
            "hostOnly": false,
            "httpOnly": false,
            "name": "timezone",
            "path": "/",
            "sameSite": "unspecified",
            "secure": true,
            "session": false,
            "storeId": "0",
            "value": "America/Phoenix",
            "index": 10,
            "isSearch": false
        },
        {
            "domain": ".www.linkedin.com",
            "expirationDate": 1749159902,
            "hostOnly": false,
            "httpOnly": false,
            "name": "li_theme",
            "path": "/",
            "sameSite": "unspecified",
            "secure": true,
            "session": false,
            "storeId": "0",
            "value": "light",
            "index": 11,
            "isSearch": false
        },
        {
            "domain": ".www.linkedin.com",
            "expirationDate": 1749159902,
            "hostOnly": false,
            "httpOnly": false,
            "name": "li_theme_set",
            "path": "/",
            "sameSite": "unspecified",
            "secure": true,
            "session": false,
            "storeId": "0",
            "value": "app",
            "index": 12,
            "isSearch": false
        },
        {
            "domain": ".linkedin.com",
            "expirationDate": 1736198659.120568,
            "hostOnly": false,
            "httpOnly": false,
            "name": "AnalyticsSyncHistory",
            "path": "/",
            "sameSite": "no_restriction",
            "secure": true,
            "session": false,
            "storeId": "0",
            "value": "AQLo6VlYYEvIfwAAAZOjAlXMlTJE1fysvvWc_N6FAQrVGI5-Ej1rRnuf22n8zYicrslEQXRsogaSZP_2pSHWeA",
            "index": 13,
            "isSearch": false
        },
        {
            "domain": ".linkedin.com",
            "expirationDate": 1741382659.131206,
            "hostOnly": false,
            "httpOnly": false,
            "name": "_guid",
            "path": "/",
            "sameSite": "no_restriction",
            "secure": true,
            "session": false,
            "storeId": "0",
            "value": "b063fabc-919b-4880-8f16-a6fbe1d475ca",
            "index": 14,
            "isSearch": false
        },
        {
            "domain": ".linkedin.com",
            "expirationDate": 1736198659.398116,
            "hostOnly": false,
            "httpOnly": false,
            "name": "lms_ads",
            "path": "/",
            "sameSite": "no_restriction",
            "secure": true,
            "session": false,
            "storeId": "0"
        },
        {
            "value": "AQEAwqsDZC--EwAAAZOjAlZI024x6IbppSD4bhjP9MZrySxKYKumfH32ne6gFeeMGzrKthp3WHmnrnuVg47XLA7-8Df1aJdE",
            "index": 15,
            "isSearch": false
        },
        {
            "domain": ".linkedin.com",
            "expirationDate": 1736198659.398155,
            "hostOnly": false,
            "httpOnly": false,
            "name": "lms_analytics",
            "path": "/",
            "sameSite": "no_restriction",
            "secure": true,
            "session": false,
            "storeId": "0",
            "value": "AQEAwqsDZC--EwAAAZOjAlZI024x6IbppSD4bhjP9MZrySxKYKumfH32ne6gFeeMGzrKthp3WHmnrnuVg47XLA7-8Df1aJdE",
            "index": 16,
            "isSearch": false
        },
        {
            "domain": ".linkedin.com",
            "expirationDate": 1765142660.633248,
            "hostOnly": false,
            "httpOnly": true,
            "name": "dfpfpt",
            "path": "/",
            "sameSite": "unspecified",
            "secure": true,
            "session": false,
            "storeId": "0",
            "value": "5a73d79e1ef046afad2070ce8cd32b5b",
            "index": 17,
            "isSearch": false
        },
        {
            "domain": ".linkedin.com",
            "expirationDate": 1749158659,
            "hostOnly": false,
            "httpOnly": false,
            "name": "AMCV_14215E3D5995C57C0A495C55%40AdobeOrg",
            "path": "/",
            "sameSite": "unspecified",
            "secure": false,
            "session": false,
            "storeId": "0",
            "value": "-637568504%7CMCIDTS%7C20065%7CMCMID%7C30384012625251334942594022204613598069%7CMCAAMLH-1734211459%7C9%7CMCAAMB-1734211459%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1733613859s%7CNONE%7CvVersion%7C5.1.1%7CMCCIDH%7C-1477720840",
            "index": 18,
            "isSearch": false
        },
        {
            "domain": ".linkedin.com",
            "expirationDate": 1741382660,
            "hostOnly": false,
            "httpOnly": false,
            "name": "_gcl_au",
            "path": "/",
            "sameSite": "unspecified",
            "secure": false,
            "session": false,
            "storeId": "0",
            "value": "1.1.1286571137.1733606660",
            "index": 19,
            "isSearch": false
        },
        {
            "domain": ".linkedin.com",
            "hostOnly": false,
            "httpOnly": true,
            "name": "fptctx2",
            "path": "/",
            "sameSite": "unspecified",
            "secure": true,
            "session": true,
            "storeId": "0",
            "value": "taBcrIH61PuCVH7eNCyH0CYjjbqLuI8XF8pleSQW5Nbzf1Mh%252bpcP6o%252bMsCxxtrGwW2%252fj6kFwTXl2N%252bkEPUXC8KRA%252bDTsuO0tl1Kcbxw2PKeJa57tDfi9oOsySZsIn7%252fzxVaUEJi0JXBsW%252fYIy0kJsR9dtS%252bJRzo9ICTgM90jlHB847c1PmgsTCTn5bm%252bKGkrv0azXQAEYME8ntbSXBSsR6Ag4tIKv8UtJ3hSJULlUeDN%252b86PIkRQI6NJXhZj0Sl94AJpYh2PkqDlC0WjwZRMBuvEZZA4KKQAP4CFQjCHK4C2FmAUeLkiX1XQy8Yqh6v6Wlx9z2wdQoGyTyibCvTnKyqi733%252fewmggc754YC4bDI%253d",
            "index": 20,
            "isSearch": false
        },
        {
            "domain": ".linkedin.com",
            "expirationDate": 1736199904,
            "hostOnly": false,
            "httpOnly": false,
            "name": "UserMatchHistory",
            "path": "/",
            "sameSite": "no_restriction",
            "secure": true,
            "session": false,
            "storeId": "0",
            "value": "AQI2G6NiuLIJ_AAAAZOjFVTb8yCuCF8FV-wmDjCDk9ezZHR0MH9WUKrThqL5LE23nsxWgBxcxw8HQaWbrDbBkWkQqPHcYaKR-tjzJsTPmlTkxS2dJMy-bAdDLjAWnxItL94w140vdeQkOENX4id72qK-cHG7nT8WvBT9ydU2h6z9TRXez2h2UUtkk5oy98zWvc2TPs52fUIgwI_zgLO4n6Vi_1a74thYP2U9o9_tr4LPBFe3aZz3MK0tRxzftTlp-dnnbmUeWO53De26-LN0SVgk_g0YgBBwDiYEUrbxzkkto9hL6zMuZIOu-7TQ9rVXbqhqOsishCk1-JujV8LnGTzzvY5gZcAV8301K8kVFcCxyKeS8w",
            "index": 21,
            "isSearch": false
        },
        {
            "domain": ".linkedin.com",
            "expirationDate": 1733655444.973652,
            "hostOnly": false,
            "httpOnly": false,
            "name": "lidc",
            "path": "/",
            "sameSite": "no_restriction",
            "secure": true,
            "session": false,
            "storeId": "0",
            "value": "\\"b=OB08:s=O:r=O:a=O:p=O:g=4862:u=1709:x=1:i=1733607905:t=1733655445:v=2:sig=AQHNB2IfUX_NM71j-zT38PiAj7gNSHWu\\"",
            "index": 22,
            "isSearch": false
        }
        ]"""
        cookies = parse_cookies(raw_cookies)

        load_cookies(driver, cookies)
        df_jobs, job_links = load_job_links('C:\\Users\\vasil\\OneDrive\\Desktop\\gProjects\\gJobSearch\\job_search_results\\seo\\seo_20241209.csv')

        if not job_links:
            logging.warning("No job links found.")
            exit()

        results = []
        for link in job_links:
            result = get_job_details(driver, link)
            results.append(result)

        # Convert results to a DataFrame and export to CSV
        results_df = pd.DataFrame(results, columns=[
            "job_title", "company_name", "job_description", "date_posted", "location", "remote_status", "salary"
        ])
        output_file = os.path.join(folder_store, filename)
        results_df.to_csv(output_file, index=False)
        logging.info("Job details saved successfully.")

    except Exception as e:
        logging.critical(f"Unhandled exception occurred: {e}")
    finally:
        driver.quit()
