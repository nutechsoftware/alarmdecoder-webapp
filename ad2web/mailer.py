import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

class Mailer(object):

    port = 25
    server = "127.0.0.1"
    tls = False
    authentication_required = False
    username = None
    password = None

    def __init__(self, server="127.0.0.1", port=25, tls=False, authentication_required=False, username=None, password=None):
        self.port = port
        self.server = server
        self.tls = tls
        self.authentication_required = authentication_required
        self.username = username
        self.password = password

    def updateUsername(self, username):
        self.username = username

    def updatePassword(self, password):
        self.password = password
    
    def updateServer(self, server):
        self.server = server

    def updatePort(self, port):
        self.port = int(port)

    def updateTls(self, tls):
        self.tls = tls

    def updateAuth(self, auth):
        self.authentication_required = authentication_required
 
    def send_mail(self, send_from, send_to, subject, text, files=None):
        assert isinstance(send_to, list)

        if files is not None:
            assert isinstance(files, list)

        msg = MIMEMultipart()
        msg['From'] = send_from
        msg['To'] = COMMASPACE.join(send_to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject

        msg.attach(MIMEText(text))

        for f in files or []:
            with open(f, "rb") as fil:
                part = MIMEApplication(fil.read(), Name=basename(f) )
                part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
                msg.attach(part)

        s = None

        s = smtplib.SMTP(self.server, self.port)

        if self.tls:
            s.starttls()

        if self.authentication_required:
            s.login(str(self.username), str(self.password))

        s.sendmail(send_from, send_to, msg.as_string())
        s.close()
