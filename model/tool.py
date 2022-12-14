# @Author: Ackerven
# @Mail: ackerven@qq.com
# @Time: 2022/12/8 20:07
# @File: tool.py
# OS: Windows 10
# IDE: PyCharm
# @Copyright Copyright(C) 2022 Ackerven All rights reserved.
import json
import random
import time
import traceback

import requests

from datascore import DB
from model.JSONDict import reportFrom
from utils.tool import LoggerPool, SingletonClass, Config, Token


class Notify(metaclass=SingletonClass):
    TITLE = '[DailyRobot]'

    def __init__(self, postman=None, address=''):
        self.logger = LoggerPool().get()
        self.logger.info(f'初始化 Notify 对象')
        self.postman = postman
        self.address = address

    def failure(self, user):
        """ 打卡失败邮箱提醒

        :param user: 用户对象
        :return:
        """
        try:
            file = Config().getConfig('log')['path'] + f'{user.name}/today.log'
            today = time.strftime('%Y/%m/%d', time.localtime())
            text = str(today) + ' 打卡失败\n\n'
            text += str(today) + f' {user.name}.log:\n'
            with open(file, 'r', encoding='utf-8') as f:
                while True:
                    line = f.readline()
                    if line:
                        text += line
                    else:
                        break
            text += '\n\n如果有问题，回复此邮件联系'
            self.logger.info(f'发邮件提醒 {user.name} 打卡失败')
            self.postman.send(address=user.mail,
                              subject=self.TITLE + '{} 打卡失败'.format(today),
                              text=text)
        except Exception as ex:
            self.logger.info(f'发送打卡失败邮件异常！异常信息：{traceback.format_exc()}')

    def tokenExpire(self, user):
        """ Token

        :param user: 用户对象
        :return:
        """
        try:
            text = "Token 已过期，请及时更新\n\n如果有问题，回复此邮件联系"
            self.logger.info(f'发邮件提醒 {user.name} Token 已过期')
            self.postman.send(address=user.mail,
                              subject=self.TITLE + 'Token 已过期',
                              text=text)
        except Exception as ex:
            self.logger.info(f'发送 Token 过期提醒邮件异常！异常信息：{traceback.format_exc()}')

    def reportFailureList(self, failure, times):
        """ 打卡失败名单邮件提醒

        :param failure: 失败名单 {'name': {'name': '', 'mail': ''},}
        :param times: 失败次数
        :return:
        """
        try:
            text = '失败名单：\n'
            self.logger.info(f'第 {times} 次报告打卡失败名单')
            for i in failure.values():
                text += i.to_str() + '\n'
            text += '\n共{}人'.format(len(failure))
            self.postman.send(address=self.address,
                              subject=self.TITLE + '{} 第{}次失败名单'.format(
                                  time.strftime('%Y/%m/%d', time.localtime()), times),
                              text=text)
        except Exception as ex:
            self.logger.info(f'发送打卡失败名单邮件异常！异常信息：{traceback.format_exc()}')


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
        self.logger.info(f'创建 {user.name} 打卡机器人')

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

    def __del__(self):
        LoggerPool().destroy(self.user.name)


class Scheduler(metaclass=SingletonClass):
    def __init__(self, scheduler):
        self.logger = LoggerPool().get()
        self.scheduler = scheduler
        self.logger.info('初始化 Scheduler 对象')
        self.start()

    def start(self):
        self.logger.info('定时任务开始执行')
        config = Config().getConfig('scheduler')
        self.scheduler.add_job(self.daily, 'cron', hour=config['daily']['h'], minute=config['daily']['m'], id='daily')
        self.scheduler.add_job(self.token, 'cron', hour=config['token']['h'], minute=config['token']['m'], id='token')
        self.scheduler.start()

    def _loadData(self):
        try:
            return DB().queryAll()
        except Exception as ex:
            self.logger.error(f'查询所有用户失败！异常信息：{traceback.format_exc()}')

    def _post(self, data, retry):
        failure = {}
        for i in data:
            time.sleep(random.randint(3, 6))
            try:
                r = Robot(i)
                if not r.submit():
                    failure[i.name] = i
                    if i.mail != '' and retry == 3:
                        Notify().failure(i)
            except Exception as ex:
                LoggerPool().get(i.name).error(f'{i.name} 打卡异常！异常信息：{traceback.format_exc()}')
                failure[i.name] = i
                if i.mail != '':
                    Notify().failure(i)
        return failure

    def daily(self):
        self.logger.info('[定时任务] 开始打卡')
        tmp = self._loadData()
        retryTimes = 0
        data = []
        for i in tmp:
            if i.token != '':
                data.append(i)

        failure = self._post(data, retryTimes)
        # Notify().reportFailureList(failure, retryTimes)

        if failure:
            while retryTimes < 3:
                retryTimes += 1
                self.logger.info(f'失败名单尝试第 {retryTimes} 次打卡')
                time.sleep(600)  # 600
                data = failure.values()
                failure = self._post(data, retryTimes)
                if failure:
                    if retryTimes == 3:
                        Notify().reportFailureList(failure, retryTimes)
                else:
                    break

    def token(self):
        self.logger.info('[定时任务] 清理无效Token')
        data = self._loadData()
        for i in data:
            if i.token != '':
                result = Token.check(i.token)
                if result is not None and result is True:
                    i.token = ''
                    Notify().tokenExpire(i)
                    try:
                        DB().update(i)
                    except Exception as ex:
                        self.logger.error(f'更新用户 {i.name} 失败！异常信息：{traceback.format_exc()}')
