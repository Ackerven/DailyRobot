# @Author: Ackerven
# @Mail: ackerven@qq.com
# @Time: 2022/12/6 21:21
# @File: mysql.py
# OS: Windows 10
# IDE: PyCharm
# @Copyright Copyright(C) 2022 Ackerven All rights reserved.
import pymysql

from model.bean import User
from datascore.datasource import DataScore
from utils.tool import LoggerPool


class MySQL(DataScore):
    TYPES = {
        'DQL': 'dql',
        'DML': 'dml',
        'DDL': 'ddl',
        'DCL': 'dcl',
    }

    def __init__(self, config):
        self.host = ''
        self.username = ''
        self.password = ''
        self.db = ''
        self.logger = LoggerPool().get()
        self.init(config)

    def getConnect(self):
        self.logger.debug(f'MySQL 获取连接')
        coon = pymysql.Connect(host=self.host,
                               user=self.username,
                               passwd=self.password,
                               db=self.db, autocommit=True)
        return coon

    def execute(self, sql, types):
        coon = self.getConnect()
        cur = coon.cursor()
        if types == 'dql':
            pass
        elif type == 'dml':
            cur.execute(sql)
        elif type == 'ddl':
            pass
        elif type == 'dcl':
            pass
        coon.close()
        cur.close()

    def init(self, config):
        self.logger.debug(f'MySQL 初始化')
        self.host = config['host']
        self.username = config['username']
        self.password = config['password']
        self.db = config['db']

    def _handler(self, record):
        if record is not None:
            return User(record[0], record[1], record[2],
                        record[3], record[4], record[5],
                        record[6], record[7])
        return None

    def queryAll(self):
        self.logger.debug(f'MySQL 查询所有用户')
        coon = self.getConnect()
        cur = coon.cursor()
        cur.execute('SELECT * FROM t_robot WHERE `isDelete` = 0')
        data = []
        for i in cur.fetchall():
            data.append(self._handler(i))
        coon.close()
        cur.close()
        return data

    def queryByName(self, name):
        self.logger.debug(f'MySQL 查询用户 Name: {name}')
        coon = self.getConnect()
        cur = coon.cursor()
        sql = "SELECT * FROM t_robot WHERE `isDelete` = 0 AND `name` = '{}'"
        cur.execute(sql.format(name))
        user = self._handler(cur.fetchone())
        coon.close()
        cur.close()
        return user

    def queryById(self, id_):
        self.logger.debug(f'MySQL 查询用户 ID: {id_}')
        coon = self.getConnect()
        cur = coon.cursor()
        sql = "SELECT * FROM t_robot WHERE `isDelete` = 0 AND `id` = {}"
        cur.execute(sql.format(id_))
        user = self._handler(cur.fetchone())
        coon.close()
        cur.close()
        return user

    def update(self, user):
        self.logger.debug(f'MySQL 更新用户 {user.name}')
        coon = self.getConnect()
        cur = coon.cursor()
        sql = "UPDATE t_robot SET `name` = '{}', `secret` = '{}', `mail` = '{}', `token` = '{}' WHERE `id` = {}"
        cur.execute(sql.format(user.name, user.secret, user.mail, user.token, user.id))
        cur.close()
        coon.close()

    def delete(self, user):
        self.logger.debug(f'MySQL 删除用户 {user.name}')
        coon = self.getConnect()
        cur = coon.cursor()
        sql = 'UPDATE t_robot SET `isDelete` = 1 WHERE `id` = {}'
        cur.execute(sql.format(user.id))
        cur.close()
        coon.close()

    def insert(self, user):
        self.logger.debug(f'MySQL 新增用户 {user.name}')
        coon = self.getConnect()
        cur = coon.cursor()
        sql = "INSERT INTO t_robot(name, secret, mail, token) VALUES ('{}', '{}', '{}', '{}')"
        cur.execute(sql.format(user.name, user.secret, user.mail, user.token))
        cur.close()
        coon.close()
