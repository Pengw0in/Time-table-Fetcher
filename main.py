from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import os
from dotenv import load_dotenv
from prettytable import PrettyTable
import datetime
import send_email
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()
USER_ID = os.getenv("USER_ID")
PASSWORD_INPUT = os.getenv("PASSWORD_INPUT")

if not USER_ID or not PASSWORD_INPUT:
    raise ValueError("Missing required environment variables: user_id or password_input")

def setup_chrome_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=600,600")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    
    # Set up Chrome service
    service = Service()
    
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(60)
        return driver
    except WebDriverException as e:
        logging.error(f"Failed to initialize Chrome driver: {e}")
        raise

def normalize_time_slot(time_slot):
    """Helper function to normalize time slot format for comparison"""
    try:
        start, end = time_slot.split('-')
        # Ensure consistent format with leading zeros
        start_parts = start.strip().split(':')
        end_parts = end.strip().split(':')
        
        start_formatted = f"{int(start_parts[0]):02d}:{start_parts[1]}" # Ensure 2 digit hour
        end_formatted = f"{int(end_parts[0]):02d}:{end_parts[1]}" # Ensure 2 digit hour
        
        return f"{start_formatted}-{end_formatted}"
    except:
        return time_slot

def parse_class_info(text):
    """Helper function to parse class information from text"""
    parts = text.strip().split(" : ")
    if len(parts) == 2:
        time_slot = parts[0].strip()
        subject = parts[1].strip()
    else:
        time_slot = parts[0].strip()
        subject = parts[0].strip()  # If no subject, use the time
    return time_slot, subject

def match_timetables(basic_timetable, detailed_timetable):
    """Match and combine data from both timetables, ensuring room and teacher are included"""
    matched_timetable = []
    current_day = datetime.datetime.now().strftime('%A')  # Get the current day
    # Filter detailed timetable to include only entries for the current day
    today_detailed_entries = [
        entry for entry in detailed_timetable if entry['day'].upper()[:3] == current_day.upper()[:3]
    ]
    # Match each basic timetable entry with today’s detailed entries
    for basic_entry in basic_timetable:
        normalized_basic_time = normalize_time_slot(basic_entry['time'])
        
        # Initialize matched entry with basic timetable info
        matched_entry = {
            'time': basic_entry['time'],
            'subject': basic_entry['subject'],
            'room': 'N/A',
            'teacher': 'N/A',
            'day': current_day
        }
        
        # Try to find a corresponding detailed entry with the same time slot
        for detailed_entry in today_detailed_entries:
            normalized_detailed_time = normalize_time_slot(detailed_entry['time'])
            if normalized_basic_time == normalized_detailed_time:
                # Update matched entry with details from detailed timetable
                matched_entry.update({
                    'room': detailed_entry.get('room', 'N/A'),
                    'teacher': detailed_entry.get('teacher', 'N/A'),
                    'subject': detailed_entry.get('subject', basic_entry['subject'])  # Prefer detailed subject
                })
                break  # Stop searching once a match is found
        matched_timetable.append(matched_entry)
    return matched_timetable

def print_matched_timetable(data):
    """Print the matched timetable data"""
    if not data:
        print("\nMatched Timetable: No classes scheduled")
        return
    
    table = PrettyTable()
    table.field_names = ["Time", "Subject", "Room", "Teacher", "Day"]
    for field in table.field_names:
        table.align[field] = "l"
    table.max_width = 30
    
    for entry in data:
        table.add_row([
            entry['time'],
            entry['subject'],
            entry['room'],
            entry['teacher'],
            entry['day']
        ])
    
    print("\nMatched Timetable:")
    print(table)

def create_email_content(timetable_data):
    """Format the matched timetable data for email"""
    if not timetable_data:
        return "No classes scheduled for today."
    
    current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
    email_content = f"Class Schedule for {current_date}\n\n"
    
    table = PrettyTable()
    table.field_names = ["Time", "Subject", "Room", "Teacher", "Day"]
    for field in table.field_names:
        table.align[field] = "l"
    table.max_width = 30
    
    for entry in timetable_data:
        table.add_row([
            entry['time'],
            entry['subject'],
            entry['room'],
            entry['teacher'],
            entry['day']
        ])
    
    email_content += table.get_string()
    return email_content

