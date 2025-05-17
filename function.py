import random
import re
import socket
import cv2
import psutil
import pywifi
import face_recognition as fr
from base64 import b64decode
from websearch import search
from ping3 import ping
from homeassistant_api import Client as hClient
from tts import *

wifi = pywifi.PyWiFi()
try:
    iface = wifi.interfaces()[net_num]
except:
    print("未连接无线网卡或网卡编号设置错误，可前往config.py修改net_num")


def get_news(msg):  # 新闻查询
    url = 'https://weibo.com/ajax/side/hotSearch'
    try:
        response = rq.get(url)
        result = response.json()['data']
        hot_names = []
        for item in result.get('realtime', []):
            hot_names.append(item.get('word', ''))
        res = '\n'.join(hot_names)
        client = OpenAI(base_url=glm_url, api_key=glm_key)
        completion = client.chat.completions.create(model=glm_llm_model, messages=[{"role": "user",
                                                                                    "content": f"{res}。上面是完整的新闻热搜，请你根据这些热搜，分析并发表你的观点见解并回答我的问题，我的问题是：{msg}？回答不要超过200个字"},
                                                                                   {"role": "system",
                                                                                    "content": "请你扮演一名专业的新闻评论员和我对话，完整阅读我给你的新闻热搜，并简要地回答我的问题。"}])
        return completion.choices[0].message.content
    except:
        return "新闻查询服务异常"


def get_weather():  # 天气查询
    def get_weather_domain():
        return b64decode('bG9saW1p').decode('utf-8')

    api = f"https://api.{get_weather_domain()}.cn/API/weather/?city={weather_city}"
    try:
        res = rq.get(api).json()
        return f"{weather_city}天气{res['data']['weather']}，现在{res['data']['current']['weather']}，气温{res['data']['current']['temp']}度，湿度{res['data']['current']['humidity']}，空气质量指数{res['data']['current']['air']}，{res['data']['current']['wind']}{res['data']['current']['windSpeed']}"
    except:
        return "天气查询服务异常"


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
        client = OpenAI(base_url=glm_url, api_key=glm_key)
        completion = client.chat.completions.create(model=glm_llm_model, messages=[{"role": "user",
                                                                                    "content": f"{search_result}。上面是完整的搜索结果，请你根据这些搜索结果，分析并回答我的问题，我的问题是：{msg}？"},
                                                                                   {"role": "system",
                                                                                    "content": "你是一个专业的搜索总结助手，我输入我的问题和杂乱的内容，你输出整理好的内容为详细的一段话，不要分段"}])
        return completion.choices[0].message.content
    except:
        return "联网搜索服务异常"


def play_music(song_name):  # 音乐播放
    music_folder = "data/music"
    try:
        mp3_files = [f for f in os.listdir(music_folder) if f.endswith('.mp3')]
        for character in song_name:
            matched_songs = [song for song in mp3_files if character in song]
            if matched_songs:
                selected_song = random.choice(matched_songs)
                song_name = selected_song.replace(".mp3", "").replace("data/music\\", "")
                break
        else:
            selected_song = random.choice(mp3_files)
            song_name = selected_song.replace(".mp3", "").replace("data/music\\", "")
        play_tts(f"请欣赏我唱{song_name}")
        audio_path = os.path.join(music_folder, selected_song)
        pg.init()
        pg.mixer.music.load(audio_path)
        pg.mixer.music.set_volume(0.25)
        pg.mixer.music.play()
        while pg.mixer.music.get_busy():
            pg.time.Clock().tick(1)
    except Exception as e:
        print(f"音乐播放服务出错，错误详情：{e}")


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


def switch_asr_mode():
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


with open("data/db/current_asr.txt", "w", encoding="utf-8") as file:
    file.write(prefer_asr)
