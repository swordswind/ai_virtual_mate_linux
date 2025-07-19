import json
import logging
import socket
from flask import Flask, send_from_directory
from config import mmd_port

app = Flask(__name__, static_folder='dist')
logging.getLogger('werkzeug').setLevel(logging.ERROR)


def get_local_ip():  # 获取本机IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('223.5.5.5', 1))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    return ip


lan_ip = get_local_ip()


@app.route('/')
def index():  # MMD角色页面
    return app.send_static_file('mmd_web.html')


@app.route('/vmd')
def index_vmd():  # MMD动作页面
    return app.send_static_file('mmd_vmd_web.html')


@app.route('/assets/<path:path>')
def serve_static(path):  # 静态资源
    if path.endswith(".js"):
        return send_from_directory('./dist/assets', path, mimetype='application/javascript')
    return send_from_directory('./dist/assets', path)


@app.route('/api/get_mouth_y')
def read_txt():  # 读取缓存
    with open("data/cache/cache.txt", "r") as f:
        return json.dumps({"y": f.read()})


def run_mmd():  # 启动MMD服务
    print(f"3D角色网址：http://{lan_ip}:{str(mmd_port)}\n3D动作网址：http://{lan_ip}:{str(mmd_port)}/vmd")
    app.run(port=mmd_port, host="0.0.0.0")
