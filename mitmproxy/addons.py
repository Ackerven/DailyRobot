# @Author: Ackerven
# @Mail: ackerven@qq.com
# @Time: 2022/12/26 18:25
# @File: addons.py.py
# OS: Windows 10
# IDE: PyCharm
# @Copyright Copyright(C) 2022 Ackerven All rights reserved.

import mitmproxy.http
import requests
from mitmproxy import http


class Interceptor:
    def __init__(self):
        pass

    def request(self, flow: mitmproxy.http.HTTPFlow):
        if flow.request.host == 'robot.erha.fun':
            return
        if flow.request.host == 'xxcj.bnuzh.edu.cn' and flow.request.path.startswith('/health-punch'):
            url = flow.request.url
            code = url.split('=')[-1]
            print(code)
            resp = requests.get('http://127.0.0.1:2023/api/auth/{}'.format(code))
            print(resp.text)
            flow.response = http.Response.make(200, resp.text)
            return
        else:
            # flow.response = http.Response.make(302, headers={'Location': 'https://robot.erha.fun/api/'})
            flow.response = http.Response.make(200,
                                               '此代理仅用于获取打卡认证的code，如需访问其他网站，请先断开代理。\n请访问 http://robot.erha.fun/docs/ 获取更多信息')

        return


addons = [Interceptor()]
