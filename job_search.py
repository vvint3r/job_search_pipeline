from seleniumbase import Driver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pandas as pd
import random
import time
import os
from datetime import datetime
import json


raw_cookies = """[
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

# Job titles and search settings
job_titles = {
    "seo": {
        "job_type": "full_time",
        "salary_range": 140000,
        "search_type": "exact",
        "remote_status": True,
    },
}

def press_shift_tab(driver):
    actions = ActionChains(driver)
    actions.key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).perform()


def parse_cookies(raw_cookie_data):
    """Parses raw cookie JSON string into Python objects."""
    try:
        cookies = json.loads(raw_cookie_data)
        return cookies
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        with open("error_log.json", "w") as f:
            f.write(raw_cookie_data)  # Save the erroneous raw_cookies to a file
        return None

def load_cookies(driver, cookies):
    """Loads cookies into the Selenium browser."""
    if not cookies:
        print("No cookies to load.")
        return

    driver.get("https://www.linkedin.com/feed/")
    if "feed" not in driver.current_url:
        print("Login failed. Check cookies or manual login required.")
        time.sleep(30)  # Allow user to log in manually
    else:
        print("Login successful!")  # Navigate to LinkedIn first

    for cookie in cookies:
        try:
            formatted_cookie = {
                "name": cookie["name"],
                "value": cookie["value"],
                "domain": cookie["domain"],
                "path": cookie.get("path", "/"),
                "secure": cookie.get("secure", False),
                "httpOnly": cookie.get("httpOnly", False),
            }
            driver.add_cookie(formatted_cookie)
        except KeyError as e:
            print(f"Missing cookie field: {e} - Skipping cookie: {cookie}")
    driver.refresh()
    print("Cookies loaded successfully!")

def generate_linkedin_job_url(job_title: str, settings: dict) -> str:
    """Generates LinkedIn job search URL based on job title and settings."""
    base_url = "https://www.linkedin.com/jobs/search/"
    keywords = f"%22{job_title.lower()}%22" if settings["search_type"] == "exact" else job_title.lower()
    salary_param = "&f_SB2=6" if settings["salary_range"] >= 140000 else "&f_SB2=7"
    remote_param = "&f_WT=2" if settings["remote_status"] else "&geoId=103644278"
    return f"{base_url}?keywords={keywords}{remote_param}{salary_param}&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true"


def save_page_html(driver, file_name="page_source.html"):
    """Saves the entire HTML of the current page to a file."""
    try:
        # Get the page source
        page_html = driver.page_source
        # Save to a file
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(page_html)
        print(f"Page HTML saved to {file_name}")
    except Exception as e:
        print(f"Error saving page HTML: {e}")


def scrape_job_data(driver, url):
    """Scrapes job data from a LinkedIn job search page."""
    job_data = []
    page = 1
    max_pages = 5  # Limit to avoid infinite loops or over-scraping

    load_cookies(driver, parse_cookies(raw_cookies))

    # Verify login
    driver.get("https://www.linkedin.com/feed/")
    if "feed" not in driver.current_url:
        print("Failed to log in using cookies. Check your cookie values.")
        return job_data

    driver.get(url)
    press_shift_tab(driver)
    time.sleep(random.uniform(5, 10))

    while page <= max_pages:
        try:
            jobs_scrollable_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#main > div > div.scaffold-layout__list-detail-inner.scaffold-layout__list-detail-inner--grow > div.scaffold-layout__list")
                )
            )
        except Exception as e:
            print("Error locating job container:", e)
            return job_data
        time.sleep(random.uniform(5, 10))

        try:
            last_height = 0
            while True:
                # Scroll down slightly instead of fully to trigger loading
                driver.execute_script("arguments[0].scrollTop += 300;", jobs_scrollable_container)
                time.sleep(1)  # Small delay to allow content to load

                new_height = driver.execute_script("return arguments[0].scrollHeight", jobs_scrollable_container)
                print(f"Scrolling... last_height={last_height}, new_height={new_height}")
                if new_height == last_height:
                    break  # Exit if no more content is loaded
                last_height = new_height
                
            for _ in range(10):  # Press the down key 10 times
                driver.execute_script("arguments[0].scrollBy(0, 300);", jobs_scrollable_container)
                time.sleep(1)

            time.sleep(5)
            
            # Extract job cards
            jobs_list = jobs_scrollable_container.find_elements(By.CSS_SELECTOR, ".job-card-container--clickable")
            print(f"Found {len(jobs_list)} job cards on page {page}.")
            
            for idx, job in enumerate(jobs_list):
                print(f"Job {idx + 1}: {job.text[:50]}")

            for idx, job in enumerate(jobs_list):
                driver.execute_script("arguments[0].scrollIntoView(true);", job)
                print(f"Scrolled to job {idx + 1}: {job.text[:50]}")
                try:
                    jobs_list = driver.find_elements(By.CSS_SELECTOR, ".job-card-container--clickable")
                    job = jobs_list[idx]
                    
                    try:
                        # Find the job title element
                        job_title_tag = job.find_element(By.CSS_SELECTOR, "a.job-card-container__link")
                        
                        # Extract only the visible text of the job title
                        job_title = job_title_tag.get_attribute("aria-label")
                        job_title = job_title.replace(" with verification", "")
                    except NoSuchElementException:
                        job_title = "Not Available"

                    # Extracting job URL
                    try:
                        job_url_block = job.find_element(By.CSS_SELECTOR, "a.job-card-container__link")
                        job_url = job_url_block.get_attribute("href")
                        job_url = job_url.split("?")[0]
                    except NoSuchElementException:
                        job_url = "Not Available"

                    # Extracting company name
                    try:
                        company_name = job.find_element(By.CSS_SELECTOR, "span.boAvmrAFfwZEHebYjctgTppwiEwazqIftEMU").text.strip()
                    except NoSuchElementException:
                        company_name = "Not Available"

                    # Extracting location
                    try:
                        location = job.find_element(By.CSS_SELECTOR, "ul.job-card-container__metadata-wrapper li span").text.strip()
                    except NoSuchElementException:
                        location = "Not Available"

                    # Extracting salary range if available
                    try:
                        salary_tag = job.find_element(By.CSS_SELECTOR, "div.artdeco-entity-lockup__metadata span")
                        salary_range = salary_tag.text.strip()
                    except NoSuchElementException:
                        salary_range = "N/A"

                    # Extracting remote status if available
                    try:
                        remote_status_element = job.find_element(By.XPATH, ".//*[contains(text(), 'Remote') or contains(text(), 'Onsite') or contains(text(), 'Hybrid')]")
                        remote_status = remote_status_element.text.strip()
                    except NoSuchElementException:
                        remote_status = "Onsite"  # Default to Onsite if not found

                    # Appending the job data to our list
                    job_data.append({
                        "company_title": company_name,
                        "job_title": job_title,
                        "job_url": job_url,
                        "salary_range": salary_range,
                        "location": location,
                        "remote_status": remote_status
                    })
                except Exception as e:
                    print(f"Error extracting data on page {page}: {e}")
                    break  # Exit while loop after error

            # Handle pagination
            try:
                next_page_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='View next page']"))
                )
                next_page_button.click()
                print("Clicked on Next button.")
                page += 1
                time.sleep(random.uniform(2, 5))
            except NoSuchElementException:
                print(f"No next page button found on page {page}. Assuming no more pages.")
                break
            except Exception as e:
                print(f"Error navigating to the next page...probably the last page.")
                break
        except Exception as e:
            print(f"Error during page scraping: {e}")
            break
    # save_page_html(driver, file_name="full_page_after_scrolling.html")
    return job_data

"""Main function to scrape LinkedIn job data."""
def main():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Enable headless mode
    driver = Driver(uc=True)
    
    try:
        driver.set_window_size(1200, 3000)
        all_jobs = []
        for job_title, settings in job_titles.items():
            url = generate_linkedin_job_url(job_title, settings)
            jobs = scrape_job_data(driver, url)
            if jobs:
                all_jobs.extend(jobs)
                # Save results
                base_folder = "job_search_results"
                search_folder = os.path.join(base_folder, job_title.lower())
                os.makedirs(search_folder, exist_ok=True)
                filename = os.path.join(
                    search_folder,
                    f"{job_title.lower()}_salary-{settings['salary_range']}_type-{settings['job_type'].lower()}_search-{settings['search_type'].lower()}_remote-{str(settings['remote_status']).lower()}_{datetime.now().strftime('%Y%m%d')}.csv"
                )

                pd.DataFrame(jobs).to_csv(filename, index=False)
                print(f"Saved jobs to {filename}")

                # Log the job search parameters
                log_filename = os.path.join(base_folder, "jobs_ran.csv")
                job_run_data = {
                    "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "job_keyword": job_title,
                    **settings,
                    "total_jobs_found": len(jobs)
                }
                if os.path.exists(log_filename):
                    pd.DataFrame([job_run_data]).to_csv(log_filename, mode='a', header=False, index=False)
                else:
                    pd.DataFrame([job_run_data]).to_csv(log_filename, index=False)
                print(f"Logged job run to {log_filename}")
            else:
                print(f"No jobs found for {job_title}. Skipping file saving.")
    finally:
        driver.quit()
        pass

if __name__ == "__main__":
    main()