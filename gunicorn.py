# @Author: Ackerven
# @Mail: ackerven@qq.com
# @Time: 2022/12/26 17:36
# @File: gunicorn.py
# OS: Windows 10
# IDE: PyCharm
# @Copyright Copyright(C) 2022 Ackerven All rights reserved.

workers = 1
workers_class = "gevent"
bind = "0.0.0.0:2023"