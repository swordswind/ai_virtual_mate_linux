import logging
from flask import Flask, jsonify, send_from_directory, request
from llm import *

app = Flask(__name__, static_folder='dist')
logging.getLogger('werkzeug').setLevel(logging.ERROR)
robot_data = {'battery_percent': '未连接', 'speed_x': '未连接', 'speed_y': '未连接', 'acc_x': '未连接',
              'acc_y': '未连接', 'acc_z': '未连接', 'gyro_x': '未连接', 'gyro_y': '未连接', 'gyro_z': '未连接'}


def get_local_ip():  # 获取本机IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('223.5.5.5', 1))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    return ip


lan_ip = get_local_ip()


def parse_data(bytes_list):  # 解析数据
    if bytes_list.startswith("7b") and bytes_list.endswith("7d") and len(bytes_list) == 48:
        bytes_list = ' '.join(bytes_list[i:i + 2] for i in range(0, len(bytes_list), 2))
        bytes_list = bytes_list.split()
        # XY双轴速度
        speed_x = int(bytes_list[2] + bytes_list[3], 16)
        if speed_x > 32767:
            speed_x = -(65536 - speed_x)
        speed_x = speed_x * 0.001
        speed_y = int(bytes_list[4] + bytes_list[5], 16)
        if speed_y > 32767:
            speed_y = -(65536 - speed_y)
        speed_y = speed_y * 0.001
        speed_z = int(bytes_list[6] + bytes_list[7], 16)
        if speed_z > 32767:
            speed_z = -(65536 - speed_z)
        speed_z = speed_z * 0.0573
        # IMU三轴加速度
        imu_acc_x = int(bytes_list[8] + bytes_list[9], 16)
        if imu_acc_x > 32767:
            imu_acc_x = -(65536 - imu_acc_x)
        imu_acc_x = imu_acc_x * 19.6 / (2 ** 15)
        imu_acc_y = int(bytes_list[10] + bytes_list[11], 16)
        if imu_acc_y > 32767:
            imu_acc_y = -(65536 - imu_acc_y)
        imu_acc_y = imu_acc_y * 19.6 / (2 ** 15)
        imu_acc_z = int(bytes_list[12] + bytes_list[13], 16)
        if imu_acc_z > 32767:
            imu_acc_z = -(65536 - imu_acc_z)
        imu_acc_z = imu_acc_z * 19.6 / (2 ** 15)
        # 三轴角速度
        gyro_x = int(bytes_list[14] + bytes_list[15], 16)
        if gyro_x > 32767:
            gyro_x = -(65536 - gyro_x)
        gyro_x = gyro_x * 500 / (2 ** 15)
        gyro_y = int(bytes_list[16] + bytes_list[17], 16)
        if gyro_y > 32767:
            gyro_y = -(65536 - gyro_y)
        gyro_y = gyro_y * 500 / (2 ** 15)
        # 电池电压
        battery_voltage = int(bytes_list[20] + bytes_list[21], 16)
        battery_voltage = battery_voltage * 0.001
        return speed_x, speed_y, imu_acc_x, imu_acc_y, imu_acc_z, gyro_x, gyro_y, speed_z, battery_voltage
    return None


def update_robot_state():  # 更新机器人状态
    global robot_data
    try:
        ser = Serial(robot_port, 115200, timeout=0.1)
        line = ser.readline()
        stm32_output = line.hex()[:48]
        ser.close()
        stm32_result = parse_data(stm32_output)
        if stm32_result:
            cell_voltage = stm32_result[8]
            cell_percent = int(((cell_voltage - 20) / (23.5 - 20)) * 99 + 1)
            cell_percent = max(0, min(100, cell_percent))
            robot_data = {'battery_percent': f"{cell_percent}%", 'speed_x': f"{stm32_result[0]:.3f} m/s",
                          'speed_y': f"{stm32_result[1]:.3f} m/s", 'acc_x': f"{stm32_result[2]:.3f} m/s²",
                          'acc_y': f"{stm32_result[3]:.3f} m/s²", 'acc_z': f"{stm32_result[4]:.3f} m/s²",
                          'gyro_x': f"{stm32_result[5]:.3f} °/s", 'gyro_y': f"{stm32_result[6]:.3f} °/s",
                          'gyro_z': f"{stm32_result[7]:.3f} °/s"}
    except:
        pass


