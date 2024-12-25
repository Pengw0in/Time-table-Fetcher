# GITAM Student Portal Automation Documentation

# Daily Timetable Email Automation

## Status: Discontinued 🚫

This project is no longer actively maintained. The GitHub Actions workflow and the associated scripts have been stopped. If you wish to use or extend this project, feel free to fork it.

### Why Discontinued?
Due to shifting priorities, this project is no longer relevant to my current work.

### Using the Code
The code is still available under the [MIT License](LICENSE). You're welcome to explore, modify, and use it for personal or educational purposes.


## Table of Contents
1. [Overview](#overview)
2. [File Structure](#file-structure)
3. [main.py](#mainpy)
4. [send_email.py](#send_emailpy)
5. [Flow and Features](#flow-and-features)

## Overview
This project automates the process of retrieving class schedules from the GITAM student portal and sends formatted daily schedules via email. The automation includes web scraping, data processing, and email delivery functionality.

## File Structure
The project consists of two main Python files:
- `main.py`: Handles web automation and data collection
- `send_email.py`: Manages email formatting and delivery

## main.py

### Import Section
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
# ... additional imports
```
This section imports necessary modules for:
- Selenium WebDriver for web automation
- Time management and delays
- Environment variable handling
- Table formatting
- Date/time operations
- Custom email module
- Logging functionality

### Configuration
```python
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()
USER_ID = os.getenv("USER_ID")
PASSWORD_INPUT = os.getenv("PASSWORD_INPUT")
```
- Sets up logging configuration with timestamp and message format
- Loads environment variables for credentials

### Key Functions

#### setup_chrome_driver()
- Creates ChromeOptions with headless configuration
- Sets browser parameters (window size, sandbox settings, etc.)
- Initializes and returns configured Chrome WebDriver

#### Helper Functions
- `normalize_time_slot(time_slot)`: Standardizes time formats
- `parse_class_info(text)`: Extracts schedule information
- `match_timetables(basic_timetable, detailed_timetable)`: Combines data sources
- `print_matched_timetable(data)`: Formats output
- `create_email_content(timetable_data)`: Prepares email content

#### Main Function
The main function handles:
1. WebDriver initialization
2. Portal navigation and login
3. CAPTCHA resolution
4. Timetable data collection
5. Data processing
6. Email triggering

## send_email.py

### Import Section
```python
import os
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
# ... additional imports
```
Imports modules for:
- Email operations
- Environment variables
- Logging
- Date/time handling

### Configuration
```python
load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
```
Loads email-related environment variables

### Key Functions

#### create_html_content(timetable_data)
- Generates HTML email template
- Includes CSS styling
- Creates formatted table structure
- Adds footer and metadata

#### send_formatted_email(email_content)
- Creates MIME message structure
- Configures email headers
- Attaches HTML content
- Manages SMTP connection
- Handles email delivery

#### Main Function
- Validates configuration
- Executes email sending process
- Manages error handling and logging

## Flow and Features

### Process Flow
1. Script initiates and logs into GITAM portal
2. Navigates through portal sections
3. Collects timetable information
4. Processes and formats data
5. Generates and sends HTML email

### Key Features
- **Automation**: Headless browser automation using Selenium
- **Security**: Environment variable-based credential management
- **CAPTCHA Handling**: Automated CAPTCHA resolution
- **Data Processing**: Sophisticated data scraping and matching
- **Email**: HTML-formatted email generation and delivery
- **Error Management**: Comprehensive error handling and logging
- **Configuration**: Flexible environment-based configuration

### Security Considerations
- Credentials stored in environment variables
- Secure email transmission using TLS
- No plain-text password storage
- Session management and cleanup

### Performance Optimizations
- Headless browser operation
- Efficient data matching algorithms
- Resource cleanup after execution
- Timeout handling for network operations

## Usage Requirements
1. Python 3.x
2. Required Python packages (Selenium, dotenv, etc.)
3. Chrome WebDriver
4. Environment variables configuration
5. SMTP server access (Gmail)
