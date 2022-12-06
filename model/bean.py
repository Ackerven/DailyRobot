# @Author: Ackerven
# @Mail: ackerven@qq.com
# @Time: 2022/12/5 13:15
# @File: bean.py
# OS: Windows 10
# IDE: PyCharm
# @Copyright Copyright(C) 2022 Ackerven All rights reserved.


class User:
    def __init__(self, id, name, secret, mail, token, isDelete=0, created=None, updated=None):
        self.id = id
        self.name = name
        self.secret = secret
        self.mail = mail
        self.token = token
        self.isDelete = isDelete
        self.created = created
        self.updated = updated

    def to_str(self):
        return 'User({}, {})'.format(self.name, self.mail)

    def __str__(self) -> str:
        return 'User({}, {}, {}, {}, {}, {}, {}, {})'.format(self.id, self.name, self.secret, self.mail, self.token,
                                                             self.isDelete, self.created, self.updated)
