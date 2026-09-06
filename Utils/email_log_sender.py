from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import smtplib
import os
from dotenv import load_dotenv


load_dotenv()
my_email = os.getenv('EMAIL_ACCOUNT_SENDER')
my_password = os.getenv('EMAIL_PASSWORD')
receiver = os.getenv('EMAIL_ACCOUNT_RECEIVER')

def sender(subject, text):
    if not my_email or not my_password:
        raise ValueError("Credentials are None!")
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(my_email, my_password)

    msg = MIMEMultipart()
    msg['From'] = my_email
    msg['To'] = receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(text))

    smtp.sendmail(from_addr="EMAIL_ACCOUNT_RECEIVER",
              to_addrs=receiver,
              msg=msg.as_string())
    smtp.quit()