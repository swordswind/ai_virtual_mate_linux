from flask import jsonify
from llm import *
from live2d import *
from mmd import *

app2 = Flask(__name__, static_folder='dist')


@app2.route('/')
def index2():
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <link rel="icon" type="image/png" href="assets/image/logo.png"/>
        <title>主机状态 - 枫云AI虚拟伙伴Linux版</title>
    </head>
    <body>
        <img src="assets/image/logo.png" alt="Logo" style="position: absolute; top: 10px; left: 10px; width: 50px; height: 50px;">
        <h1>·</h1>
        <h1>枫云AI虚拟伙伴Linux版</h1>
        <h2>主机状态</h2>
        <p>CPU使用率：<span id="cpu_percent"></span>%</p>
        <p>内存使用率：<span id="memory_percent"></span>%</p>
        <p>内部温度：<span id="temp"></span>℃</p>
        <h2>网络信息</h2>
        <p>外部网络信息：<span id="net_info"></span></p>
        <p>WiFi信息：<span id="wifi_info"></span></p>
        <h2>网址信息</h2>
        <p>2D角色网址：http://{lan_ip}:{live2d_port}</p>
        <p>3D角色网址：http://{lan_ip}:{mmd_port}</p>
        <p>3D动作网址：http://{lan_ip}:{mmd_port}/vmd</p>
        <script>
            function updateInfo() {{
                fetch('/api/info')
                   .then(response => response.json())
                   .then(data => {{
                        document.getElementById('cpu_percent').textContent = data.cpu_percent;
                        document.getElementById('memory_percent').textContent = data.memory_percent;
                        document.getElementById('temp').textContent = data.temp;
                        document.getElementById('net_info').textContent = data.net_info;
                        document.getElementById('wifi_info').textContent = data.wifi_info;
                    }});
            }}
            setInterval(updateInfo, 5000);
            updateInfo();
        </script>
    </body>
    </html>
    """
    return html


@app2.route('/api/info')
def get_info():
    try:
        temps = psutil.sensors_temperatures()
        temp = int(temps[next(iter(temps))][0].current)
    except:
        temp = "未知"
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_percent = psutil.virtual_memory().percent
    net_info = get_net_info()
    wifi_info = get_wifi_info()
    return jsonify({'cpu_percent': cpu_percent, 'memory_percent': memory_percent, 'temp': temp,
                    'net_info': net_info, 'wifi_info': wifi_info})


@app2.route('/assets/<path:path>')
def serve_static(path):  # 静态资源
    return send_from_directory('./dist/assets', path)


def run_state_web():  # 启动主机状态监测服务
    print(f"主机状态网址：http://{lan_ip}:{str(state_port)}")
    app2.run(port=state_port, host="0.0.0.0")


def sensevoice_main():  # 语音交互主线程
    from asr import recognize_audio, record_audio
    while True:
        try:
            with open("data/db/current_asr.txt", "r", encoding="utf-8") as f:
                current_asr = f.read()
            if current_asr == "RealTime" or current_asr == "WakeWord":
                say_text = recognize_audio(record_audio())
                if len(say_text) > 1 and current_asr == "RealTime":
                    pg.init()
                    if pg.mixer.music.get_busy():
                        pass
                    else:
                        print(f"{username}：{say_text}")
                        chat_preprocess(say_text)
                elif len(say_text) > 2 and current_asr == "WakeWord" and wake_word in say_text:
                    pg.init()
                    if pg.mixer.music.get_busy():
                        pass
                    else:
                        say_text = say_text.replace(wake_word, "")
                        print(f"{username}：{say_text}")
                        chat_preprocess(say_text)
            else:
                time.sleep(0.1)
        except:
            time.sleep(0.1)


def text_chat():  # 文本聊天线程
    while True:
        pg.quit()
        try:
            msg = input(f"{username}：")
        except:
            print("格式错误，请重新输入消息")
            continue
        if msg == "":
            print("请输入内容后再发送")
            continue
        chat_preprocess(msg)


Thread(target=run_state_web).start()
Thread(target=run_live2d).start()
Thread(target=run_mmd).start()
Thread(target=sensevoice_main).start()
Thread(target=text_chat).start()
pg.init()
pg.mixer.Sound("data/audio/welcome.mp3").play()
while True:
    time.sleep(1)
