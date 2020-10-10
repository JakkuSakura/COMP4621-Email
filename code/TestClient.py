import smtplib
from email.header import Header
from email.mime.text import MIMEText

if __name__ == '__main__':
    sender = 'test@email.com'
    receivers = ['tester@cs.ust.hk']

    message = MIMEText('Email send test.', 'plain', 'utf-8')
    message['From'] = Header("Tester From", 'utf-8')
    message['To'] = Header('Tester To', 'utf-8')

    subject = 'Python SMTP Test'
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP('127.0.0.1', port=1111)
        smtpObj.sendmail(sender, receivers, message.as_string())
    except smtplib.SMTPException as e:
        print(e)