def main():
    driver = None
    try:
        logging.info("Initializing Chrome driver")
        driver = setup_chrome_driver()
        logging.info("Navigating to login page")
        driver.get("https://login.gitam.edu/Login.aspx")
        wait = WebDriverWait(driver, 30)
        # Login process
        logging.info("Attempting login")
        username = wait.until(EC.visibility_of_element_located((By.ID, "txtusername")))
        username.send_keys(USER_ID)
        time.sleep(1)
        password = wait.until(EC.visibility_of_element_located((By.ID, "password")))
        password.send_keys(PASSWORD_INPUT)
        time.sleep(1)
        # Handle CAPTCHA
        captcha_numbers = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.preview span')))
        first_number = int(captcha_numbers[0].text.strip())
        second_number = int(captcha_numbers[4].text.strip())
        captcha_answer = first_number + second_number
        captcha_input = wait.until(EC.visibility_of_element_located((By.ID, "captcha_form")))
        captcha_input.send_keys(str(captcha_answer))
        password.send_keys(Keys.RETURN)
        
        time.sleep(2)
        # Course page navigation
        logging.info("Navigating to course page")
        course_link_element = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="maindiv"]/div[1]/div/div[2]/div[8]')))
        course_link_element.click()
        
        # Handle new window
        wait.until(lambda d: len(d.window_handles) > 1)
        driver.switch_to.window(driver.window_handles[-1])
        # Collect basic timetable data
        logging.info("Collecting basic timetable data")
        timetable_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "ul#ullist")))
        timetable_items = timetable_element.find_elements(By.CSS_SELECTOR, "li")
        basic_timetable = []
        
        for item in timetable_items:
            class_info = item.text.strip()
            if ':' in class_info:
                time_slot, subject = parse_class_info(class_info)
                if subject != "I":
                    basic_timetable.append({
                        "time": time_slot,
                        "subject": subject
                    })
        detailed_timetable = []
        if basic_timetable:  # Only proceed if there are classes scheduled
            # Get detailed timetable
            logging.info("Collecting detailed timetable")
            driver.get("https://newgstudent.gitam.edu/Home")
            time_table_element = wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "a.Time[onclick=\"mbLoadConfigView('14');\"] h5")))
            time_table_element.click()
            try:
                registered_courses_table_element = wait.until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "h3 + div.box-inner div.table-responsive > table.table-bordered")))
                
                rows = registered_courses_table_element.find_elements(By.CSS_SELECTOR, "tr")
                
                for row in rows[1:]:  # Skip header row
                    try:
                        columns = row.find_elements(By.CSS_SELECTOR, "td")
                        if len(columns) >= 8:
                            slot_info = columns[8].text.strip()
                            if '[' in slot_info and ']' in slot_info:
                                slot_parts = slot_info[1:-1].split("-")
                                if len(slot_parts) >= 3:
                                    time_range = f"{slot_parts[0]}-{slot_parts[1]}"
                                    day = slot_parts[2]
                                else:
                                    time_range, day = "N/A", "N/A"
                            else:
                                time_range, day = "N/A", "N/A"
                            detailed_timetable.append({
                                "subject": columns[1].text.strip(),
                                "room": columns[2].text.strip(),
                                "teacher": columns[7].text.strip(),
                                "time": time_range,
                                "day": day
                            })
                    except Exception as e:
                        logging.warning(f"Error processing row: {e}")
                        continue
                # Match timetables and create combined view
                matched_timetable = match_timetables(basic_timetable, detailed_timetable)
                print_matched_timetable(matched_timetable)
            except TimeoutException:
                logging.error("Timeout while loading detailed timetable")
                print("\nDetailed Timetable: Failed to load (timeout)")
            except Exception as e:
                logging.error(f"Error collecting detailed timetable: {e}")
                print("\nDetailed Timetable: Failed to load (error)")
            
            if matched_timetable:
                logging.info("Sending email with timetable")
                email_content = send_email.create_html_content(matched_timetable)
                send_email.main(email_content)
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

if __name__ == "__main__":
    main()