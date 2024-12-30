import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, WebDriverException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver import ActionChains
from pyvirtualdisplay import Display
import time
import os
import csv
import sys
import random
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Store credentials securely in environment variables
APOLLO_EMAIL = os.getenv('APOLLO_EMAIL', 'vasily.souzdenkov@gmail.com')
APOLLO_PASSWORD = os.getenv('APOLLO_PASSWORD', 'Souzdenkov23!')

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

def setup_driver():
    """Initialize and configure the Chrome driver with enhanced anti-detection."""
    try:
        options = uc.ChromeOptions()
        
        # Server-specific options
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # Enhanced anti-detection measures
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-browser-side-navigation')
        options.add_argument('--disable-site-isolation-trials')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--start-maximized')
        
        # Random window size
        width = random.randint(1050, 1200)
        height = random.randint(800, 1000)
        options.add_argument(f'--window-size={width},{height}')
        
        # Randomized user agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        options.add_argument(f'user-agent={random.choice(user_agents)}')
        
        driver = uc.Chrome(options=options)
        
        # Additional JavaScript patches to avoid detection
        driver.execute_script("""
            // Overwrite the navigator properties
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Add language and plugins to appear more human-like
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Modify the permissions behavior
            Object.defineProperty(navigator, 'permissions', {
                get: () => ({
                    query: Promise.resolve({ state: 'granted' })
                })
            });
            
            // Add a fake notification API
            window.Notification = {
                permission: 'default',
                requestPermission: () => Promise.resolve('default')
            };
        """)
        
        # Add random delay before returning driver
        time.sleep(random.uniform(1, 3))
        
        # Add this function to generate random but realistic hardware specs
        def get_random_hardware_specs():
            return f"""
            Object.defineProperty(navigator, 'hardwareConcurrency', {{
                get: () => {random.choice([4, 8, 12, 16])}
            }});
            Object.defineProperty(navigator, 'deviceMemory', {{
                get: () => {random.choice([4, 8, 16, 32])}
            }});
            Object.defineProperty(navigator, 'platform', {{
                get: () => '{random.choice(["Win32", "MacIntel", "Linux x86_64"])}'
            }});
            """

        # Then in setup_driver, add the random specs to your JavaScript
        driver.execute_script(get_random_hardware_specs())
        
        return driver
        
    except Exception as e:
        logging.error(f"Error setting up driver: {e}")
        raise

def add_random_delays():
    """Add random delay between actions."""
    time.sleep(random.uniform(2, 5))

def save_page_html(driver, page_number, base_folder="/home/wynt3r/JobSearch/company_people_extractions/apollo_extractions/apollo_html"):
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

def load_cookie_data(cookie_file='company_people_extractions/apollo_extractions/apollo_cookies.txt'):
    """Load cookie data from external file."""
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

def load_cookies(driver, cookie_file='company_people_extractions/apollo_extractions/apollo_cookies.txt'):
    """Handle the complete cookie loading process."""
    try:
        # First load and verify cookies
        cookies = load_cookie_data(cookie_file)
        logging.info(f"Successfully loaded {len(cookies)} cookies")
        
        # Navigate to base domain first
        logging.info("Navigating to base domain...")
        driver.get("https://app.apollo.io/#/login")
        time.sleep(3)
        
        # Click the Google login button using the correct selector
        logging.info("Looking for Google login button...")
        selectors = [
            # Exact class combination for the Google button
            "button[type='button'][class='zp-button zp_GGHzP zp_Kbe5T zp_PLp2D zp_rduLJ zp_g5xYz']",
            # Using the button label text
            "//button[.//div[@class='zp_lVtbq' and text()='Log In with Google']]",
            # Using the Google image presence
            "//button[.//img[contains(@src, 'google')] and .//div[contains(@class, 'zp_lVtbq')]]"
        ]
        
        google_login_button = None
        for selector in selectors:
            try:
                logging.info(f"Trying selector: {selector}")
                if '//' in selector:
                    elements = driver.find_elements(By.XPATH, selector)
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                logging.info(f"Found {len(elements)} elements with selector {selector}")
                if elements:
                    # Verify it's the Google login button by checking both image and text
                    for element in elements:
                        try:
                            html = element.get_attribute('innerHTML')
                            if 'google' in html.lower() and 'Log In with Google' in html:
                                google_login_button = element
                                logging.info("Found correct Google login button")
                                break
                        except:
                            continue
                if google_login_button:
                    break
            except Exception as e:
                logging.warning(f"Selector {selector} failed: {e}")
        
        if google_login_button:
            logging.info("Found Google login button, attempting to click...")
            # Try different click methods
            try:
                google_login_button.click()
            except:
                try:
                    driver.execute_script("arguments[0].click();", google_login_button)
                except:
                    actions = ActionChains(driver)
                    actions.move_to_element(google_login_button).click().perform()
                    
            time.sleep(5)
            
            # Now navigate to the home page where cookies were captured
            logging.info("Navigating to home page...")
            driver.get("https://app.apollo.io/")
            time.sleep(3)
            
            # Apply cookies
            apply_cookies(driver, cookies)
            
            # Refresh to apply cookies
            driver.refresh()
            time.sleep(5)
            
            # Try to find navigation menu
            logging.info("Waiting for navigation menu...")
            start_time = time.time()
            while time.time() - start_time < 30:  # 30 second timeout
                try:
                    # Check for navigation menu
                    menu = driver.find_elements(By.CSS_SELECTOR, "div[data-tour='prospect_enrich']")
                    if menu:
                        logging.info("Found navigation menu!")
                        return
                    time.sleep(1)
                except Exception as e:
                    logging.warning(f"Error while waiting for menu: {e}")
                    continue
            
            # If we get here, menu wasn't found
            logging.error("Navigation menu not found after timeout")
            raise TimeoutException("Navigation menu not found")
            
        else:
            raise Exception("Could not find Google login button with any selector")
            
    except Exception as e:
        logging.error(f"Error in cookie loading process: {e}")
        raise

