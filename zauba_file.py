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

# %%
column_names = [
    'Index', 
    'Company_ID', 
    'Company_Name', 
    'Location', 
    'Status', 
    'Website'
]
 
# Read the CSV with custom headers
df = pd.read_csv(
    r"details.csv", 
    delimiter='\t', 
    header=None, 
    names=column_names, 
    on_bad_lines='skip'
)
 
# Replace the URLs
df['Website'] = df['Website'].str.replace(
    r'/company/', '/company-directors/', regex=False
)

# %%
# demo=df.head()
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome()
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")

# %%
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

# %%
final=pd.DataFrame()
 
# engine=sqlalchemy.create_engine('mssql+pyodbc://test:%s@10.20.1.152:1433/SAL_DB?driver=ODBC+Driver+17+for+SQL+Server' % quote('test'))
# Navigate to the login page
driver.get('https://www.zaubacorp.com/company-directors/AM-DAILY-SERVICES-OPC-PRIVATE-LIMITED/U74999MH2021OPC368405')  # Replace with the actual login URL
print(f"Page title: {driver.title}")
 
# Click on the login button
sign_in_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT, "Login")))
sign_in_button.click()
 
# Handle CAPTCHA
captcha_div = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='form-type-textfield form-item-captcha-response form-item form-group']")))
captcha_text = captcha_div.text
print(f"Captcha text: {captcha_text}")
 
captcha_answer = solve_captcha(captcha_text)
if captcha_answer is None:
    print("Failed to solve captcha.")
    driver.quit()
    exit()
 
print(f"Captcha answer: {captcha_answer}")
 
# Fill in the login form
WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//input[@name='name']"))).send_keys('dummy3')
WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//input[@name='pass']"))).send_keys('Sal@2021')
WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//input[@name='captcha_response']"))).send_keys(str(captcha_answer))
 
# Submit the login form
login_button = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='edit-submit']")))
login_button.click()
print("Login form submitted.")
 
# Now process each URL after logging in
director_data = []
 
# Now process each URL after logging in
for url in df['Website'][0:50]:
    driver.get(url)
    #print(f"Page title: {driver.title}")
    url_parts = url.split('/')
    company_name = url_parts[-2]  # Value between last and second last
    cin = url_parts[-1]
 
    try:
        # Wait for the past directors section to load
        past_directors_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Past Directors')]"))
        )
 
        # Find the parent element that contains past director details
        director_details = past_directors_section.find_element(By.XPATH, "./following-sibling::table")
 
        # Extract the data from the table
        rows = director_details.find_elements(By.TAG_NAME, "tr")
        for row in rows[1:]:  # Skip header row
            columns = row.find_elements(By.TAG_NAME, "td")
            # Safely extract values or set to None if not found
            din = columns[0].text if len(columns) > 0 else None
            name = columns[1].text if len(columns) > 1 else None
            designation = columns[2].text if len(columns) > 2 else None
            start_date = columns[3].text if len(columns) > 3 else None
            end_date = columns[4].text if len(columns) > 4 else None  # Adjusted index
 
            # Print the values
            #print(f"DIN: {din}, Name: {name}, Designation: {designation}, Start Date: {start_date}, End Date: {end_date}")
 
            # Append the data to the list
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
 
# Create a DataFrame from the collected data
final = pd.DataFrame(director_data)
 
# Optionally, save to a CSV file
# final.to_csv('directors_data.csv', index=False)  # Uncomment to save to a CSV
 
# Close the driver
driver.quit()
# filename=r'directors_data.csv'
final.to_csv(r'data_dummy.csv')
 
# final.to_sql(f'zauba_past_director',engine,if_exists='append',index=False)
# print('Data Inserted in DB')

 
# final.to_sql(f'zauba_past_director',engine,if_exists='append',index=False)
# print('Data Inserted in DB')


# %%



