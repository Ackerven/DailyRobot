# @Author: Ackerven
# @Mail: ackerven@qq.com
# @Time: 2022/12/5 14:03
# @File: tool.py
# OS: Windows 10
# IDE: PyCharm
# @Copyright Copyright(C) 2022 Ackerven All rights reserved.
import datetime
import logging
import os
import sys
import threading
import time
from logging.handlers import TimedRotatingFileHandler

import yaml

from utils.datascore.mysql.mysql import MySQL


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
        print('Notify Init...')
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
        for i in failure.values():
            text += str(i) + '\n'
        text += '\n共{}人'.format(len(failure))
        self.postman.send(address=self.address,
                          subject=self.TITLE + '{} 第{}次失败名单'.format(time.strftime('%Y/%m/%d', time.localtime()), times),
                          text=text)


class DB(metaclass=SingletonClass):
    SOURCES = {
        'MYSQL': 'mysql',
    }

    def __init__(self, source='mysql', config=None):
        print(f'DataScore {source} Init...')
        self.engine = None
        if source == 'mysql':
            self.engine = MySQL(config)

    def queryAll(self):
        """ 查询所有用户

        :return: 用户对象列表
        """
        return self.engine.queryAll()

    def queryByName(self, name):
        """ 通过用户名查询用户

        :param name: 用户名
        :return: 用户对象
        """
        return self.engine.queryByName(name)

    def queryById(self, id_):
        """ 通过 ID 查询用户

        :param id_: 用户 ID
        :return: 用户对象
        """
        return self.engine.queryById(id_)

    def update(self, user):
        """ 更新用户

        :param user: 用户对象
        :return:
        """
        self.engine.update(user)

    def delete(self, user):
        """ 删除用户

        :param user: 用户对象
        :return:
        """
        self.engine.delete(user)

    def insert(self, user):
        """ 插入用户

        :param user: 用户对象
        :return:
        """
        self.engine.insert(user)


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
