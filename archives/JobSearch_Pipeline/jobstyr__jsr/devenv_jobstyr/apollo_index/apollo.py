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

def main():
    driver = None
    display = None
    try:
        # Setup virtual display and driver
        display = setup_virtual_display()
        driver = setup_driver()
        
        # Add random delay before starting
        add_random_delays()
        
        # Open or create CSV file
        output_file = 'apollo_records.csv'
        file_exists = os.path.isfile(output_file)
        with open(output_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Name", "Title", "Company", "Email", "Links",
                            "Location", "# Employees", "Industry", "Keywords"])

        # Login to Apollo with better error handling
        retries = 3
        for attempt in range(retries):
            try:
                logging.info("Navigating to Apollo login page...")
                driver.get("https://app.apollo.io/#/login")
                time.sleep(random.uniform(3, 5))
                
                # Wait for login page to load
                logging.info("Waiting for login form...")
                email_input = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='email'][placeholder='Work Email']"))
                )
                
                logging.info("Entering email...")
                email_input.send_keys(APOLLO_EMAIL[0:3])
                add_random_delays()
                email_input.send_keys(APOLLO_EMAIL[3:6])
                add_random_delays()
                email_input.send_keys(APOLLO_EMAIL[6:])
                add_random_delays()

                logging.info("Entering password...")
                password_input = driver.find_element(By.CSS_SELECTOR, "input[name='password'][placeholder='Enter your password']")
                password_input.send_keys(APOLLO_PASSWORD)
                time.sleep(random.uniform(1, 3))

                logging.info("Clicking login button...")
                login_button = driver.find_element(By.CSS_SELECTOR, "button[data-cy='login-button']")
                driver.execute_script("arguments[0].click();", login_button)
                
                # Wait for login to complete and dashboard to load
                logging.info("Waiting for login to complete...")
                time.sleep(10)  # Give more time for the page to load
                
                # Check if login was successful
                logging.info("Checking login status...")
                try:
                    # After login, wait for navigation and click People link
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
                    break
                    
                except TimeoutException:
                    logging.error("Failed to find navigation elements after login")
                    if attempt < retries - 1:
                        logging.info("Retrying login process...")
                        continue
                    else:
                        raise
                        
            except WebDriverException as e:
                if attempt < retries - 1:
                    logging.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(random.uniform(3, 7))
                else:
                    logging.error(f"Failed to complete login process after {retries} attempts: {e}")
                    raise

        # Save page source for debugging
        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logging.info("Saved page source for debugging")

        # Process pages
        max_pages = int(os.getenv('MAX_PAGES', 1))
        page_count = 1
        total_records = 0

        while page_count <= max_pages:
            try:
                logging.info(f"Processing page {page_count}...")
                
                # Save the HTML for this page
                save_page_html(driver, page_count)
                
                # [Rest of your existing page processing code...]
                # Note: Keep your existing record processing logic here
                
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
