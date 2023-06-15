import redis
import time
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, render_template
import requests
import datetime

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0)
app = Flask(__name__)

# Define the email message
msg = MIMEMultipart('alternative')
msg['From'] = 'naval976583@gmail.com'
msg['To'] = 'naval976583@gmail.com'
msg['Subject'] = 'Test Email'

with app.app_context():
    student = json.loads(r.get("student1"))
    html = render_template('Student_Email.html', student=student)
    html_part = MIMEText(html, 'html')
    msg.attach(html_part)

# Set the target time to 9:05 PM today
target_time = datetime.datetime.now().replace(hour=22, minute=10, second=0, microsecond=0)

# Compute the time difference between the current time and the target time
time_diff = (target_time - datetime.datetime.now()).total_seconds()

# Schedule the email to be sent at the target time
r.zadd('mail_queue', {msg.as_string(): time.time() + time_diff})

# Schedule the email to be sent in 10 seconds
# r.zadd('mail_queue', {msg.as_string(): time.time() + 5})

# Check for scheduled emails every second and send them
while True:
    # Get the next scheduled email
    next_email = r.zrangebyscore('mail_queue', 0, time.time(), start=0, num=1)

    # If there are no scheduled emails, wait for a second and try again
    if not next_email:
        if r.zcard('mail_queue') == 0:
            break  # No more scheduled emails left in the queue
        time.sleep(1)
        continue

    # Send the email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('naval976583@gmail.com', 'ezkbjdqxxuetwiwd')
    server.sendmail('naval976583@gmail.com', 'naval976583@gmail.com', next_email[0])
    # server.sendmail('naval976583@gmail.com',  next_email[0])
    server.quit()

    email_data = {
        "to": ["naval976583@gmail.com"],
        "from": "naval976583@gmail.com",
        "cc": [],
        "bcc": [],
        "subject": "STUDENT DETAILS",
        "name": "Student Details",
        "content": "Student details added successfully",
        "reply_to": None
    }
    requests.post('https://email.digicollect.com/sendgrid/send_mail',
                  headers={"Content-Type": "application/json"},
                  json=email_data).json()

    # Remove the email from the queue
    r.zrem('mail_queue', next_email[0])

if __name__ == '__main__':
    pass
