# @Author: Ackerven
# @Mail: ackerven@qq.com
# @Time: 2022/12/8 23:33
# @File: main.py
# OS: Windows 10
# IDE: PyCharm
# @Copyright Copyright(C) 2022 Ackerven All rights reserved.
import json

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, request

from datascore import DB
from model.bean import User
from model.tool import Notify, Scheduler, Robot
from utils.mail import Postman
from utils.tool import Config, LoggerPool
from utils.tool import Token

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    return 'Hello world!'


@app.route('/login', methods=['POST'])
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


@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = json.loads(request.get_data())
        name = data['name']
        secret = data['secret']
        mail = data['mail']
        token = ''
        try:
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


@app.route('/delete', methods=['POST'])
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


@app.route('/update/<name>/<code>', methods=['GET'])
def update(name, code):
    try:
        try:
            u = DB().queryByName(name)
            r = Robot(u)
            try:
                if not r.auth(code):
                    return {
                        'code': 400,
                        'msg': '认证失败'
                    }
            except:
                return {
                    'code': 400,
                    'msg': '认证失败'
                }

            DB().update(r.user)
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


def init():
    Config('config/config.yml')
    LoggerPool(name='DailyRobot', config=Config().getConfig('log'))
    DB(source='mysql', config=Config().getConfig('db')['mysql'])
    Notify(postman=Postman(Config().getConfig('mail')['smtp']), address='ackerven@qq.com')
    Scheduler(scheduler=BackgroundScheduler(timezone='Asia/Shanghai'))


if __name__ == '__main__':
    init()
    app.config['JSON_AS_ASCII'] = False
    app.run()
