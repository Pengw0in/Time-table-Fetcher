import os
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

def create_html_content(timetable_data):
    """Create HTML formatted content for the email"""
    today = datetime.now().strftime("%A, %B %d, %Y")
    
    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f4f4;
            }}
            .container {{
                width: 100%;
                max-width: 800px;
                margin: 20px auto;
                background-color: #ffffff;
                padding: 20px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            h2 {{
                color: #333333;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            .footer {{
                margin-top: 20px;
                font-size: 12px;
                color: #666666;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Timetable for {today}</h2>
            <table>
                <tr>
                    <th>Time</th>
                    <th>Subject</th>
                    <th>Room</th>
                    <th>Teacher</th>
                    <th>Day</th>
                </tr>
    """
    
    for entry in timetable_data:
        html += f"""
                <tr>
                    <td>{entry['time']}</td>
                    <td>{entry['subject']}</td>
                    <td>{entry['room']}</td>
                    <td>{entry['teacher']}</td>
                    <td>{entry['day']}</td>
                </tr>
        """
    
    html += """
            </table>
            <div class="footer">
                This is an automated email. Please do not reply.
            </div>
        </div>
    </body>
    </html>
    """
    return html

def send_formatted_email(email_content):
    """
    Send an email with formatted timetable content
    """
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = "Your Daily Class Schedule"

        # Attach the HTML content to the email
        msg.attach(MIMEText(email_content, "html"))

        # Setup SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        # Send email
        server.send_message(msg)
        server.quit()
        logging.info("Email sent successfully")
        return True

    except Exception as e:
        logging.error(f"Email sending failed: {str(e)}")
        return False

def main(content):
    """
    Main function to send email
    """
    try:
        if not all([EMAIL_ADDRESS, EMAIL_PASSWORD, RECIPIENT_EMAIL]):
            raise ValueError("Missing email configuration in environment variables")
        
        return send_formatted_email(content)
    
    except Exception as e:
        logging.error(f"Email sending failed: {str(e)}")
        return False

if __name__ == "__main__":
    main("Test email content")