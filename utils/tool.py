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
import traceback
from logging.handlers import TimedRotatingFileHandler

import yaml


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


class Config(metaclass=SingletonClass):
    def __init__(self, file=None):
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


class Token:
    @staticmethod
    def decode(token):
        data = None
        try:
            tmp = token.split('.')
            header = json.loads(base64.b64decode(tmp[0]))
            if len(tmp[1]) % 3 == 1:
                tmp[1] += '=='
            elif len(tmp[1]) % 3 == 2:
                tmp[1] += '='
            payload = json.loads(base64.b64decode(tmp[1]))
            data = {'header': header, 'payload': payload}
        except Exception as ex:
            LoggerPool().get().error(f'Token解码异常！异常信息：{traceback.format_exc()}')
        return data

    @staticmethod
    def check(token):
        try:
            data = Token.decode(token)
            if data is None: return True
            expire = int(data['payload']['exp'])
            now = int(time.mktime(time.localtime()))
            return now > expire
        except Exception as ex:
            LoggerPool().get().error(f'检查Token异常！异常信息：{traceback.format_exc()}')
        return None

    @staticmethod
    def expire(token):
        try:
            data = Token.decode(token)
            if data is None: return True
            expire = int(data['payload']['exp'])
            return time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(expire))
        except Exception as ex:
            LoggerPool().get().error(f'获取Token过期时间异常！异常信息：{traceback.format_exc()}')
        return None