def save_page_screenshot(driver, page_number, base_folder="/home/wynt3r/JobSearch/company_people_extractions/apollo_extractions/apollo_html"):
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

def main():
    driver = None
    display = None
    try:
        display = setup_virtual_display()
        driver = setup_driver()
        
        # Add random delay before starting
        add_random_delays()
        
        # Load cookies instead of manual login
        load_cookies(driver)
        
        # Navigate directly to Apollo
        driver.get("https://app.apollo.io/#/login")
        time.sleep(5)  # Wait for redirect after cookie auth
        
        # Wait for navigation menu and click Companies
        logging.info("Waiting for navigation menu...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-tour='prospect_enrich']"))
        )

        logging.info("Looking for Companies link...")
        companies_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-tour='prospect_enrich'] a#side-nav-companies"))
        )

        logging.info("Clicking Companies link...")
        driver.execute_script("arguments[0].click();", companies_link)
        time.sleep(5)

        # Add this section to modify the column width
        logging.info("Adjusting column width...")
        try:
            # Inject JavaScript to modify the 5th column width
            column_width_script = """
            let rows = document.getElementsByClassName('zp_hWv1I');
            if (rows.length > 0) {
                let fifthColumn = rows[0].children[4];
                if (fifthColumn) {
                    fifthColumn.style.width = '650px';
                }
            }
            """
            driver.execute_script(column_width_script)
            time.sleep(2)  # Give time for the change to apply
            logging.info("Column width adjusted successfully")
            
            # Take screenshot after column modification
            save_page_screenshot(driver, "initial")
            
        except Exception as e:
            logging.warning(f"Failed to adjust column width: {e}")

        # Update output file path
        output_dir = "/home/wynt3r/JobSearch/company_people_extractions/apollo_extractions/companies"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'apollo_records.csv')
        
        file_exists = os.path.isfile(output_file)
        with open(output_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Name", "Title", "Company", "Email", "Links",
                               "Location", "# Employees", "Industry", "Keywords"])

        # Process pages
        max_pages = int(os.getenv('MAX_PAGES', 1))
        page_count = 1
        total_records = 0

        while page_count <= max_pages:
            try:
                logging.info(f"Processing page {page_count}...")
                
                # Save the HTML for this page
                save_page_html(driver, page_count)
                
                try:
                    print(f"Processing page {page_count}...")
                    # Wait until all rows on the page are present
                    records = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@id, 'table-row-')]")
                                                            ))

                    for index in range(len(records)):
                        try:
                            record_xpath = f"//div[@id='table-row-{index}']"
                            record = driver.find_element(By.XPATH, record_xpath)
                            try:
                                access_button = record.find_element(By.XPATH, ".//button[./span[text()='Access email']]")
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", access_button)
                                time.sleep(random.uniform(10, 30))
                                driver.execute_script("arguments[0].click();", access_button)
                                time.sleep(random.uniform(3, 6))
                            except NoSuchElementException:
                                pass

                            # Collect data for the record
                            try:
                                company = record.find_element(By.XPATH, ".//a[@data-link-variant='default']/span").text
                            except NoSuchElementException:
                                email = "N/A"

                            # Updated link extraction logic to handle missing elements
                            try:
                                links_element = record.find_element(By.XPATH, ".//a[contains(@href, 'linkedin')]")
                                links = links_element.get_attribute("href")
                            except NoSuchElementException:
                                links = "N/A"

                            # Added safety check to collect location and other fields that might be missing
                            try:
                                location = record.find_element(
                                    By.XPATH, ".//span[contains(@class, 'zp_xvo3G') and contains(text(), ',')]").text
                            except NoSuchElementException:
                                location = "N/A"

                            try:
                                employees = record.find_element(By.XPATH, ".//span[contains(@data-count-size, 'small')]").text
                            except NoSuchElementException:
                                employees = "N/A"

                            try:
                                # First check for visible industry
                                industry_elements = record.find_elements(By.XPATH, ".//span[contains(@class, 'zp_CEZf9')]")
                                visible_industries = []
                                
                                for element in industry_elements:
                                    industry_text = element.text
                                    if industry_text and not industry_text.startswith('+'):  # Only add if not a count indicator
                                        visible_industries.append(industry_text)
                                
                                # Check for "+X" button in this specific row
                                more_industries_button = record.find_elements(
                                    By.XPATH, 
                                    ".//button[contains(@class, 'zp_qe0Li')]//span[contains(@class, 'zp_CEZf9') and starts-with(text(), '+')]"
                                )
                                
                                if more_industries_button:
                                    try:
                                        # Scroll the button into view and click
                                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", more_industries_button[0])
                                        time.sleep(0.5)
                                        driver.execute_script("arguments[0].click();", more_industries_button[0])
                                        time.sleep(1)  # Wait for popup
                                        
                                        # Find the most recently created floating-ui div
                                        popup_industries = WebDriverWait(driver, 5).until(
                                            EC.presence_of_all_elements_located(
                                                (By.XPATH, "//div[contains(@class, 'zp_RF8MX')]//button//span[@class='zp_CEZf9']")
                                            )
                                        )
                                        
                                        # Add popup industries to our list
                                        for industry in popup_industries:
                                            industry_text = industry.text
                                            if industry_text and industry_text not in visible_industries and not industry_text.startswith('+'):
                                                visible_industries.append(industry_text)
                                        
                                        # Click elsewhere to close popup
                                        driver.execute_script("""
                                            document.elementFromPoint(0, 0).click();
                                        """)
                                        time.sleep(0.5)
                                        
                                    except Exception as e:
                                        logging.warning(f"Error getting additional industries: {e}")
                                
                                # Join all industries with semicolon
                                industry = '; '.join(visible_industries) if visible_industries else "N/A"
                                
                            except NoSuchElementException:
                                industry = "N/A"

                            try:
                                keywords = record.find_element(
                                    By.XPATH, ".//div[contains(@class, 'zp_ofXB9')]//span[contains(@class, 'zp_CEZf9')]").text
                            except NoSuchElementException:
                                keywords = "N/A"

                            # Write data to CSV file
                            with open(output_file, mode='a', newline='', encoding='utf-8') as file:
                                writer = csv.writer(file)
                                writer.writerow([company, links, location, employees, industry])

                            total_records += 1
                            print(f"Collected record {total_records}: {company}")
                        except NoSuchElementException as e:
                            print(f"Error processing record {index}: {e}")
                            continue

                    # Step 4: Click the next page button if available
                    next_page_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//i[contains(@class, 'apollo-icon-chevron-arrow-right')]")
                                                    ))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_page_button)
                    driver.execute_script("arguments[0].click();", next_page_button)
                    time.sleep(random.uniform(10, 30))
                    page_count += 1
                except (NoSuchElementException, TimeoutException, ElementClickInterceptedException) as e:
                    print(f"No more pages available or an error occurred: {e}")
                    break
                
                # Click next page
                next_page_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//i[contains(@class, 'apollo-icon-chevron-arrow-right')]"))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_page_button)
                time.sleep(random.uniform(1, 2))
                driver.execute_script("arguments[0].click();", next_page_button)
                time.sleep(random.uniform(10, 15))
                page_count += 1
                
            except (NoSuchElementException, TimeoutException, ElementClickInterceptedException) as e:
                logging.error(f"Error processing page {page_count}: {e}")
                # Save HTML on error for debugging
                save_page_html(driver, f"{page_count}_error")
                break

        logging.info(f"Total pages processed: {page_count - 1}")
        logging.info(f"Total records collected: {total_records}")

    except Exception as e:
        logging.error(f"Script failed: {e}")
        # Save screenshot if possible
        try:
            if driver:
                driver.save_screenshot("error_screenshot.png")
                logging.info("Error screenshot saved")
        except:
            pass
        raise
    finally:
        if driver:
            driver.quit()
            logging.info("Driver closed")
        if display:
            display.stop()
            logging.info("Virtual display stopped")

if __name__ == "__main__":
    main()
