from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
from dotenv import load_dotenv


load_dotenv()
email_sender = os.getenv('EMAIL_ACCOUNT_SENDER')
my_password = os.getenv('EMAIL_PASSWORD')
email_reciver = os.getenv('EMAIL_ACCOUNT_RECEIVER')

def sender(subject, text):
    if not email_sender or not my_password:
        raise ValueError("Credentials are None!")
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(email_sender, my_password)

    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = email_reciver
    msg['Subject'] = subject
    msg.attach(MIMEText(text))

    smtp.sendmail(from_addr=email_sender,
                  to_addrs=email_reciver,
                  msg=msg.as_string())
    smtp.quit()