@app.route('/')
def index():
    html = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="icon" type="image/png" href="assets/image/logo.png"/>
        <title>主机状态 - 枫云AI虚拟伙伴Linux版</title>
    </head>
    <body style="margin:0; padding:0; box-sizing:border-box;">
        <div style="width:100%; height:100vh; overflow:auto; padding:10px; box-sizing:border-box;">
            <h1><img src="assets/image/logo.png" alt="Logo" style="width:25px; height:25px; margin-right:5px;">枫云AI虚拟伙伴Linux版</h1>
            <h2>硬件状态</h2>
            <p>CPU使用率：<span id="cpu_percent"></span>% | 内存使用率：<span id="memory_percent"></span>% | 内部温度：<span id="temp"></span>℃</p>
            <h2>网络状态</h2>
            <p>外部网络：<span id="net_info"></span> | WiFi：<span id="wifi_info"></span></p>
            <h2>网址信息</h2>
            <p>2D角色网址：<a href="#" id="live2d_url" target="_blank"></a></p>
            <p>3D角色网址：<a href="#" id="mmd_url" target="_blank"></a></p>
            <p>3D动作网址：<a href="#" id="vmd_url" target="_blank"></a></p>
            <p>机器人控制网址：<a href="#" id="control_url" target="_blank"></a></p>
            <h2>AI聊天</h2>
            <div style="display:flex; gap:10px; margin-bottom:20px;">
                <input type="text" id="chat_input" placeholder="请输入消息..." style="flex:1; padding:8px; border:1px solid #ccc; border-radius:4px;">
                <button id="send_button" style="padding:8px 16px; background-color:#4CAF50; color:white; border:none; border-radius:4px; cursor:pointer;">发送</button>
            </div>
            <h2>机器人状态</h2>
            <table border="1" style="width:100%; border-collapse:collapse;">
                <tr>
                    <td>电池电量</td>
                    <td>X方向速度</td>
                    <td>Y方向速度</td>
                </tr>
                <tr>
                    <td><span id="robot_battery_percent">--</span></td>
                    <td><span id="robot_speed_x">--</span></td>
                    <td><span id="robot_speed_y">--</span></td>
                </tr>
                <tr>
                    <td>X方向加速度</td>
                    <td>Y方向加速度</td>
                    <td>Z方向加速度</td>
                </tr>
                <tr>
                    <td><span id="robot_acc_x">--</span></td>
                    <td><span id="robot_acc_y">--</span></td>
                    <td><span id="robot_acc_z">--</span></td>
                </tr>
                <tr>
                    <td>X方向角速度</td>
                    <td>Y方向角速度</td>
                    <td>Z方向角速度</td>
                </tr>
                <tr>
                    <td><span id="robot_gyro_x">--</span></td>
                    <td><span id="robot_gyro_y">--</span></td>
                    <td><span id="robot_gyro_z">--</span></td>
                </tr>
            </table>
            <script>
                function updateInfo() {
                    fetch('/api/info')
                       .then(response => response.json())
                       .then(data => {
                            document.getElementById('cpu_percent').textContent = data.cpu_percent;
                            document.getElementById('memory_percent').textContent = data.memory_percent;
                            document.getElementById('temp').textContent = data.temp;
                            document.getElementById('net_info').textContent = data.net_info;
                            document.getElementById('wifi_info').textContent = data.wifi_info;
                            document.getElementById('live2d_url').textContent = data.live2d_url;
                            document.getElementById('live2d_url').href = data.live2d_url;
                            document.getElementById('mmd_url').textContent = data.mmd_url;
                            document.getElementById('mmd_url').href = data.mmd_url;
                            document.getElementById('vmd_url').textContent = data.vmd_url;
                            document.getElementById('vmd_url').href = data.vmd_url;
                            document.getElementById('control_url').textContent = data.control_url;
                            document.getElementById('control_url').href = data.control_url;
                            document.getElementById('robot_battery_percent').textContent = data.robot_data.battery_percent;
                            document.getElementById('robot_speed_x').textContent = data.robot_data.speed_x;
                            document.getElementById('robot_speed_y').textContent = data.robot_data.speed_y;
                            document.getElementById('robot_acc_x').textContent = data.robot_data.acc_x;
                            document.getElementById('robot_acc_y').textContent = data.robot_data.acc_y;
                            document.getElementById('robot_acc_z').textContent = data.robot_data.acc_z;
                            document.getElementById('robot_gyro_x').textContent = data.robot_data.gyro_x;
                            document.getElementById('robot_gyro_y').textContent = data.robot_data.gyro_y;
                            document.getElementById('robot_gyro_z').textContent = data.robot_data.gyro_z;
                        })
                       .catch(error => {
                            console.error('Error fetching data:', error);
                        });
                }
                document.getElementById('send_button').addEventListener('click', function() {
                    const message = document.getElementById('chat_input').value;
                    if (message.trim() === '') return;
                    fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({message: message})
                    })
                    .then(response => {
                        if (response.ok) {
                            console.log('命令已发送');
                            document.getElementById('chat_input').value = '';
                        } else {
                            console.error('发送命令失败');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
                });
                document.getElementById('chat_input').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        document.getElementById('send_button').click();
                    }
                });
                updateInfo();
                setInterval(updateInfo, 5000);
            </script>
        </div>
    </body>
    </html>
    """
    return html


@app.route('/api/info')
def get_info():
    try:
        temps = psutil.sensors_temperatures()
        temp = int(temps[next(iter(temps))][0].current)
    except:
        temp = "未知"
    if embody_ai_switch == "ON":
        update_robot_state()
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory_percent = psutil.virtual_memory().percent
    net_info = get_net_info()
    wifi_info = get_wifi_info()
    return jsonify({'cpu_percent': cpu_percent, 'memory_percent': memory_percent, 'temp': temp,
                    'net_info': net_info, 'wifi_info': wifi_info, 'live2d_url': f"http://{lan_ip}:{live2d_port}",
                    'mmd_url': f"http://{lan_ip}:{mmd_port}", 'vmd_url': f"http://{lan_ip}:{mmd_port}/vmd",
                    'control_url': f"http://{lan_ip}:{control_port}", 'robot_data': robot_data})


@app.route('/api/chat', methods=['POST'])
def handle_chat():
    data = request.json
    message = data.get('message')
    if message:
        try:
            chat_preprocess(message)
            return jsonify({'status': 'success'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    return jsonify({'status': 'error', 'message': '消息未提供'}), 400


@app.route('/assets/<path:path>')
def serve_static(path):  # 静态资源
    return send_from_directory('./dist/assets', path)


def run_state_web():  # 启动主机状态监测服务
    print(f"主机状态网址：http://{lan_ip}:{str(state_port)}")
    app.run(port=state_port, host="0.0.0.0")
