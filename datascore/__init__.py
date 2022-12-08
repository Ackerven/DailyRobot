from datascore.mysql.mysql import MySQL
from utils.tool import SingletonClass, LoggerPool


class DB(metaclass=SingletonClass):
    SOURCES = {
        'MYSQL': 'mysql',
    }

    def __init__(self, source='mysql', config=None):
        self.logger = LoggerPool().get()
        self.logger.info(f'初始化 {source} 数据源')
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
