import sys
import os

# Add job_search to Python path for driver_utils
# Go up from apollo_extractions -> company_people_extractions -> networking_pipeline -> home -> JobSearch
networking_pipeline_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
jobsearch_path = os.path.join(os.path.dirname(networking_pipeline_root), 'JobSearch', 'job_search', 'job_extraction')
sys.path.append(jobsearch_path)

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, WebDriverException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver import ActionChains
from pyvirtualdisplay import Display
import time
import csv
import random
import logging
from datetime import datetime
import json
from driver_utils import create_driver, cleanup_driver

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create directory for storing HTML and screenshots if it doesn't exist
APOLLO_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'apollo_html')
os.makedirs(APOLLO_OUTPUT_DIR, exist_ok=True)

def setup_virtual_display():
    """Set up virtual display for headless environment."""
    try:
        display = Display(visible=0, size=(1920, 1080))
        display.start()
        logging.info("Virtual display started")
        return display
    except Exception as e:
        logging.error(f"Error setting up virtual display: {e}")
        raise

def save_page_html(driver, page_number):
    """Save the current page HTML to a file."""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(APOLLO_OUTPUT_DIR, f"apollo_recruiters_page_{page_number}_{timestamp}.html")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logging.info(f"Saved HTML for page {page_number} to {filename}")
    except Exception as e:
        logging.error(f"Error saving page HTML: {e}")

def save_page_screenshot(driver, page_number):
    """Save a screenshot of the current page."""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(APOLLO_OUTPUT_DIR, f"apollo_recruiters_page_{page_number}_{timestamp}.png")
        driver.save_screenshot(filename)
        logging.info(f"Saved screenshot for page {page_number} to {filename}")
    except Exception as e:
        logging.error(f"Error saving screenshot: {e}")

def load_cookie_data(cookie_file=None):
    """Load cookie data from external file."""
    if cookie_file is None:
        cookie_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'apollo_cookies.txt')
    try:
        with open(cookie_file, 'r') as file:
            content = file.read().strip()
            logging.info("Cookie file read successfully")
            cookie_json = content.replace('\n', '').replace('    ', '')
            cookies = json.loads(cookie_json)
            logging.info(f"Successfully parsed {len(cookies)} cookies")
            return cookies
    except Exception as e:
        logging.error(f"Error loading cookies: {e}")
        raise

def apply_cookies(driver, cookies):
    """Apply cookies to the browser session."""
    try:
        for cookie in cookies:
            try:
                if 'sameSite' in cookie:
                    del cookie['sameSite']
                if 'storeId' in cookie:
                    del cookie['storeId']
                if 'expirationDate' in cookie:
                    cookie['expiry'] = int(cookie['expirationDate'])
                    del cookie['expirationDate']
                if 'domain' not in cookie:
                    cookie['domain'] = '.apollo.io'
                
                driver.add_cookie(cookie)
            except Exception as e:
                logging.warning(f"Error adding cookie {cookie.get('name', 'unknown')}: {e}")
                continue
        logging.info("Cookies applied successfully")
    except Exception as e:
        logging.error(f"Error applying cookies: {e}")
        raise

def load_cookies(driver, cookie_file=None):
    """Handle the complete cookie loading process."""
    if cookie_file is None:
        cookie_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'apollo_cookies.txt')
    try:
        cookies = load_cookie_data(cookie_file)
        logging.info(f"Successfully loaded {len(cookies)} cookies")
        
        driver.get("https://app.apollo.io/#/login")
        time.sleep(3)
        
        # Click the Google login button
        selectors = [
            "button[type='button'][class='zp-button zp_GGHzP zp_Kbe5T zp_PLp2D zp_rduLJ zp_g5xYz']",
            "//button[.//div[@class='zp_lVtbq' and text()='Log In with Google']]",
            "//button[.//img[contains(@src, 'google')] and .//div[contains(@class, 'zp_lVtbq')]]"
        ]
        
        google_login_button = None
        for selector in selectors:
            try:
                if '//' in selector:
                    elements = driver.find_elements(By.XPATH, selector)
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                if elements:
                    for element in elements:
                        try:
                            html = element.get_attribute('innerHTML')
                            if 'google' in html.lower() and 'Log In with Google' in html:
                                google_login_button = element
                                break
                        except:
                            continue
                if google_login_button:
                    break
            except Exception as e:
                continue
        
        if google_login_button:
            try:
                google_login_button.click()
            except:
                try:
                    driver.execute_script("arguments[0].click();", google_login_button)
                except:
                    actions = ActionChains(driver)
                    actions.move_to_element(google_login_button).click().perform()
                    
            time.sleep(5)
            driver.get("https://app.apollo.io/")
            time.sleep(3)
            apply_cookies(driver, cookies)
            driver.refresh()
            time.sleep(5)
            
        else:
            raise Exception("Could not find Google login button")
            
    except Exception as e:
        logging.error(f"Error in cookie loading process: {e}")
        raise

