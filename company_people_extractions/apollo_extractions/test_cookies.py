import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def test_cookie_loading(cookie_file='company_people_extractions/apollo_extractions/apollo_cookies.txt'):
    """Test loading and parsing of the cookie file."""
    try:
        logging.info(f"Attempting to load cookies from {cookie_file}")
        
        with open(cookie_file, 'r') as file:
            content = file.read().strip()
            logging.info("Cookie file read successfully")
            
            # Print raw content for debugging
            logging.info(f"Raw content first 200 chars: {content[:200]}")
            
            # Try parsing the JSON
            cookies = json.loads(content)
            logging.info(f"Successfully parsed {len(cookies)} cookies")
            
            # Print some cookie info for verification
            for cookie in cookies[:2]:  # Just show first two cookies
                logging.info(f"Sample cookie - Name: {cookie.get('name')}, Domain: {cookie.get('domain')}")
            
            return cookies
            
    except FileNotFoundError:
        logging.error(f"Cookie file not found: {cookie_file}")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing cookies JSON: {e}")
        # Print the problematic content
        logging.error(f"Content causing error: {content[:200]}...")  # Show first 200 chars
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise

if __name__ == "__main__":
    test_cookie_loading() 