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

from utils.tool import LoggerPool


class Postman:
    def __init__(self, smtpHost, username, password, port, debug=False):
        self.smtpHost = smtpHost
        self.username = username
        self.password = password
        self.port = port
        self.debugMode = debug
        self.smtp = None
        self.logger = LoggerPool().get()
        self.init()

    def init(self):
        self.logger.info('初始化 Postman 对象')
        self.smtp = smtplib.SMTP_SSL(host=self.smtpHost, port=self.port)
        if self.debugMode:
            self.smtp.set_debuglevel(1)
        self.smtp.ehlo(self.smtpHost)
        self.smtp.login(self.username, self.password)
        self.logger.info('初始化 Postman 对象成功')

    def send(self, address, *args, **kwargs):
        self.logger.info(f'发送邮件给 {address}')
        message = MIMEText(kwargs['text'], 'plain', 'utf-8')
        message['Subject'] = Header(kwargs['subject'])
        message['From'] = Header(self.username)
        message['To'] = Header(address)
        self.smtp.sendmail(self.username, address, message.as_string())
        self.logger.info(f'发送邮件给 {address} 成功')

    def __del__(self):
        try:
            self.smtp.quit()
        except Exception as ex:
            # print(str(ex))
            pass
