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
        self.logger = LoggerPool().get()

    def getConnection(self):
        self.logger.debug('Postman 连接发件服务器')
        smtp = smtplib.SMTP_SSL(host=self.host, port=self.port)
        if self.debugMode:
            smtp.set_debuglevel(1)
        # self.smtp.ehlo(self.host)
        smtp.connect(self.host, self.port)
        smtp.login(self.username, self.password)
        return smtp

    def send(self, address, *args, **kwargs):
        self.logger.info(f'发送邮件给 {address}')
        smtp = self.getConnection()
        message = MIMEText(kwargs['text'], 'plain', 'utf-8')
        message['Subject'] = Header(kwargs['subject'])
        message['From'] = Header(self.username)
        message['To'] = Header(address)
        smtp.ehlo(self.host)
        smtp.sendmail(self.username, address, message.as_string())
        self.logger.info(f'发送邮件给 {address} 成功')
        smtp.quit()
