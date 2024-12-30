import json
import logging
import os

def load_cookie_data(cookie_file='linkedin_cookies.txt'):
    """Load cookie data from external file."""
    try:
        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cookie_path = os.path.join(current_dir, cookie_file)
        
        with open(cookie_path, 'r') as file:
            content = file.read().strip()
            logging.info("Cookie file read successfully")
            
            # Clean up the content without logging it
            cookie_json = content.replace('\n', '').replace('    ', '')
            
            # Parse the JSON
            cookies = json.loads(cookie_json)
            logging.info(f"Successfully parsed {len(cookies)} cookies")
            return cookies
            
    except FileNotFoundError:
        logging.error(f"Cookie file not found: {cookie_path}")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing cookies JSON: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error loading cookies: {e}")
        raise