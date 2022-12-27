# Daily Robot

新版每日打卡机器人



## 打卡流程

![](https://s2.loli.net/2022/12/05/yi9kHYPnh7Tg1VU.png)



## 部署服务

1. 克隆项目
2. 执行 `pip3 install -r requirements.txt` 安装依赖
3. 执行 `gunicorn -c gunicorn.py main:app` 启动后端
4. 进入 mitmproxy 目录，执行 `mitmdump -s addons.py --listen-port 7890 --set block_global=false` 启动代理
5. 把 website 文件夹里面的静态资源放到 Web 服务器即可