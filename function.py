import re
import socket
import cv2
import psutil
import pywifi
import face_recognition as fr
import mediapipe as mp
from base64 import b64decode
from xml.etree import ElementTree
from homeassistant_api import Client as hClient
from ping3 import ping
from ultralytics import YOLO
from websearch import search
from tts import *

wifi = pywifi.PyWiFi()
try:
    iface = wifi.interfaces()[net_num]
except:
    print("未连接无线网卡或网卡编号设置错误，可前往config.py修改net_num")
pose, yolo_model = None, None


def function_llm(fc_prompt, msg):  # 函数大语言模型
    client = OpenAI(base_url=glm_url, api_key=glm_key)
    completion = client.chat.completions.create(
        model=glm_llm_model, messages=[{"role": "user", "content": msg}, {"role": "system", "content": fc_prompt}])
    return completion.choices[0].message.content


def get_news(msg):  # 新闻查询
    def get_news_from_wb():
        response = rq.get('https://weibo.com/ajax/side/hotSearch')
        result = response.json()['data']
        hot_names = []
        for item in result.get('realtime', []):
            hot_names.append(item.get('word', ''))
        return '\n'.join(hot_names)

    def get_news_from_zxw(news_url):
        res = rq.get(news_url)
        xml_content = res.content.decode("utf-8")
        root1 = ElementTree.fromstring(xml_content)
        titles = []
        for item in root1.findall(".//item"):
            title_elem = item.find("title")
            if title_elem is not None and title_elem.text:
                titles.append(title_elem.text.strip())
        result = "\n".join(titles)
        return result

    try:
        if "微博" in msg:
            news_result = get_news_from_wb()
        elif "世界" in msg or "国际" in msg:
            news_result = get_news_from_zxw("https://www.chinanews.com.cn/rss/world.xml")
        elif "财经" in msg or "经济" in msg:
            news_result = get_news_from_zxw("https://www.chinanews.com.cn/rss/finance.xml")
        else:
            news_result = get_news_from_zxw("https://www.chinanews.com.cn/rss/society.xml")
        answer = function_llm(f"{prompt}。请你根据新闻信息和我对话",
            f"{news_result}。上面是完整的新闻热搜，请你根据这些热搜，分析并发表你的观点见解并回答我的问题，我的问题是：{msg}？回答不要超过100个字")
        return answer
    except:
        return "新闻服务维护中，请一段时间后再试"


def get_weather():  # 天气查询
    def get_weather_domain():
        return b64decode('bG9saW1p').decode('utf-8')

    api = f"https://api.{get_weather_domain()}.cn/API/weather/?city={weather_city}"
    try:
        res = rq.get(api).json()
        return f"{weather_city}{res['data']['weather']}，现在{res['data']['current']['weather']}，气温{res['data']['current']['temp']}度，湿度{res['data']['current']['humidity']}，空气质量指数{res['data']['current']['air']}，{res['data']['current']['wind']}{res['data']['current']['windSpeed']}"
    except:
        return "气象第三方服务异常，请检查城市名或一段时间后试"


def get_wifi_info():  # WiFi强度查询
    try:
        if iface.status() == pywifi.const.IFACE_CONNECTED:
            iface.scan()
            time.sleep(1)
            scan_results = iface.scan_results()
            result = scan_results[0]
            signal = result.signal
            if signal >= -25:
                signal_percent = 100
            elif signal <= -95:
                signal_percent = 0
            else:
                signal_percent = int((signal - (-95)) / ((-25) - (-95)) * 100)
            return f"信号强度为{signal_percent}%"
        return "WiFI已开启，但未连接"
    except:
        return "WiFI未开启"


def get_net_info():  # 网络延迟查询
    try:
        net_delay = ping("223.5.5.5", timeout=10, unit="ms")
        return f"网络延迟{int(net_delay)}毫秒"
    except:
        return "外部网络未连接"


def get_lan_url():  # 局域网地址查询
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('223.5.5.5', 1))
            ip = s.getsockname()[0]
        except:
            ip = '127.0.0.1'
        return ip

    lan_url = f"IP地址为{get_local_ip()}，2D角色网页端口{live2d_port}，3D角色端口{mmd_port}，3D动作端口网址为{mmd_port}/vmd"
    return lan_url


def get_state():  # 系统状态查询
    try:
        temps = psutil.sensors_temperatures()
        temp = int(temps[next(iter(temps))][0].current)
    except:
        temp = "未知"
    state = f"温度{temp}度，处理器使用率{psutil.cpu_percent(interval=1)}%，内存使用率{psutil.virtual_memory().percent}%"
    return state


def ol_search(msg):  # 联网搜索
    msg = re.sub(r"联网|连网|搜索|查|查询|查找|资料", "", msg)
    try:
        results = search(msg, num_results=5)
        search_result = results[0].get('abstract') + results[1].get('abstract') + results[2].get('abstract') + results[
            3].get('abstract') + results[4].get('abstract')
        answer = function_llm(
            "你是一个专业的搜索总结助手，我输入我的问题和杂乱的内容，你输出整理好的内容为详细的一段话，不要分段",
            f"{search_result}。上面是完整的搜索结果，请你根据这些搜索结果，分析并回答我的问题，我的问题是：{msg}？")
        return answer
    except:
        return "联网搜索服务维护中，请一段时间后再试"


