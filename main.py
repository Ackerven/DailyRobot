# @Author: Ackerven
# @Mail: ackerven@qq.com
# @Time: 2022/12/8 23:33
# @File: main.py
# OS: Windows 10
# IDE: PyCharm
# @Copyright Copyright(C) 2022 Ackerven All rights reserved.
import json

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request

from datascore import DB
from model.bean import User
from model.tool import Notify, Scheduler, Robot
from utils.mail import Postman
from utils.tool import Config, LoggerPool
from utils.tool import Token


def init():
    Config('config/config.yml')
    LoggerPool(name='DailyRobot', config=Config().getConfig('log'))
    DB(source='mysql', config=Config().getConfig('db')['mysql'])
    Notify(postman=Postman(Config().getConfig('mail')['smtp']), address='ackerven@qq.com')
    Scheduler(scheduler=BackgroundScheduler(timezone='Asia/Shanghai'))


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        JSON_AS_ASCII=False
    )

    init()

    @app.route('/api/', methods=['GET', 'POST'])
    def index():
        return 'Hello world!'

    @app.route('/api/login', methods=['POST'])
    def login():
        try:
            data = json.loads(request.get_data())
            name = data['name']
            secret = data['secret']
            try:
                u = DB().queryByName(name)
                if u.secret == secret:
                    if u.token == '':
                        return {
                            'code': 200,
                            'msg': 'Token 已过期'
                        }
                    return {
                        'code': 200,
                        'msg': Token.expire(u.token)
                    }
                else:
                    return {
                        'code': 300,
                        'msg': 'Secret 错误'
                    }
            except:
                return {
                    'code': 400,
                    'msg': '数据库访问失败'
                }
        except:
            return {
                'code': 500,
                'msg': '请联系系统管理员！'
            }

    @app.route('/api/signup', methods=['POST'])
    def signup():
        try:
            data = json.loads(request.get_data())
            name = data['name']
            secret = data['secret']
            mail = data['mail']
            token = ''
            try:
                u = DB().queryByName(name)
                if u is not None:
                    return {
                        'code': 200,
                        'msg': '用户已存在'
                    }

                DB().insert(User(0, name, secret, mail, token))
                return {
                    'code': 200,
                    'msg': '注册成功'
                }
            except:
                return {
                    'code': 400,
                    'msg': '数据库访问失败'
                }
        except:
            return {
                'code': 500,
                'msg': '请联系系统管理员！'
            }

    @app.route('/api/delete', methods=['POST'])
    def delete():
        try:
            data = json.loads(request.get_data())
            name = data['name']
            secret = data['secret']
            try:
                u = DB().queryByName(name)
                if u.secret == secret:
                    DB().delete(u)
                    return {
                        'code': 200,
                        'msg': '删除成功'
                    }
                else:
                    return {
                        'code': 300,
                        'msg': 'Secret 错误'
                    }
            except:
                return {
                    'code': 400,
                    'msg': '数据库访问失败'
                }
        except:
            return {
                'code': 500,
                'msg': '请联系系统管理员！'
            }

    @app.route('/api/auth/<code>', methods=['GET'])
    def auth(code):
        try:
            r = Robot(User(0, '1', '', '', ''))
            try:
                if not r.auth(code):
                    return {
                        'code': 300,
                        'msg': '认证失败'
                    }
            except:
                return {
                    'code': 300,
                    'msg': '认证失败'
                }

            token_data = Token.decode(r.user.token)
            if token_data is None:
                return {
                    'code': 300,
                    'msg': 'Token 不合法'
                }

            name = token_data['payload']['sub']
            try:
                u = DB().queryByName(name)
                if u is None:
                    return {
                        'code': 300,
                        'msg': '用户未注册'
                    }

                u.token = r.user.token
                DB().update(u)
                return {
                    'code': 200,
                    'msg': '更新Token成功'
                }
            except:
                return {
                    'code': 400,
                    'msg': '数据库访问失败'
                }
        except:
            return {
                'code': 500,
                'msg': '请联系系统管理员！'
            }

    return app


app = create_app()

if __name__ == '__main__':
    app.run()
