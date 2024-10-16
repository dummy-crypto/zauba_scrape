from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Set Chrome binary location
chrome_options.binary_location = "/usr/bin/google-chrome"

# Set ChromeDriver location
service = Service("/usr/local/bin/chromedriver")

# Initialize WebDriver
driver = webdriver.Chrome(service=service, options=chrome_options)
