import sys
import os

# Add job_search to Python path for driver_utils - using workspace-relative path
workspace_root = "/home/wynt3r/JobSearch"  # Hardcode the workspace root since we know it
driver_utils_path = os.path.join(workspace_root, 'job_search/job_extraction')
sys.path.append(driver_utils_path)

try:
    from driver_utils import create_driver, cleanup_driver
except ImportError as e:
    raise ImportError(f"Could not import driver_utils. Path {driver_utils_path} may be incorrect. Error: {e}")

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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Add console output
        logging.FileHandler('apollo_companies.log')  # Keep file logging
    ]
)

# Constants
DEFAULT_TIMEOUT = 20
SCROLL_PAUSE_TIME = 2
PAGE_LOAD_WAIT = 5
CLICK_WAIT = 0.5

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

def add_random_delays():
    """Add random delay between actions."""
    time.sleep(random.uniform(2, 5))

def save_page_html(driver, page_number, base_folder="/home/wynt3r/networking_pipeline/company_people_extractions/apollo_extractions/apollo_html"):
    """Save the current page HTML to a file."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(base_folder, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(base_folder, f"apollo_companies_page_{page_number}_{timestamp}.html")
        
        # Save the page source
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logging.info(f"Saved HTML for page {page_number} to {filename}")
        
    except Exception as e:
        logging.error(f"Error saving page HTML: {e}")

def load_cookie_data(cookie_file=None):
    """Load cookie data from external file."""
    if cookie_file is None:
        cookie_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'apollo_cookies.txt')
    try:
        with open(cookie_file, 'r') as file:
            content = file.read().strip()
            logging.info("Cookie file read successfully")
            
            # Clean up the content without logging it
            cookie_json = content.replace('\n', '').replace('    ', '')
            
            # Parse the JSON
            cookies = json.loads(cookie_json)
            logging.info(f"Successfully parsed {len(cookies)} cookies")
            return cookies
            
    except FileNotFoundError:
        logging.error(f"Cookie file not found: {cookie_file}")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing cookies JSON: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error loading cookies: {e}")
        raise

def apply_cookies(driver, cookies):
    """Apply cookies to the browser session."""
    try:
        for cookie in cookies:
            try:
                # Remove problematic keys
                if 'sameSite' in cookie:
                    del cookie['sameSite']
                if 'storeId' in cookie:
                    del cookie['storeId']
                # Handle expirationDate
                if 'expirationDate' in cookie:
                    cookie['expiry'] = int(cookie['expirationDate'])
                    del cookie['expirationDate']
                # Add domain if missing
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

def save_page_screenshot(driver, page_number, base_folder="/home/wynt3r/networking_pipeline/company_people_extractions/apollo_extractions/apollo_html"):
    """Save a screenshot of the current page."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(base_folder, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(base_folder, f"apollo_companies_page_{page_number}_{timestamp}.png")
        
        # Save the screenshot
        driver.save_screenshot(filename)
        logging.info(f"Saved screenshot for page {page_number} to {filename}")
        
    except Exception as e:
        logging.error(f"Error saving screenshot: {e}")

def navigate_to_page(driver, target_page):
    """Navigate to a specific page using direct URL."""
    try:
        logging.info(f"Attempting to navigate to page {target_page}")
        
        # Use the exact URL format with the target page
        url = f"https://app.apollo.io/#/people?page={target_page}&organizationNumEmployeesRanges[]=101%2C200&organizationNumEmployeesRanges[]=201%2C500&organizationNumEmployeesRanges[]=10001&organizationNumEmployeesRanges[]=5001%2C10000&organizationNumEmployeesRanges[]=2001%2C5000&organizationNumEmployeesRanges[]=501%2C1000&organizationNumEmployeesRanges[]=1001%2C2000&organizationNumEmployeesRanges[]=51%2C100&organizationLocations[]=United%20States&organizationTradingStatus[]=public&sortByField=%5Bnone%5D&sortAscending=false"
        
        logging.info(f"Navigating to URL: {url}")
        driver.get(url)
        time.sleep(5)  # Wait for page load
        
        # Take screenshot after navigation
        save_page_screenshot(driver, f"page_{target_page}")
        save_page_html(driver, f"page_{target_page}")
        
        # Verify navigation by checking the page number
        try:
            # Wait for records to be present
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='rowgroup']"))
            )
            
            # Verify we're on the correct page by checking the page number text
            current_page_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.zp_jzp8p"))
            )
            
            actual_page = current_page_element.text.strip()
            logging.info(f"Current page shows: {actual_page}, Target was: {target_page}")
            
            if str(target_page) == actual_page:
                logging.info(f"Successfully navigated to page {target_page}")
                return True
            else:
                logging.error(f"Navigation verification failed - Expected page {target_page}, but found page {actual_page}")
                return False
                
        except TimeoutException:
            logging.error(f"Failed to verify navigation to page {target_page}")
            save_page_screenshot(driver, f"page_{target_page}_verification_failed")
            save_page_html(driver, f"page_{target_page}_verification_failed")
            return False
            
    except Exception as e:
        logging.error(f"Error navigating to page {target_page}: {e}")
        save_page_screenshot(driver, f"page_{target_page}_error")
        save_page_html(driver, f"page_{target_page}_error")
        return False

