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
    def __init__(self, config=None):
        self.host = config['host']
        self.username = config['username']
        self.password = config['password']
        self.port = config['port']
        self.debugMode = config['debug']
        self.smtp = None
        self.logger = LoggerPool().get()
        self.init()

    def init(self):
        self.logger.debug('初始化 Postman 对象')
        self.smtp = smtplib.SMTP_SSL(host=self.host, port=self.port)
        if self.debugMode:
            self.smtp.set_debuglevel(1)
        self.smtp.ehlo(self.host)
        self.smtp.login(self.username, self.password)

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
