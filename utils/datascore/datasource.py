# @Author: Ackerven
# @Mail: ackerven@qq.com
# @Time: 2022/12/6 13:35
# @File: datasource.py
# OS: Windows 10
# IDE: PyCharm
# @Copyright Copyright(C) 2022 Ackerven All rights reserved.
import abc


class DataScore(abc.ABC):
    @abc.abstractmethod
    def init(self, config):
        pass

    @abc.abstractmethod
    def queryAll(self):
        pass

    @abc.abstractmethod
    def queryByName(self, name):
        pass

    @abc.abstractmethod
    def queryById(self, id_):
        pass

    @abc.abstractmethod
    def update(self, user):
        pass

    @abc.abstractmethod
    def delete(self, user):
        pass

    @abc.abstractmethod
    def insert(self, user):
        pass
