
import smtplib
from pathlib import Path
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
import sys
COMMASPACE = ', '
SERVER = 'localhost'
PORT = '1111'


def send_mail(send_from, send_to, subject, message, files=None,
              server=SERVER, port=PORT, username='', password='',
              use_tls=False):
    """Compose and send email with provided info and attachments.

    Args:
        send_from (str): from name
        send_to (list[str]): to name(s)
        subject (str): message title
        message (str): message body
        files (list[str]): list of file paths to be attached to email
        server (str): mail server host name
        port (int): port number
        username (str): server auth username
        password (str): server auth password
        use_tls (bool): use TLS mode
    """
    if files is None:
        files = []
    elif type(files) == str:
        files = [files]

    msg = MIMEMultipart()
    msg['From'] = send_from
    if type(send_to) == str:
        send_to = [send_to]
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain', 'utf-8'))

    for path in files:
        part = MIMEBase('application', "octet-stream")
        with open(path, 'rb') as file:
            part.set_payload(file.read())

        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename="{}"'.format(Path(path).name))
        msg.attach(part)

    try:
        smtp = smtplib.SMTP(server, port)
        if use_tls:
            smtp.starttls()
        if username:
            smtp.login(username, password)
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.quit()
    except smtplib.SMTPException as e:
        print(e, file=sys.stderr)


def send_text(send_from, send_to, subject, message):
    message = MIMEText(message, 'plain', 'utf-8')
    message['Subject'] = subject
    message['From'] = send_from
    message['To'] = send_to

    try:
        smtp = smtplib.SMTP(SERVER, port=PORT)
        smtp.sendmail(send_from, send_to, message.as_string())
    except smtplib.SMTPException as e:
        print(e, file=sys.stderr)


if __name__ == '__main__':
    send_text('test@email.com', 'tester@cs.ust.hk', 'Python SMTP Text Test', "Hello, here is the content")
    send_mail('test@email.com', 'tester@cs.ust.hk', 'Python SMTP Attachment Test', "Hello, here is the content",
              files='../LICENSE')
