# @Author: Ackerven
# @Mail: ackerven@qq.com
# @Time: 2022/12/5 14:03
# @File: tool.py
# OS: Windows 10
# IDE: PyCharm
# @Copyright Copyright(C) 2022 Ackerven All rights reserved.
import base64
import datetime
import json
import logging
import os
import sys
import threading
import time
from logging.handlers import TimedRotatingFileHandler

import requests
import yaml

from model.JSONDict import reportFrom


def Singleton(cls):
    _instance = {}

    def _singleton(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    return _singleton


class SingletonClass(type):
    _instance_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with SingletonClass._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super(SingletonClass, cls).__call__(*args, **kwargs)
        return cls._instance


class Notify(metaclass=SingletonClass):
    TITLE = '[DailyRobot]'

    def __init__(self, postman=None, address=''):
        self.logger = LoggerPool().get()
        self.postman = postman
        self.address = address

    def failure(self, address, subject, text, *args, **kwargs):
        """ 打卡失败邮箱提醒

        :param address: 收件人
        :param subject: 主题
        :param text: 发件内容
        :return:
        """
        text += '\n\n如果有问题，回复此邮件联系'
        self.logger.info(f'发邮件提醒 {address} 打卡失败')
        self.postman.send(address=address,
                          subject=self.TITLE + subject,
                          text=text)

    def reportFailureList(self, failure, times):
        """ 打卡失败名单邮件提醒

        :param failure: 失败名单 {'name': {'name': '', 'mail': ''},}
        :param times: 失败次数
        :return:
        """
        text = '失败名单：\n'
        self.logger.info(f'第 {times} 次报告打卡失败名单')
        for i in failure.values():
            text += str(i) + '\n'
        text += '\n共{}人'.format(len(failure))
        self.postman.send(address=self.address,
                          subject=self.TITLE + '{} 第{}次失败名单'.format(time.strftime('%Y/%m/%d', time.localtime()), times),
                          text=text)


class Config(metaclass=SingletonClass):
    def __init__(self, file):
        print('Config Init...')
        with open(file, 'r', encoding='utf-8') as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)

    def getConfig(self, name):
        """ 获取配置

        :param name: 配置名称
        :return: 配置项 -> dict
        """
        if name in self.config:
            return self.config[name]
        return None


