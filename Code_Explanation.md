# Code Explanation of GITAM Portal Scraper

## Import Section
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
```
- Imports Selenium components for web automation
- `webdriver`: Main class for browser control
- `By`: Class for locating elements (ID, CSS, XPath, etc.)
- `Service`: Manages ChromeDriver service
- `Keys`: Simulates keyboard input
- `WebDriverWait` and `EC`: For explicit waiting conditions
- Exception classes for error handling

```python
import time
import os
from dotenv import load_dotenv
from prettytable import PrettyTable
import datetime
import send_email
import logging
```
- Standard library imports for various functionalities
- `time`: For adding delays
- `os`: Operating system interface
- `load_dotenv`: Environment variable management
- `PrettyTable`: For formatting tabular data
- `datetime`: Date/time handling
- Custom `send_email` module
- `logging`: For system logging

## Logging Setup
```python
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
```
- Configures logging with:
  - INFO level messages and above
  - Format: timestamp, log level, message

## Environment Variables
```python
load_dotenv()
user_id = os.getenv("user_id")
password_input = os.getenv("password_input")

if not user_id or not password_input:
    raise ValueError("Missing required environment variables")
```
- Loads environment variables from .env file
- Retrieves login credentials
- Validates that required credentials exist

## Chrome Driver Setup
```python
def setup_chrome_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
```
- Creates ChromeOptions object
- Sets various Chrome arguments:
  - `--headless=new`: Runs Chrome without GUI
  - `--no-sandbox`: Disables sandbox for stability
  - `--disable-dev-shm-usage`: Memory handling
  - `--disable-gpu`: Disables GPU acceleration
  - Sets window size and disables various features

```python
    service = Service()
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(60)
        return driver
    except WebDriverException as e:
        logging.error(f"Failed to initialize Chrome driver: {e}")
        raise
```
- Creates Chrome service
- Initializes Chrome driver with options
- Sets page load timeout to 60 seconds
- Handles initialization errors

## Main Function
```python
def main():
    driver = None
    try:
        logging.info("Initializing Chrome driver")
        driver = setup_chrome_driver()
```
- Starts main execution
- Initializes driver variable
- Logs start of process

### Login Process
```python
        driver.get("https://login.gitam.edu/Login.aspx")
        wait = WebDriverWait(driver, 30)

        username = wait.until(EC.visibility_of_element_located((By.ID, "txtusername")))
        username.send_keys(user_id)

        password = wait.until(EC.visibility_of_element_located((By.ID, "password")))
        password.send_keys(password_input)
```
- Navigates to login page
- Creates WebDriverWait object with 30-second timeout
- Waits for username field and enters username
- Waits for password field and enters password

### CAPTCHA Handling
```python
        captcha_numbers = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'div.preview span')))
        first_number = int(captcha_numbers[0].text.strip())
        second_number = int(captcha_numbers[4].text.strip())
        captcha_answer = first_number + second_number
        
        captcha_input = wait.until(EC.visibility_of_element_located(
            (By.ID, "captcha_form")))
        captcha_input.send_keys(str(captcha_answer))
```
- Locates CAPTCHA numbers on page
- Extracts first and second numbers
- Calculates sum for CAPTCHA answer
- Enters CAPTCHA solution

### Course Navigation
```python
        course_link_element = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="maindiv"]/div[1]/div/div[2]/div[8]')))
        course_link_element.click()
        
        wait.until(lambda d: len(d.window_handles) > 1)
        driver.switch_to.window(driver.window_handles[-1])
```
- Waits for and clicks course link
- Handles new window opening
- Switches to new window

### Timetable Data Collection
```python
        timetable_element = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "ul#ullist")))
        timetable_items = timetable_element.find_elements(By.CSS_SELECTOR, "li")
        
        timetable_data = []
        for item in timetable_items:
            class_info = item.text.strip()
            if ' - ' in class_info:
                time_slot = class_info.split(" - ")[-1]
                subject = class_info.split(" - ")[0]
                timetable_data.append({
                    "subject": subject,
                    "time": time_slot
                })
```
- Locates timetable list
- Extracts individual class entries
- Parses subject and time information
- Stores in timetable_data list

### Detailed Timetable Collection
```python
        driver.get("https://newgstudent.gitam.edu/Home")
        time_table_element = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "a.Time[onclick=\"mbLoadConfigView('14');\"] h5")))
        time_table_element.click()
```
- Navigates to detailed timetable page
- Locates and clicks timetable link

```python
        registered_courses_table_element = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "h3 + div.box-inner div.table-responsive > table.table-bordered")))
        
        detailed_timetable_data = []
        rows = registered_courses_table_element.find_elements(By.CSS_SELECTOR, "tr")
```
- Locates detailed course table
- Prepares to extract row data

### Data Processing
```python
        for row in rows[1:]:
            columns = row.find_elements(By.CSS_SELECTOR, "td")
            row_data = [col.text.strip() for col in columns]
            if row_data and len(row_data) >= 4:
                slot_info = row_data[0]
                slot_parts = slot_info[1:-1].split("-")
                if len(slot_parts) >= 3:
                    time_range = slot_parts[0].strip()
                    day = slot_parts[2].strip()
                    detailed_timetable_data.append({
                        "subject": row_data[1],
                        "time": time_range,
                        "day": day,
                        "room": row_data[2],
                        "teacher": row_data[3]
                    })
```
- Processes each table row
- Extracts slot information
- Parses time, day, room, and teacher info
- Stores in detailed_timetable_data

### Combining Timetables
```python
        today = datetime.datetime.now().strftime("%A")
        combined_timetable = []
        
        for basic_class in timetable_data:
            for detailed_class in detailed_timetable_data:
                if (basic_class["subject"] == detailed_class["subject"] and
                    basic_class["time"] == detailed_class["time"] and
                    detailed_class["day"] == today):
                    combined_timetable.append({
                        "subject": basic_class["subject"],
                        "time": basic_class["time"],
                        "room": detailed_class["room"],
                        "teacher": detailed_class["teacher"],
                        "day": detailed_class["day"]
                    })
```
- Gets current day of week
- Matches basic and detailed timetable entries
- Creates combined timetable for today's classes

### Email Sending and Error Handling
```python
        if combined_timetable:
            send_email.main(combined_timetable)
        else:
            logging.info("No matching timetable entries found for today")

    except TimeoutException as e:
        logging.error(f"Timeout error: {e}")
        raise
    except WebDriverException as e:
        logging.error(f"WebDriver error: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise
    finally:
        if driver:
            driver.quit()
```
- Sends email if timetable data exists
- Handles various exceptions:
  - Timeout errors
  - WebDriver errors
  - Unexpected errors
- Ensures driver cleanup in finally block

## Script Execution
```python
if __name__ == "__main__":
    main()
```
- Runs main function when script is executed directly
