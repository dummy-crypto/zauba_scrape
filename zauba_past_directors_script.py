#!/usr/bin/env python
# coding: utf-8

from tqdm import tqdm
import pandas as pd
from sqlalchemy import create_engine
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import re
from urllib.parse import quote
import pyodbc
import sqlalchemy

# Define your database engine
engine = create_engine('mssql+pyodbc://SAL_USER01:%s@172.16.22.25:1433/SAL_DB?driver=ODBC+Driver+17+for+SQL+Server' % quote('Sal@123'))

# Log errors to a text file
def log_error(error_message):
    with open('error_log.txt', 'a') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {error_message}\n")

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    #chrome_options.add_argument("--enable-logging")
    #chrome_options.add_argument("--v=1")
    chrome_options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"  # Ensure correct Chrome binary location
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Function to log in to Zaubacorp
def login_to_zaubacorp(driver, username, password):
    try:
        driver.get('https://www.zaubacorp.com/company-directors/AM-DAILY-SERVICES-OPC-PRIVATE-LIMITED/U74999MH2021OPC368405')
        print(f"Page title: {driver.title}")

        sign_in_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.LINK_TEXT, "Login")))
        sign_in_button.click()

        captcha_div = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[@class='form-type-textfield form-item-captcha-response form-item form-group']")))
        captcha_text = captcha_div.text
        print(f"Captcha text: {captcha_text}")

        captcha_answer = solve_captcha(captcha_text)
        if captcha_answer is None:
            log_error("Failed to solve captcha.")
            return False

        print(f"Captcha answer: {captcha_answer}")

        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//input[@name='name']"))).send_keys(username)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//input[@name='pass']"))).send_keys(password)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//input[@name='captcha_response']"))).send_keys(str(captcha_answer))

        login_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='edit-submit']")))
        login_button.click()
        print("Login form submitted.")
        return True
    except Exception as e:
        log_error(f"Error during login process: {e}")
        return False

def solve_captcha(captcha_text):
    try:
        captcha_question = re.search(r'(\d+ [\+\-\*/] \d+)', captcha_text)
        if captcha_question:
            expression = captcha_question.group()
            result = eval(expression)
            return result
    except Exception as e:
        log_error(f"Error solving captcha: {e}")
    return None

# Initialize the WebDriver outside the loop
driver = create_driver()

# Log in to Zaubacorp
login_success = login_to_zaubacorp(driver, 'dummy3', 'Sal@2021')
if not login_success:
    driver.quit()
    exit()

# Process each URL after logging in
director_data = []

for url in df['Website'][0:100]:
    try:
        time.sleep(1)
        driver.get(url)
        url_parts = url.split('/')
        company_name = url_parts[-2].encode('utf-8').decode('utf-8')
        cin = url_parts[-1].encode('utf-8').decode('utf-8')
        past_directors_section = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Past Directors')]"))
        )
        director_details = past_directors_section.find_element(By.XPATH, "./following-sibling::table")

        rows = director_details.find_elements(By.TAG_NAME, "tr")
        for row in rows[1:]:
            columns = row.find_elements(By.TAG_NAME, "td")
            din = columns[0].text if len(columns) > 0 else None
            name = columns[1].text if len(columns) > 1 else None
            designation = columns[2].text if len(columns) > 2 else None
            start_date = columns[3].text if len(columns) > 3 else None
            end_date = columns[4].text if len(columns) > 4 else None

            director_data.append({
                'DIN': din,
                'Name': name.encode('utf-8').decode('utf-8') if name else None,
                'Designation': designation.encode('utf-8').decode('utf-8') if designation else None,
                'Start Date': start_date.encode('utf-8').decode('utf-8') if start_date else None,
                'End Date': end_date.encode('utf-8').decode('utf-8') if end_date else None,
                'CIN': cin,
                'Company_Name': company_name
            })
    except (WebDriverException, TimeoutException) as e:
        error_message = f"Error occurred for {url}"
        log_error(error_message)
        continue

# Create a DataFrame from the collected data
final = pd.DataFrame(director_data)

# Close the driver
driver.quit()

try:
    # Insert data into the SQL database
    final.to_sql('zauba_past_director', engine, if_exists='append', index=False)
    print('Data inserted into DB successfully.')
except Exception as e:
    log_error(f"Error inserting data into DB: {e}")