class LoggerPool(metaclass=SingletonClass):
    LEVELS = {
        'NOTSET': logging.NOTSET,
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    def __init__(self, name='', config=None):
        print("LoggerPool Init...")
        self.name = name
        self.config = config
        self._instance = {}
        self._init()

    def _init(self):
        path = self.config['path']
        level = self.config['level']

        if not (os.path.exists(path) and os.path.isdir(path)):
            os.mkdir(path)

        logger = logging.getLogger(self.name)
        logger.setLevel(self.LEVELS[level])
        if self.config['file']['enable']:
            logger.addHandler(self._fileHandler(self.name))
        logger.addHandler(self._consoleHandler())
        self._instance[self.name] = logger

    def _fileHandler(self, name):
        path = self.config['path'] + name
        fileName = path + f'/{name}.log'
        level = self.config['file']['level']
        format_ = logging.Formatter(self.config['format'][level])

        if not (os.path.exists(path) and os.path.isdir(path)):
            os.mkdir(path)
        if not os.path.exists(fileName):
            fp = open(fileName, 'a', encoding='utf-8')
            fp.close()
        handler = TimedRotatingFileHandler(filename=fileName, encoding='utf-8', when='midnight', interval=1,
                                           backupCount=7, atTime=datetime.time(0, 0, 0, 0))
        handler.setFormatter(format_)
        handler.setLevel(self.LEVELS[level])
        return handler

    def _consoleHandler(self):
        level = self.config['console']['level']
        format_ = logging.Formatter(self.config['format'][level])

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(format_)
        handler.setLevel(self.LEVELS[level])
        return handler

    def _mailHandler(self, name):
        path = self.config['path'] + name
        fileName = path + '/today.log'
        level = self.config['mail']['level']
        format_ = logging.Formatter(self.config['format'][level])

        if not (os.path.exists(path) and os.path.isdir(path)):
            os.mkdir(path)
        if not os.path.exists(fileName):
            fp = open(fileName, 'w', encoding='utf-8')
            fp.close()
        else:
            os.remove(fileName)
            fp = open(fileName, 'w', encoding='utf-8')
            fp.close()
        handler = logging.FileHandler(filename=fileName, encoding='utf-8')
        handler.setLevel(self.LEVELS[level])
        handler.setFormatter(format_)
        return handler

    def _register(self, name):
        level = self.config['level']

        logger = logging.getLogger(name)
        logger.setLevel(self.LEVELS[level])
        if self.config['file']['enable']:
            logger.addHandler(self._fileHandler(name))
        if self.config['console']['enable']:
            logger.addHandler(self._consoleHandler())
        if self.config['mail']['enable']:
            logger.addHandler(self._mailHandler(name))
        return logger

    def get(self, name=None) -> logging.Logger:
        """ 获取一个日志对象

        :param name: 日志对象名称
        :return: logging.Logger 对象
        """
        if name is None:
            return self._instance[self.name]
        if name in self._instance:
            return self._instance[name]
        self._instance[name] = self._register(name)
        return self._instance[name]

    def destroy(self, name):
        """ 销毁一个日志对象

        :param name: 日志对象名称
        """
        if name == self.name:
            return
        if name in self._instance:
            del self._instance[name]
            del logging.Logger.manager.loggerDict[name]


class Robot:
    _headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63030532)',
    }
    HOST = 'https://xxcj.bnuzh.edu.cn'

    def __init__(self, user):
        self.user = user
        self.logger = LoggerPool().get(user.name)
        self.session = requests.Session()
        self.data = None

    def auth(self, code):
        """ 使用 code 获取 token

        :param code: 43位的secret
        """
        self.logger.info('{} 请求授权'.format(self.user.name))
        api = f'/hApi/applet/userDailyReport/healthAuthorization/{code}'
        url = self.HOST + api
        response = self.session.get(url, headers=self._headers)
        if response.status_code == 200:
            result = json.loads(response.text)
            if result['message'] == '授权成功':
                self.logger.info(f'{self.user.name} 授权成功')
                self.user.token = result['data']['qyToken']
            else:
                self.logger.error(f'{self.user.name} 授权失败，请检查 code 是否合法！Message: {result["message"]}')
        else:
            self.logger.error(f'{self.user.name} 请求失败！状态码：{str(response.status_code)}')

    def lately(self):
        """ 获取用户最近16天的打卡情况

        :return:
        """
        self.logger.info(f'{self.user.name} 获取打卡情况')
        api = f'/hApi/applet/userDailyReport/getLatelyUserDailyReport'
        self._headers['Authorization-qy'] = f'Bearer {self.user.token}'
        url = self.HOST + api
        response = self.session.get(url, headers=self._headers)
        if response.status_code == 200:
            result = json.loads(response.text)
            if result['data'] is not None:
                self.logger.info(f'{self.user.name} 获取打卡情况成功')
                self.data = result['data']
            else:
                self.logger.info(f'{self.user.name} 获取打卡情况失败！Message: {result["message"]}')
        else:
            self.logger.error(f'{self.user.name} 请求失败！状态码：{response.status_code}')

    def check(self):
        """ 检查用户是否打卡

        :return:
        """
        if self.data is None:
            self.lately()
        self.logger.info(f'检查 {self.user.name} 是否打卡')
        today = self.data[0]
        if today['dailyReportStatus'] == 1:
            self.logger.info(f'{self.user.name} 已打卡')
            return True
        elif today['dailyReportStatus'] == 0:
            self.logger.info(f'{self.user.name} 未打卡')
            return False

    def _load(self):
        """ 处理打卡数据

        :return: 打卡表单
        """
        if self.data is None:
            self.lately()
        self.logger.info(f'{self.user.name} 加载数据')
        yesterday = self.data[1]
        exclude = ['id', 'todayDate', 'todayTime', 'createTime', 'updateTime', 'version']
        for i in reportFrom.keys():
            if i not in exclude:
                reportFrom[i] = yesterday[i]
        reportFrom['id'] = self.data[0]['id']
        reportFrom['todayDate'] = self.data[0]['todayDate']
        reportFrom['createTime'] = self.data[0]['createTime']
        reportFrom['todayTime'] = time.strftime('%H:%M:%S', time.localtime())
        reportFrom['updateTime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        return reportFrom

    def submit(self):
        """ 提交打卡数据

        :return: 打卡是否成功
        """
        self.logger.info(f'{self.user.name} 开始打卡')
        api = f'/hApi/applet/userDailyReport/addUserDailyReport'
        self._headers['Authorization-qy'] = f'Bearer {self.user.token}'
        self._headers['Content-Type'] = 'application/json;charset=UTF-8'
        url = self.HOST + api
        from_ = json.dumps(self._load(), ensure_ascii=False)
        response = self.session.post(url, headers=self._headers, data=from_.encode('utf-8'))
        if response.status_code == 200:
            result = json.loads(response.text)
            if result['message'] == '提交成功':
                self.logger.info(f'{self.user.name} 打卡成功')
                return True
            else:
                self.logger.error(f'{self.user.name} 打卡失败！Message: {result["message"]}')
        else:
            self.logger.error(f'{self.user.name} 请求失败！状态码：{response.status_code}')

        return False


class Token:
    @staticmethod
    def decode(token):
        tmp = token.split('.')
        header = json.loads(base64.b64decode(tmp[0]))
        if len(tmp[1]) % 3 == 1:
            tmp[1] += '=='
        elif len(tmp[1]) % 3 == 2:
            tmp[1] += '='
        payload = json.loads(base64.b64decode(tmp[1]))
        data = {'header': header, 'payload': payload}
        return data

    @staticmethod
    def check(token):
        data = Token.decode(token)
        expire = int(data['payload']['exp'])
        now = int(time.mktime(time.localtime()))
        return now > expire