def control_ha():  # Home Assistant控制
    try:
        client = hClient(f"{ha_api}/api/", ha_key)
        button = client.get_domain("button")
    except:
        return "Home Assistant配置错误"
    try:
        result = button.press(entity_id=entity_id)
        if len(result) == 0:
            return "设备不在线"
    except:
        return "设备不在线"
    return "操作成功"


def input_face(msg):  # 录入人脸
    name = msg.replace("录入人脸", "").replace("我", "").replace("是", "").replace("你", "")
    try:
        cap = cv2.VideoCapture(cam_num)
        ret, frame = cap.read()
        cap.release()
        cv2.imencode('.jpg', frame)[1].tofile(f'data/image/face/{name}.jpg')
        return "我现在认识你啦"
    except Exception as e:
        return f"录入人脸服务异常，错误详情：{e}"


def delete_face():  # 删除人脸
    folder_path = 'data/image/face'
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    jpg_files = [f for f in files if f.lower().endswith('.jpg')]
    if not jpg_files:
        return
    latest_file = max(jpg_files, key=lambda f: os.path.getmtime(os.path.join(folder_path, f)))
    os.remove(os.path.join(folder_path, latest_file))
    return "最新的人脸删除啦"


def recog_face():  # 人脸识别
    known_face_encodings = []  # 加载已知的人脸图像和对应的姓名
    known_face_names = []
    image_folder = "data/image/face"  # 遍历image文件夹中的所有图片
    try:
        for filename in os.listdir(image_folder):
            if filename.endswith(".jpg"):
                name = os.path.splitext(filename)[0]
                image_path = os.path.join(image_folder, filename)
                image = fr.load_image_file(image_path)
                face_encoding = fr.face_encodings(image)[0]
                known_face_encodings.append(face_encoding)
                known_face_names.append(name)
        cap = cv2.VideoCapture(cam_num)
        ret, frame = cap.read()
        cap.release()
        rgb_frame = np.ascontiguousarray(frame[:, :, ::-1])  # 将画面转换为RGB格式
        face_locations = fr.face_locations(rgb_frame)  # 检测画面中的人脸
        face_encodings = fr.face_encodings(rgb_frame, face_locations)
        for face_encoding in face_encodings:  # 遍历检测到的人脸
            matches = fr.compare_faces(known_face_encodings, face_encoding)  # 与已知的人脸进行比对
            if True in matches:  # 如果找到匹配的人脸
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                return f"我当然知道你啦，你是{name}"
            else:
                return "初次见面，很高兴认识你"
        return "你在哪呢，我没看到你哦"
    except Exception as e:
        return f"人脸识别服务异常，错误详情：{e}"


def check_person(cap):  # 人物检测
    global pose
    if pose is None:
        pose = mp.solutions.pose.Pose()
    ret, frame = cap.read()
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image)
    if results.pose_landmarks:
        return "有人"
    return "无人"


def check_yolo(obj, cap):  # 物体检测
    global yolo_model
    if yolo_model is None:
        yolo_model = YOLO('data/model/YOLO/yolo11n.pt')
    obj_dict = {"书本": "book", "手机": "cell phone", "杯子": "cup", "剪刀": "scissors", "苹果": "apple",
                "橙子": "orange", "香蕉": "banana"}
    obj = obj_dict.get(obj, obj)
    ret, frame = cap.read()
    results = yolo_model(frame)
    for result in results:
        for box in result.boxes:
            class_id = int(box.cls)
            class_name = yolo_model.names[class_id]  # 获取类别名称
            if class_name == obj:
                return True
    return False


def exit_app():  # 退出程序
    res = f"{mate_name}即将退出，再见"
    print(f"{mate_name}：{res}")
    play_tts(res)
    os.kill(os.getpid(), 15)


def reboot():  # 重启
    res = f"{mate_name}即将重启，等会见"
    print(f"{mate_name}：{res}")
    play_tts(res)
    try:
        os.system("reboot -h now")
    except:
        print("重启失败，该操作需要root权限")


def shutdown():  # 关机
    res = f"{mate_name}即将关机，再见"
    print(f"{mate_name}：{res}")
    play_tts(res)
    try:
        os.system("shutdown -h now")
    except:
        print("关机失败，该操作需要root权限")


def switch_asr_mode():  # 切换语音模式
    with open("data/db/current_asr.txt", "r", encoding="utf-8") as f:
        current_asr = f.read()
    if current_asr == "RealTime":
        with open("data/db/current_asr.txt", "w", encoding="utf-8") as f:
            f.write("WakeWord")
        return "已切换为唤醒词模式"
    elif current_asr == "WakeWord":
        with open("data/db/current_asr.txt", "w", encoding="utf-8") as f:
            f.write("RealTime")
        return "已切换为实时语音模式"


def switch_ase_mode():  # 切换主动对话模式
    with open("data/db/current_ase.txt", "r", encoding="utf-8") as f:
        current_ase = f.read()
    if current_ase == "ON":
        with open("data/db/current_ase.txt", "w", encoding="utf-8") as f:
            f.write("OFF")
        return "已关闭主动感知对话"
    elif current_ase == "OFF":
        with open("data/db/current_ase.txt", "w", encoding="utf-8") as f:
            f.write("ON")
        return "已开启主动感知对话"


with open("data/db/current_asr.txt", "w", encoding="utf-8") as file:
    file.write(prefer_asr)
with open("data/db/current_ase.txt", "w", encoding="utf-8") as file:
    file.write(prefer_ase)
