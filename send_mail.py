from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


def main(message, emails):
    msg = MIMEMultipart()
    password = "nt_dev11"
    msg['From'] = "nt_development@mail.ru"
    msg.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
    server.login(msg['From'], password)
    for email in emails:
        msg['To'] = email
        server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

