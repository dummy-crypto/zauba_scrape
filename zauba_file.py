# %%
from tqdm import tqdm
import pandas as pd
from sqlalchemy import create_engine
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from selenium.common.exceptions import TimeoutException
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException
import re
from urllib.parse import quote
import pandas as pd
import sqlalchemy

column_names = [
    'Index', 
    'Company_ID', 
    'Company_Name', 
    'Location', 
    'Status', 
    'Website'
]
df = pd.read_csv(
    r"details.csv", 
    delimiter='\t', 
    header=None, 
    names=column_names, 
    on_bad_lines='skip'
)

df['Website'] = df['Website'].str.replace(
    r'/company/', '/company-directors/', regex=False
)

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome()
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")


def solve_captcha(captcha_text):
    try:
        captcha_question = re.search(r'(\d+ [\+\-\*/] \d+)', captcha_text)
        if captcha_question:
            expression = captcha_question.group()
            result = eval(expression)
            return result
    except Exception as e:
        print(f"Error solving captcha: {e}")
    return None


final=pd.DataFrame()
 
driver.get('https://www.zaubacorp.com/company-directors/AM-DAILY-SERVICES-OPC-PRIVATE-LIMITED/U74999MH2021OPC368405')  # Replace with the actual login URL
print(f"Page title: {driver.title}")
 
sign_in_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT, "Login")))
sign_in_button.click()

captcha_div = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='form-type-textfield form-item-captcha-response form-item form-group']")))
captcha_text = captcha_div.text
print(f"Captcha text: {captcha_text}")
 
captcha_answer = solve_captcha(captcha_text)
if captcha_answer is None:
    print("Failed to solve captcha.")
    driver.quit()
    exit()
 
print(f"Captcha answer: {captcha_answer}")

WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//input[@name='name']"))).send_keys('dummy3')
WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//input[@name='pass']"))).send_keys('Sal@2021')
WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//input[@name='captcha_response']"))).send_keys(str(captcha_answer))
 
# Submit the login form
login_button = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='edit-submit']")))
login_button.click()
print("Login form submitted.")

director_data = []

for url in df['Website'][0:50]:
    driver.get(url)
    url_parts = url.split('/')
    company_name = url_parts[-2]  # Value between last and second last
    cin = url_parts[-1]
 
    try:
        past_directors_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Past Directors')]"))
        )
        director_details = past_directors_section.find_element(By.XPATH, "./following-sibling::table")

        rows = director_details.find_elements(By.TAG_NAME, "tr")
        for row in rows[1:]:  # Skip header row
            columns = row.find_elements(By.TAG_NAME, "td")
            din = columns[0].text if len(columns) > 0 else None
            name = columns[1].text if len(columns) > 1 else None
            designation = columns[2].text if len(columns) > 2 else None
            start_date = columns[3].text if len(columns) > 3 else None
            end_date = columns[4].text if len(columns) > 4 else None  # Adjusted index
 
            director_data.append({
                'DIN': din,
                'Name': name,
                'Designation': designation,
                'Start Date': start_date,
                'End Date': end_date,
                'CIN':cin,
                'Company_Name':company_name
            })
    except TimeoutException:
        print("Failed to find the past directors section on this page.")

final = pd.DataFrame(director_data)
 

driver.quit()
final.to_csv(r'data_dummy.csv')
