"""
Base class for form fillers.
"""
import time
import random
import logging
from abc import ABC, abstractmethod
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class BaseFormFiller(ABC):
    """Base class for all form fillers."""
    
    def __init__(self, driver, config):
        """
        Initialize the form filler.
        
        Args:
            driver: Selenium WebDriver instance
            config: User configuration dictionary
        """
        self.driver = driver
        self.config = config
        self.wait = WebDriverWait(driver, 15)
        self.logger = logging.getLogger(__name__)
    
    def random_delay(self, min_seconds=0.5, max_seconds=2.0):
        """Add random delay to mimic human behavior."""
        time.sleep(random.uniform(min_seconds, max_seconds))
    
    def find_element_safe(self, selectors, timeout=10):
        """
        Try multiple selectors to find an element.
        
        Args:
            selectors: List of tuples (By, selector) or single tuple
            timeout: Maximum time to wait
            
        Returns:
            WebElement or None
        """
        if not isinstance(selectors, list):
            selectors = [selectors]
        
        for by, selector in selectors:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, selector))
                )
                return element
            except TimeoutException:
                continue
        
        return None
    
    def fill_text_field(self, selectors, value, clear_first=True):
        """
        Fill a text input field.
        
        Args:
            selectors: CSS selector or list of selectors
            value: Value to fill
            clear_first: Whether to clear the field first
            
        Returns:
            bool: True if successful
        """
        if not value:
            return False
        
        element = self.find_element_safe(selectors if isinstance(selectors, list) else [selectors])
        if not element:
            self.logger.warning(f"Could not find text field with selectors: {selectors}")
            return False
        
        try:
            if clear_first:
                element.clear()
            self.random_delay(0.2, 0.5)
            element.send_keys(value)
            self.random_delay(0.3, 0.7)
            return True
        except Exception as e:
            self.logger.error(f"Error filling text field: {e}")
            return False
    
    def select_dropdown(self, selectors, value, match_type='exact'):
        """
        Select an option from a dropdown.
        
        Args:
            selectors: CSS selector or list of selectors
            value: Value to select
            match_type: 'exact', 'contains', or 'starts_with'
            
        Returns:
            bool: True if successful
        """
        if not value:
            return False
        
        element = self.find_element_safe(selectors if isinstance(selectors, list) else [selectors])
        if not element:
            self.logger.warning(f"Could not find dropdown with selectors: {selectors}")
            return False
        
        try:
            # Try using Select class first (for standard HTML selects)
            try:
                select = Select(element)
                options = select.options
                for option in options:
                    option_text = option.text.strip()
                    if match_type == 'exact' and option_text == value:
                        select.select_by_visible_text(value)
                        self.random_delay(0.3, 0.7)
                        return True
                    elif match_type == 'contains' and value in option_text:
                        select.select_by_visible_text(option_text)
                        self.random_delay(0.3, 0.7)
                        return True
                    elif match_type == 'starts_with' and option_text.startswith(value):
                        select.select_by_visible_text(option_text)
                        self.random_delay(0.3, 0.7)
                        return True
            except:
                # If Select doesn't work, try clicking and selecting
                element.click()
                self.random_delay(0.5, 1.0)
                
                # Look for option elements
                option_selectors = [
                    (By.XPATH, f"//option[contains(text(), '{value}')]"),
                    (By.XPATH, f"//li[contains(text(), '{value}')]"),
                    (By.XPATH, f"//div[contains(text(), '{value}')]")
                ]
                
                option = self.find_element_safe(option_selectors, timeout=5)
                if option:
                    option.click()
                    self.random_delay(0.3, 0.7)
                    return True
            
            self.logger.warning(f"Could not find option '{value}' in dropdown")
            return False
        except Exception as e:
            self.logger.error(f"Error selecting dropdown: {e}")
            return False
    
    def upload_file(self, selectors, file_path):
        """
        Upload a file to a file input.
        
        Args:
            selectors: CSS selector or list of selectors
            file_path: Path to the file to upload
            
        Returns:
            bool: True if successful
        """
        import os
        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {file_path}")
            return False
        
        element = self.find_element_safe(selectors if isinstance(selectors, list) else [selectors])
        if not element:
            self.logger.warning(f"Could not find file input with selectors: {selectors}")
            return False
        
        try:
            # File inputs typically have type="file"
            if element.tag_name != 'input' or element.get_attribute('type') != 'file':
                # Try to find a hidden file input and trigger click on visible element
                self.logger.warning("Element is not a file input, attempting workaround")
            
            element.send_keys(file_path)
            self.random_delay(1.0, 2.0)  # File uploads take time
            return True
        except Exception as e:
            self.logger.error(f"Error uploading file: {e}")
            return False
    
    def click_button(self, selectors, wait_after=True):
        """
        Click a button or clickable element.
        
        Args:
            selectors: CSS selector or list of selectors
            wait_after: Whether to wait after clicking
            
        Returns:
            bool: True if successful
        """
        element = self.find_element_safe(selectors if isinstance(selectors, list) else [selectors])
        if not element:
            self.logger.warning(f"Could not find button with selectors: {selectors}")
            return False
        
        try:
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            self.random_delay(0.3, 0.7)
            
            # Try JavaScript click first (more reliable)
            self.driver.execute_script("arguments[0].click();", element)
            if wait_after:
                self.random_delay(1.0, 2.0)
            return True
        except Exception as e:
            self.logger.error(f"Error clicking button: {e}")
            return False
    
    def check_checkbox(self, selectors, checked=True):
        """
        Check or uncheck a checkbox.
        
        Args:
            selectors: CSS selector or list of selectors
            checked: True to check, False to uncheck
            
        Returns:
            bool: True if successful
        """
        element = self.find_element_safe(selectors if isinstance(selectors, list) else [selectors])
        if not element:
            self.logger.warning(f"Could not find checkbox with selectors: {selectors}")
            return False
        
        try:
            current_state = element.is_selected()
            if current_state != checked:
                element.click()
                self.random_delay(0.3, 0.7)
            return True
        except Exception as e:
            self.logger.error(f"Error checking checkbox: {e}")
            return False
    
    @abstractmethod
    def fill_application(self, job_url, job_data=None):
        """
        Fill out the job application form.
        
        Args:
            job_url: URL of the job posting
            job_data: Optional dictionary with job information
            
        Returns:
            dict: Result with 'success' (bool) and 'message' (str)
        """
        pass
    
    @abstractmethod
    def detect_application_page(self):
        """
        Detect if we're on an application page.
        
        Returns:
            bool: True if on application page
        """
        pass


