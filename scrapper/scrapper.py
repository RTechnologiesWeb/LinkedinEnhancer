import logging
import os
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv
import requests
from requests.exceptions import ProxyError, Timeout, RequestException

app = Flask(__name__)
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

cloudinary.config(
    cloud_name="dm7uq1adt",
    api_key="246721327163695",
    api_secret="Pozr913oXcnPC6P4JrsSjkuA6oA"
)

class ScrapeException(Exception):
    """Custom exception for scrape errors"""
    pass

def is_valid_proxy(proxy):
    """
    Check if the provided proxy is valid.
    """
    try:
        response = requests.get('https://www.google.com', proxies={"http": proxy, "https": proxy}, timeout=5)
        if response.status_code == 200:
            logger.info("Proxy is valid: %s", proxy)
            return True
        else:
            logger.warning("Proxy returned non-200 status code: %d", response.status_code)
            return False
    except ProxyError:
        logger.error("ProxyError: The proxy is not valid or not reachable.")
        return False
    except Timeout:
        logger.error("Timeout: The proxy timed out.")
        return False
    except RequestException as e:
        logger.error("RequestException: %s", str(e))
        return False
def login_to_linkedin(driver, username, password):
    driver.get("https://www.linkedin.com/login")
    
    # Enter username
    email_element = driver.find_element(By.ID, "username")
    email_element.send_keys(username)
    
    # Enter password
    password_element = driver.find_element(By.ID, "password")
    password_element.send_keys(password)
    
    # Submit the login form
    sign_in_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    sign_in_button.click()
    
    time.sleep(5)  # Wait for login to complete
class Scrapper:
    def __init__(self, proxy=None, username=None, password=None):
        logger.info("Initializing Scrapper")
        self.chrome_options = Options()
        # self.chrome_options.add_argument("--start-maximized")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.chrome_options.add_argument('--log-level 3') 
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_argument("--window-size=1920,1080")

        if username and password:
            login_to_linkedin(self.driver, username, password)
        else:
            logger.warning("No LinkedIn credentials provided; attempting to scrape without login.")


    def take_full_page_screenshot(self, driver):
        """Take a full-page screenshot using Selenium."""
        logger.info("Taking full-page screenshot")
        total_width = driver.execute_script("return document.body.scrollWidth")
        total_height = driver.execute_script("return document.body.scrollHeight")
        driver.set_window_size(total_width, total_height)
        time.sleep(2)  # Let the window resize

        screenshot = driver.get_screenshot_as_png()
        logger.info("Screenshot taken successfully")
        return screenshot

    def upload_to_cloudinary(self, image_data):
        """Upload the screenshot to Cloudinary and return the URL."""
        logger.info("Uploading screenshot to Cloudinary")
        upload_result = cloudinary.uploader.upload(image_data, folder="scraper_screenshots/")
        logger.info("Screenshot uploaded successfully: %s", upload_result['secure_url'])
        return upload_result['secure_url']

    def scrape(self, url) -> dict:
        """Scrapes LinkedIn profile data."""
        logger.info("Starting scrape for URL: %s", url)
        driver = webdriver.Chrome(options=self.chrome_options)

        driver.get(url)
        time.sleep(3)

        tries = 0
        while driver.current_url != url:
            print(driver.current_url)
            logger.warning("Redirected to login page, retrying... Attempt: %d", tries + 1)
            if tries > 50:
                driver.quit()
                logger.error("Exceeded maximum retry attempts. Scraping failed.")
                raise ScrapeException("Could not scrape page. \nRequest timedout, Please try with proxy as linkedin is blocking your request.")

            driver.get(url)
            time.sleep(2)
            tries += 1
            
        time.sleep(5)
        try:
            logger.info("Attempting to close sign-in popups")
            driver.find_element(by=By.CSS_SELECTOR, value='#base-contextual-sign-in-modal > div > section > button').click()
        except:
            try:
                driver.find_element(by=By.CSS_SELECTOR, value='#public_profile_contextual-sign-in > div > section > button').click()
            except:
                logger.warning("No sign-in popups found")
                pass

        time.sleep(2)
        logger.info("Extracting profile information")
        about = driver.find_element(by=By.CSS_SELECTOR, value='section.core-section-container:nth-child(2) > div:nth-child(2) > p:nth-child(1)').text
        logger.info("About section found: %s", about)
        headline = driver.find_element(by=By.CSS_SELECTOR, value='.top-card-layout__headline').text
        logger.info("Headline found: %s", headline)

        projectDetailsLi = driver.find_elements(by=By.CSS_SELECTOR, value='.personal-project')
        projDetails = '\n'.join([project.text.strip() for project in projectDetailsLi])
        logger.info("Projects found: %s", projDetails)

        experienceLi = driver.find_elements(by=By.CSS_SELECTOR, value='.experience-item')
        experience = '\n'.join([exp.text.strip() for exp in experienceLi])
        logger.info("Experience found: %s", experience)

        certificationLi = driver.find_elements(by=By.CSS_SELECTOR, value='.experience-item')
        certificationDetails = '\n'.join([cert.text.strip() for cert in certificationLi])
        logger.info("Certifications found: %s", certificationDetails)

        educationDetailsLis = driver.find_elements(by=By.CSS_SELECTOR, value='.education__list-item')
        eduDetails = '\n'.join([edu.text.strip() for edu in educationDetailsLis])
        logger.info("Education details found: %s", eduDetails)

        # Take full-page screenshot
        screenshot = self.take_full_page_screenshot(driver)
        driver.quit()

        # Upload screenshot to Cloudinary
        screenshot_url = self.upload_to_cloudinary(screenshot)

        return {
            'about': about,
            'headline': headline,
            'projects': projDetails,
            'experience': experience,
            'certifications': certificationDetails,
            'education': eduDetails,
            'screenshot_url': screenshot_url
        }

@app.route('/', methods=['GET'])
def home():
    logger.info("Home endpoint accessed")
    return (
        "<h1>Hello, World!</h1>"
        "<p>Welcome to the Scraper API!</p>"
        "<p>Use the POST operation on /scrape endpoint with a 'url' query parameter to scrape LinkedIn profile data.</p>"
        "<p>Example: /scrape?url=https://www.linkedin.com/in/some-profile</p>"
        "<p>To use Proxy, send the request as body-> raw-> json{ 'url: https://www.linkedin.com/in/some-profile , proxy : http://user:password@proxy-server:port'}"
    )

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        logger.info("Scrape endpoint accessed")
        data = request.json
        url = data.get('url')
        proxy = data.get('proxy')  # Expecting proxy in the request data, e.g., "http://user:password@proxy-server:port"


        if not url:
            logger.error("No URL provided")
            return jsonify({'error': 'URL is required'}), 400

        if proxy:
            if not is_valid_proxy(proxy):
                logger.error("Invalid proxy provided: %s", proxy)
                return jsonify({'error': 'Invalid proxy provided'}), 400
            else:
                logger.info("Using valid proxy: %s", proxy)
        scrapper = Scrapper(proxy=proxy, )
        result = scrapper.scrape(url)

        logger.info("Scraping successful")
        return jsonify({
            'status': 'success',
            'data': result
        })
    
    except ScrapeException as e:
        logger.error("ScrapeException occurred: %s", str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
    except Exception as e:
        logger.error("An unexpected error occurred: %s", str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == "__main__":
    logger.info("Starting Flask app")
    app.run(host='0.0.0.0', port=15000)