def click_net_new_button(driver):
    """Click the Net New button in the filter section."""
    try:
        logging.info("Looking for Net New button...")
        wait = WebDriverWait(driver, DEFAULT_TIMEOUT)
        
        # Wait for the radio button group to be present
        radio_group = wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='radiogroup' and contains(@class, 'zp_mmM2U')]"))
        )
        
        # Find the Net New button within the radio group
        net_new_button = radio_group.find_element(By.XPATH, ".//label[.//div[contains(text(), 'Net New')]]")
        
        # Scroll the button into view and click with retry logic
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", net_new_button)
        time.sleep(CLICK_WAIT)
        
        try:
            net_new_button.click()
        except Exception as e:
            try:
                driver.execute_script("arguments[0].click();", net_new_button)
            except Exception as js_error:
                raise WebDriverException(f"Failed to click Net New button: {e}, {js_error}")
        
        # Wait for the filter to apply
        time.sleep(PAGE_LOAD_WAIT)
        logging.info("Clicked Net New button successfully")
        
    except Exception as e:
        logging.error(f"Error clicking Net New button: {e}")
        raise

def process_record(driver, record, index, output_file, current_page, total_records, page_records):
    """Process a single record with proper error handling."""
    try:
        # Find and click the Save button for this record with retry logic
        try:
            save_button = record.find_element(By.XPATH, ".//button[.//span[text()='Save']]")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_button)
            time.sleep(CLICK_WAIT)
            
            try:
                save_button.click()
            except Exception:
                driver.execute_script("arguments[0].click();", save_button)
            
            time.sleep(CLICK_WAIT)
            logging.info(f"Clicked Save button for record {index}")
        except Exception as e:
            logging.warning(f"Could not click Save button for record {index}: {e}")

        # Extract data with proper error handling
        data = {
            'company': "N/A",
            'links': "N/A",
            'location': "N/A",
            'employees': "N/A",
            'industry': "N/A",
            'keywords': "N/A"
        }

        # Company name
        try:
            data['company'] = record.find_element(
                By.XPATH, ".//a[@data-link-variant='default']/span"
            ).text.strip()
        except NoSuchElementException:
            logging.warning(f"Company name not found for record {index}")

        # LinkedIn URL
        try:
            links_element = record.find_element(By.XPATH, ".//a[contains(@href, 'linkedin')]")
            data['links'] = links_element.get_attribute("href")
        except NoSuchElementException:
            logging.warning(f"LinkedIn URL not found for record {index}")

        # Location
        try:
            data['location'] = record.find_element(
                By.XPATH, ".//span[contains(@class, 'zp_xvo3G') and contains(text(), ',')]"
            ).text.strip()
        except NoSuchElementException:
            logging.warning(f"Location not found for record {index}")

        # Employee count
        try:
            data['employees'] = record.find_element(
                By.XPATH, ".//span[contains(@data-count-size, 'small')]"
            ).text.strip()
        except NoSuchElementException:
            logging.warning(f"Employee count not found for record {index}")

        # Industry with popup handling
        try:
            industry_elements = record.find_elements(By.XPATH, ".//span[contains(@class, 'zp_CEZf9')]")
            visible_industries = []
            
            for element in industry_elements:
                try:
                    industry_text = element.text.strip()
                    if industry_text and not industry_text.startswith('+'):
                        visible_industries.append(industry_text)
                except StaleElementReferenceException:
                    continue

            # Handle "+X" button for additional industries
            more_industries_button = record.find_elements(
                By.XPATH,
                ".//button[contains(@class, 'zp_qe0Li')]//span[contains(@class, 'zp_CEZf9') and starts-with(text(), '+')]"
            )
            
            if more_industries_button:
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", more_industries_button[0])
                    time.sleep(CLICK_WAIT)
                    driver.execute_script("arguments[0].click();", more_industries_button[0])
                    time.sleep(1)
                    
                    wait = WebDriverWait(driver, 5)
                    popup_industries = wait.until(
                        EC.presence_of_all_elements_located(
                            (By.XPATH, "//div[contains(@class, 'zp_RF8MX')]//button//span[@class='zp_CEZf9']")
                        )
                    )
                    
                    for industry in popup_industries:
                        try:
                            industry_text = industry.text.strip()
                            if industry_text and industry_text not in visible_industries and not industry_text.startswith('+'):
                                visible_industries.append(industry_text)
                        except StaleElementReferenceException:
                            continue
                    
                    # Click elsewhere to close popup
                    driver.execute_script("document.elementFromPoint(0, 0).click();")
                    time.sleep(CLICK_WAIT)
                    
                except Exception as e:
                    logging.warning(f"Error getting additional industries: {e}")
            
            data['industry'] = '; '.join(visible_industries) if visible_industries else "N/A"
            
        except Exception as e:
            logging.warning(f"Error processing industries for record {index}: {e}")

        # Keywords
        try:
            data['keywords'] = record.find_element(
                By.XPATH, ".//div[contains(@class, 'zp_ofXB9')]//span[contains(@class, 'zp_CEZf9')]"
            ).text.strip()
        except NoSuchElementException:
            logging.warning(f"Keywords not found for record {index}")

        # Write data to CSV file with proper error handling
        try:
            with open(output_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    data['company'],
                    data['links'],
                    data['location'],
                    data['employees'],
                    data['industry'],
                    data['keywords']
                ])
        except IOError as e:
            logging.error(f"Failed to write record to CSV: {e}")
            raise

        return True

    except Exception as e:
        logging.error(f"Error processing record {index}: {e}")
        return False