def main():
    driver = None
    display = None
    temp_dir = None
    try:
        total_records = 0
        current_page = 1
        
        display = setup_virtual_display()
        driver, temp_dir = create_driver(profile_name="apollo_recruiters")
        
        time.sleep(random.uniform(1, 3))
        load_cookies(driver)
        
        # Navigate directly to filtered URL with Net New filter
        filtered_url = "https://app.apollo.io/#/people?organizationNumEmployeesRanges[]=101%2C200&organizationNumEmployeesRanges[]=201%2C500&organizationNumEmployeesRanges[]=10001&organizationNumEmployeesRanges[]=5001%2C10000&organizationNumEmployeesRanges[]=2001%2C5000&organizationNumEmployeesRanges[]=501%2C1000&organizationNumEmployeesRanges[]=1001%2C2000&organizationNumEmployeesRanges[]=51%2C100&organizationLocations[]=United%20States&organizationTradingStatus[]=public&prospectedByCurrentTeam[]=no&personTitles[]=technical%20recruiter&sortAscending=false&sortByField=sanitized_organization_name_unanalyzed&page=1"
        logging.info("Navigating to filtered People page...")
        driver.get(filtered_url)
        time.sleep(10)
        
        # Click Net New button if not already selected
        try:
            net_new_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//label[@for='m5sbretq']"))
            )
            if not "zp_Tt1XI" in net_new_button.get_attribute("class"):
                logging.info("Clicking Net New button...")
                driver.execute_script("arguments[0].click();", net_new_button)
                time.sleep(5)
        except Exception as e:
            logging.error(f"Error clicking Net New button: {e}")
            
        # Open CSV file
        output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'apollo_recruiters', 'apollo_recruiter_records_2.csv')
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        file_exists = os.path.isfile(output_file)
        
        with open(output_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Name", "Title", "Company", "Email", "Links",
                               "Location", "# Employees", "Industry", "Keywords"])
        
        # Process pages
        while True:
            try:
                records_on_page = 0
                logging.info(f"\n{'='*50}")
                logging.info(f"Processing page {current_page}")
                logging.info(f"Total records collected so far: {total_records}")
                logging.info(f"{'='*50}\n")
                
                # Save page state
                save_page_html(driver, current_page)
                save_page_screenshot(driver, current_page)
                
                # Find and process records
                try:
                    main_container_xpath = "//div[@id='main-app']//div[contains(@class, 'zp_tFLCQ')]"
                    container = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, main_container_xpath))
                    )
                    records = container.find_elements(By.XPATH, ".//div[contains(@class, 'zp_hWv1I')][@role='row']")
                    
                    if not records:
                        logging.error("No records found in container")
                        break
                        
                    logging.info(f"Found {len(records)} records on page {current_page}")
                    
                    # Add scroll to ensure all records are loaded
                    driver.execute_script("window.scrollTo(0, 0);")  # Start at top
                    time.sleep(2)
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll to bottom
                    time.sleep(2)
                    driver.execute_script("window.scrollTo(0, 0);")  # Back to top
                    time.sleep(2)
                    
                    # Re-find records after scrolling
                    container = driver.find_element(By.XPATH, main_container_xpath)
                    records = container.find_elements(By.XPATH, ".//div[contains(@class, 'zp_hWv1I')][@role='row']")
                    
                    # Process each record
                    for index, record in enumerate(records):
                        try:
                            # Extract name
                            try:
                                name_element = record.find_element(By.XPATH, ".//a[@data-link-variant='default'][contains(@href, '/people/')]")
                                name = name_element.get_attribute('textContent').strip()
                                driver.execute_script("""
                                    arguments[0].addEventListener('click', function(e) {
                                        e.preventDefault();
                                        e.stopPropagation();
                                        return false;
                                    }, true);
                                """, name_element)
                            except NoSuchElementException:
                                name = "N/A"
                                
                            # Extract email
                            email = "N/A"
                            try:
                                email_button_selectors = [
                                    ".//button[contains(@class, 'zp_FG3Vz')][.//span[text()='Access email']]",
                                    ".//button[@data-cta-variant='secondary'][.//span[text()='Access email']]",
                                    ".//button[.//span[text()='Access email']]"
                                ]
                                
                                for selector in email_button_selectors:
                                    try:
                                        access_button = record.find_element(By.XPATH, selector)
                                        if access_button.is_displayed() and access_button.is_enabled():
                                            driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});", access_button)
                                            time.sleep(random.uniform(2, 3))
                                            driver.execute_script("""
                                                arguments[0].click();
                                                arguments[0].dispatchEvent(new Event('click', { bubbles: true }));
                                            """, access_button)
                                            
                                            email_element = WebDriverWait(record, 10).until(
                                                EC.presence_of_element_located((By.XPATH, ".//span[contains(@class, 'zp_hdyyu')]//span"))
                                            )
                                            email = email_element.text.strip()
                                            break
                                    except:
                                        continue
                            except Exception as e:
                                logging.warning(f"Error accessing email: {e}")
                                
                            # Extract other fields
                            try:
                                title = next((elem.text for elem in record.find_elements(By.XPATH, ".//span[contains(@class, 'zp_xvo3G')]") 
                                            if not elem.find_elements(By.XPATH, "ancestor::a[contains(@href, '/accounts/')]")), "N/A")
                            except:
                                title = "N/A"
                                
                            try:
                                company = record.find_element(By.XPATH, ".//a[contains(@href, '/accounts/')]//span[contains(@class, 'zp_xvo3G')]").text
                            except:
                                company = "N/A"
                                
                            try:
                                links = record.find_element(By.XPATH, ".//a[contains(@href, 'linkedin.com')]").get_attribute("href")
                            except:
                                links = "N/A"
                                
                            try:
                                location = next((elem.text for elem in record.find_elements(By.XPATH, ".//span[contains(@class, 'zp_xvo3G')]") if ',' in elem.text), "N/A")
                            except:
                                location = "N/A"
                                
                            try:
                                employees = record.find_element(By.XPATH, ".//span[contains(@class, 'zp_mE7no')]").text
                            except:
                                employees = "N/A"
                                
                            try:
                                industry_elements = record.find_elements(By.XPATH, ".//div[contains(@class, 'zp_ofXB9')]//span[contains(@class, 'zp_CEZf9')]")
                                industry = ", ".join([elem.text for elem in industry_elements if not elem.text.startswith('+')])
                            except:
                                industry = "N/A"
                                
                            try:
                                keywords_elements = record.find_elements(By.XPATH, ".//div[contains(@class, 'zp_ofXB9')]//span[contains(@class, 'zp_CEZf9')]")
                                keywords = ", ".join([elem.text for elem in keywords_elements if not elem.text.startswith('+')])
                            except:
                                keywords = "N/A"
                            
                            # Write to CSV
                            with open(output_file, mode='a', newline='', encoding='utf-8') as file:
                                writer = csv.writer(file)
                                writer.writerow([name, title, company, email, links, location, employees, industry, keywords])
                            
                            total_records += 1
                            records_on_page += 1
                            logging.info(f"Page {current_page}: Collected record {records_on_page}/25 - {name} ({total_records} total records)")
                            
                            time.sleep(random.uniform(2, 4))
                            
                        except Exception as e:
                            logging.error(f"Error processing record {index}: {e}")
                            continue
                    
                    # Try to move to next page
                    try:
                        next_page_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//i[contains(@class, 'apollo-icon-chevron-arrow-right')]"))
                        )
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_page_button)
                        driver.execute_script("arguments[0].click();", next_page_button)
                        time.sleep(random.uniform(10, 15))
                        current_page += 1
                    except:
                        logging.info("No next page button found - reached the end of results")
                        break
                        
                except Exception as e:
                    logging.error(f"Error processing page {current_page}: {e}")
                    break
                    
            except Exception as e:
                logging.error(f"Unexpected error on page {current_page}: {e}")
                break
                
        logging.info(f"Total pages processed: {current_page}")
        logging.info(f"Total records collected: {total_records}")
        
    except Exception as e:
        logging.error(f"Script failed: {e}")
        if driver:
            save_page_screenshot(driver, "error")
            save_page_html(driver, "error")
    finally:
        if driver:
            cleanup_driver(driver, temp_dir)
            logging.info("Driver closed")
        if display:
            display.stop()
            logging.info("Virtual display stopped")

if __name__ == "__main__":
    main()
