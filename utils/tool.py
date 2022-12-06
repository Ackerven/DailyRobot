# @Author: Ackerven
# @Mail: ackerven@qq.com
# @Time: 2022/12/5 14:03
# @File: tool.py
# OS: Windows 10
# IDE: PyCharm
# @Copyright Copyright(C) 2022 Ackerven All rights reserved.
import time

from utils.mysql.mysql import MySQL


def Singleton(cls):
    _instance = {}

    def _singleton(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    return _singleton


@Singleton
class Notify:
    TITLE = '[DailyRobot]'

    def __init__(self, postman=None, address=''):
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


@Singleton
class DB:
    SOURCES = {
        'MYSQL': 'mysql',
    }

    def __init__(self, source='mysql', config=None):
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