def navigate_to_next_page(driver, current_page):
    """Navigate to the next page with proper error handling."""
    try:
        wait = WebDriverWait(driver, DEFAULT_TIMEOUT)
        
        # Find and click the Next button
        next_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@aria-label='Next' and contains(@class, 'zp_qe0Li')]")
            )
        )
        
        # Scroll the button into view
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
        time.sleep(SCROLL_PAUSE_TIME)
        
        # Click the next button with retry logic
        try:
            next_button.click()
        except Exception:
            driver.execute_script("arguments[0].click();", next_button)
        
        # Wait for the page to load with random delay
        time.sleep(random.uniform(10, 15))
        
        # Verify page changed
        try:
            current_page_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.zp_jzp8p"))
            )
            new_page = current_page_element.text.strip()
            
            if str(current_page + 1) == new_page:
                logging.info(f"Successfully navigated to page {new_page}")
                return True, int(new_page)
            else:
                logging.error(f"Navigation failed - Expected page {current_page + 1}, but found page {new_page}")
                return False, current_page
                
        except TimeoutException:
            logging.error("Could not verify page navigation - timeout waiting for page number")
            return False, current_page
            
    except Exception as e:
        logging.error(f"Failed to navigate to next page: {e}")
        return False, current_page

def main():
    driver = None
    display = None
    temp_dir = None
    try:
        # Get start and end page from environment variables with validation
        try:
            start_page = int(os.getenv('START_PAGE', '1'))
            end_page = int(os.getenv('END_PAGE', '100'))
            if start_page < 1 or end_page < start_page:
                raise ValueError("Invalid page range")
        except ValueError as e:
            logging.error(f"Invalid page numbers: {e}")
            return
        
        logging.info(f"Starting extraction from page {start_page} to page {end_page}")
        
        display = setup_virtual_display()
        driver, temp_dir = create_driver(profile_name="apollo_companies")
        
        # Add random delay before starting
        time.sleep(random.uniform(1, 3))
        
        # Load cookies and authenticate
        load_cookies(driver)
        
        # Navigate directly to filtered URL for companies
        filtered_url = f"https://app.apollo.io/#/companies?organizationNumEmployeesRanges[]=101%2C200&organizationNumEmployeesRanges[]=201%2C500&organizationNumEmployeesRanges[]=10001&organizationNumEmployeesRanges[]=5001%2C10000&organizationNumEmployeesRanges[]=2001%2C5000&organizationNumEmployeesRanges[]=501%2C1000&organizationNumEmployeesRanges[]=1001%2C2000&organizationNumEmployeesRanges[]=51%2C100&organizationLocations[]=United%20States&organizationTradingStatus[]=public&prospectedByCurrentTeam[]=no&sortAscending=false&sortByField=sanitized_organization_name_unanalyzed&page={start_page}"
        logging.info("Navigating to filtered Companies page...")
        driver.get(filtered_url)
        time.sleep(10)  # Wait for page load
        
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

        # Update output file path with error handling
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "companies")
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            logging.error(f"Failed to create output directory: {e}")
            raise
            
        output_file = os.path.join(output_dir, 'apollo_records_companies_2.csv')
        logging.info(f"Output file will be saved to: {output_file}")

        # Test file write access
        try:
            file_exists = os.path.isfile(output_file)
            with open(output_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(["Company", "LinkedIn URL", "Location", "# Employees", "Industry", "Keywords"])
                    logging.info("Created new CSV file with headers")
                else:
                    logging.info("Existing CSV file found, will append data")
        except Exception as e:
            logging.error(f"Failed to access output file: {e}")
            raise

        # Process pages
        current_page = start_page
        total_records = 0
        consecutive_errors = 0
        MAX_CONSECUTIVE_ERRORS = 3
        
        while current_page <= end_page:
            try:
                # Get the progress counter text
                try:
                    progress_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.zp_xAPpZ"))
                    )
                    progress_text = progress_element.text  # e.g., "1226 - 1250 of 7,747"
                    logging.info(f"Progress: {progress_text}")
                except Exception as e:
                    progress_text = "Progress counter not found"
                    logging.warning(f"Could not find progress counter: {e}")
                
                logging.info(f"Processing page {current_page} of {end_page}... ({progress_text})")
                print(f"\n{'='*50}")
                print(f"Processing page {current_page} of {end_page}")
                print(f"Progress: {progress_text}")
                print(f"{'='*50}\n")
                
                # Save the HTML for this page
                save_page_html(driver, current_page)
                
                # Initialize counter for this page
                page_records = 0
                
                # Wait until all rows on the page are present
                try:
                    records = WebDriverWait(driver, DEFAULT_TIMEOUT).until(
                        EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@id, 'table-row-')]"))
                    )
                    
                    if not records:
                        raise NoSuchElementException("No records found on page")
                    
                    logging.info(f"Found {len(records)} records on page {current_page}")
                    print(f"\n{'*'*20} STARTING DATA COLLECTION {'*'*20}")
                    print(f"Found {len(records)} records to process on page {current_page}")
                    print(f"{'*'*60}\n")

                    # Process each record
                    for index in range(len(records)):
                        try:
                            record_xpath = f"//div[@id='table-row-{index}']"
                            record = driver.find_element(By.XPATH, record_xpath)
                            
                            # Process the record
                            if process_record(driver, record, index, output_file, current_page, total_records, page_records):
                                total_records += 1
                                page_records += 1
                                consecutive_errors = 0  # Reset error counter on success
                            else:
                                consecutive_errors += 1
                                
                            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                                logging.error(f"Too many consecutive errors ({consecutive_errors}). Stopping execution.")
                                return
                            
                        except NoSuchElementException as e:
                            logging.error(f"Error processing record {index}: {e}")
                            consecutive_errors += 1
                            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                                logging.error(f"Too many consecutive errors ({consecutive_errors}). Stopping execution.")
                                return
                            continue

                    # Report progress for this page
                    logging.info(f"Page {current_page} complete - Collected {page_records} companies (Total: {total_records})")
                    print(f"Page {current_page} complete - Collected {page_records} companies (Total: {total_records})")

                    # Navigate to next page if not on last page
                    if current_page < end_page:
                        success, new_page = navigate_to_next_page(driver, current_page)
                        if success:
                            current_page = new_page
                            consecutive_errors = 0  # Reset error counter on successful navigation
                        else:
                            consecutive_errors += 1
                            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                                logging.error(f"Too many consecutive errors ({consecutive_errors}). Stopping execution.")
                                break
                            # Try to refresh the page and continue
                            driver.refresh()
                            time.sleep(PAGE_LOAD_WAIT)
                    else:
                        break
                        
                except TimeoutException as e:
                    logging.error(f"Timeout waiting for records on page {current_page}: {e}")
                    consecutive_errors += 1
                    if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                        logging.error(f"Too many consecutive errors ({consecutive_errors}). Stopping execution.")
                        break
                    continue

            except Exception as e:
                logging.error(f"Unexpected error on page {current_page}: {e}")
                consecutive_errors += 1
                if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                    logging.error(f"Too many consecutive errors ({consecutive_errors}). Stopping execution.")
                    break
                continue

        logging.info(f"Total pages processed: {current_page - 1}")
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
