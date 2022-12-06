# @Author: Ackerven
# @Mail: ackerven@qq.com
# @Time: 2022/12/6 10:23
# @File: mail.py
# OS: Windows 10
# IDE: PyCharm
# @Copyright Copyright(C) 2022 Ackerven All rights reserved.

import smtplib
from email.header import Header
from email.mime.text import MIMEText


class Postman:
    def __init__(self, smtpHost, username, password, port, debug=False):
        self.smtpHost = smtpHost
        self.username = username
        self.password = password
        self.port = port
        self.debugMode = debug
        self.smtp = None
        self.init()

    def init(self):
        self.smtp = smtplib.SMTP_SSL(host=self.smtpHost, port=self.port)
        if self.debugMode:
            self.smtp.set_debuglevel(1)
        self.smtp.ehlo(self.smtpHost)
        self.smtp.login(self.username, self.password)

    def send(self, address, *args, **kwargs):
        message = MIMEText(kwargs['text'], 'plain', 'utf-8')
        message['Subject'] = Header(kwargs['subject'])
        message['From'] = self.username
        message['To'] = address
        self.smtp.sendmail(self.username, address, message.as_string())

    def __del__(self):
        self.smtp.quit()
