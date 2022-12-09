# @Author: Ackerven
# @Mail: ackerven@qq.com
# @Time: 2022/12/8 23:33
# @File: main.py
# OS: Windows 10
# IDE: PyCharm
# @Copyright Copyright(C) 2022 Ackerven All rights reserved.

from apscheduler.schedulers.background import BackgroundScheduler

from datascore import DB
from model.tool import Notify, Scheduler
from utils.mail import Postman
from utils.tool import Config, LoggerPool


def init():
    Config('config/config.yml')
    LoggerPool(name='DailyRobot', config=Config().getConfig('log'))
    DB(source='mysql', config=Config().getConfig('db')['mysql'])
    Notify(postman=Postman(Config().getConfig('mail')['smtp']), address='ackerven@qq.com')
    Scheduler(scheduler=BackgroundScheduler(timezone='Asia/Shanghai'))


if __name__ == '__main__':
    init()
    while True:
        pass
