from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import csv
import time

# LinkedIn credentials
LINKEDIN_USERNAME = "vasily.souzdenkov@gmail.com"
LINKEDIN_PASSWORD = "Godric23!"

# Initialize WebDriver with options
options = Options()
options.add_argument('--log-level=3')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')
options.add_argument('--no-sandbox')
options.add_argument("--headless")  # Run browser in headless mode

# Set up WebDriver and disable detection
driver = webdriver.Chrome(service=Service("chromedriver.exe"), options=options)
script_to_disable_webdriver = "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': script_to_disable_webdriver})


def linkedin_login(driver):
    """
    Logs into LinkedIn using the provided credentials.
    """
    driver.get("https://www.linkedin.com/login")
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        driver.find_element(By.ID, "username").send_keys(LINKEDIN_USERNAME)
        driver.find_element(By.ID, "password").send_keys(LINKEDIN_PASSWORD)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "global-nav")))
        print("Logged into LinkedIn successfully.")
    except TimeoutException:
        print("Error: Login failed. Please check your credentials or the page structure.")


def extract_profile_data(profile_url):
    """
    Extracts profile data from the LinkedIn profile page, focusing on job experience companies based on date spans.
    """
    wait = WebDriverWait(driver, 15)  # Initialize the WebDriverWait object
    driver.get(profile_url)
    time.sleep(10)  # Allow the page to load
    data = {}

    try:
        # Extract full name
        data['full_name'] = driver.find_element(By.CSS_SELECTOR, "h1.text-heading-xlarge.inline.t-24").text.strip()
    except Exception:
        data['full_name'] = None

    try:
        # Extract role title
        role_title = driver.find_element(By.CSS_SELECTOR, "div.text-body-medium.break-words").text.strip()
        data['role_title'] = role_title.split(' at ')[0]
    except Exception:
        data['role_title'] = None

    try:
        # Extract location
        data['location'] = driver.find_element(By.CSS_SELECTOR, "span.text-body-small.inline.t-black--light").text.strip()
    except Exception:
        data['location'] = None

    try:
        # Extract current company
        company_text = driver.find_element(By.CSS_SELECTOR, "div.text-body-medium.break-words").text.strip()
        data['company_current'] = company_text.split(' at ')[-1]
    except Exception:
        data['company_current'] = None

    try:
        # Define the full XPaths for the top 3 companies
        xpaths = [
            "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[4]/div[3]/ul/li[2]/div/div[2]/div[1]/a/div/div/div/div/span[1]",
            "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[4]/div[3]/ul/li[3]/div/div[2]/div[1]/div/span[1]/span[1]"
        ]

        # Extract company names
        companies = []
        for xpath in xpaths:
            try:
                company_element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                print(company_element)
                company_name = company_element.text.strip()
                if company_name:  # Ensure it's not empty
                    companies.append(company_name)
            except Exception as e:
                print(f"Error extracting company at {xpath}: {e}")

        # Store the extracted company names
        data['company_all'] = ", ".join(companies) if companies else None

    except Exception as e:
        print(f"Error locating experience section or extracting data: {e}")
        data['company_all'] = None

    return data



# Read LinkedIn URLs from CSV
input_csv = "linkedin_profiles.csv"  # Replace with your input file
output_csv = "linkedin_profiles_output.csv"  # Replace with your output file

linkedin_urls = []
with open(input_csv, 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        linkedin_urls.append(row['linkedin_profiles'])

# Login to LinkedIn
linkedin_login(driver)

# Extract data and write to CSV
with open(output_csv, 'w', newline='', encoding='utf-8') as file:
    fieldnames = ['full_name', 'role_title', 'location', 'company_current', 'company_all']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    
    for url in linkedin_urls:
        print(f"Processing: {url}")
        try:
            profile_data = extract_profile_data(url)
            writer.writerow(profile_data)
        except Exception as e:
            print(f"Failed to process {url}: {e}")

driver.quit()