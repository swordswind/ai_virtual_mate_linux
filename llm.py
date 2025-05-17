import json
from datetime import datetime
from vlm import *

with open('data/db/memory.db', 'r', encoding='utf-8') as memory_file:
    try:
        openai_history = json.load(memory_file)
    except:
        openai_history = []


def current_time():  # 当前时间
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def chat_llm(msg):  # 与大语言模型对话
    if prefer_llm == "ZhipuAI":
        glm_client = OpenAI(base_url=glm_url, api_key=glm_key)
        openai_history.append({"role": "user", "content": msg})
        messages = [{"role": "system", "content": prompt}]
        messages.extend(openai_history)
        completion = glm_client.chat.completions.create(model=glm_llm_model, messages=messages)
        openai_history.append({"role": "assistant", "content": completion.choices[0].message.content})
        return completion.choices[0].message.content
    elif prefer_llm == "OpenAI":
        custom_client = OpenAI(base_url=openai_url, api_key=openai_key)
        openai_history.append({"role": "user", "content": msg})
        messages = [{"role": "system", "content": prompt}]
        messages.extend(openai_history)
        completion = custom_client.chat.completions.create(model=openai_llm_model, messages=messages)
        openai_history.append({"role": "assistant", "content": completion.choices[0].message.content})
        return completion.choices[0].message.content
    elif prefer_llm == "Ollama":
        try:
            rq.get(ollama_url)
        except:
            os.system(f"ollama pull {ollama_llm_model}")
        ollama_client = Client(host=ollama_url)
        openai_history.append({"role": "user", "content": msg})
        messages = [{"role": "system", "content": prompt}]
        messages.extend(openai_history)
        response = ollama_client.chat(model=ollama_llm_model, messages=messages)
        openai_history.append({"role": "assistant", "content": response['message']['content']})
        return response['message']['content']
    elif prefer_llm == "LM Studio":
        lmstudio_client = OpenAI(base_url=f"{lmstudio_url}/v1", api_key="lm-studio")
        openai_history.append({"role": "user", "content": msg})
        messages = [{"role": "system", "content": prompt}]
        messages.extend(openai_history)
        completion = lmstudio_client.chat.completions.create(model="", messages=messages)
        openai_history.append({"role": "assistant", "content": completion.choices[0].message.content})
        return completion.choices[0].message.content
    elif prefer_llm == "AnythingLLM":
        res = chat_anything_llm(msg)
        return res
    elif prefer_llm == "Dify":
        res = chat_dify(msg)
        return res
    else:
        return "对话语言模型选择错误，请检查配置"


def chat_preprocess(msg):  # 对话预处理
    pg.quit()
    try:
        if "几点" in msg or "多少点" in msg or "时间" in msg or "时候" in msg:
            msg = f"[当前时间:{current_time()}]{msg}"
        if "哈喽" in msg:
            res = f"{username}，我是{mate_name}，很高兴遇见你"
        elif "唱一" in msg or "唱首" in msg or "唱歌" in msg or "放歌" in msg or "放一" in msg or "放首" in msg or "你唱" in msg:
            play_music(msg)
            return
        elif (
                "画面" in msg or "图像" in msg or "看到" in msg or "看见" in msg or "照片" in msg or "摄像头" in msg or "图片" in msg) and prefer_vlm != "OFF":
            if prefer_vlm == "ZhipuAI":
                res = glm_4v_cam(msg)
            elif prefer_vlm == "OpenAI":
                res = openai_vlm_cam(msg)
            elif prefer_vlm == "Ollama":
                res = ollama_vlm_cam(msg)
            elif prefer_vlm == "QwenVL":
                res = qwen_vlm_cam(msg)
            elif prefer_vlm == "GLM-V":
                res = glm_v_cam(msg)
            elif prefer_vlm == "Janus":
                res = janus_cam(msg)
            elif prefer_vlm == "YOLO-OCR":
                res = yolo_ocr_cam(msg)
            else:
                res = "图像识别引擎选择错误，请检查配置"
        elif "天气" in msg:
            res = get_weather()
        elif "新闻" in msg:
            res = get_news(msg)
        elif "联网" in msg or "连网" in msg or "搜索" in msg or "查询" in msg or "查找" in msg:
            res = ol_search(msg)
        elif "信号" in msg or "强度" in msg:
            res = get_wifi_info()
        elif "网址" in msg or "地址" in msg or "端口" in msg:
            res = get_lan_url()
        elif "网络" in msg:
            res = get_net_info()
        elif "状态" in msg or "温度" in msg:
            res = get_state()
        elif "灯" in msg and "开" in msg:
            res = control_ha()
        elif "灯" in msg and "关" in msg:
            res = control_ha()
        elif "录入人脸" in msg:
            res = input_face(msg)
        elif "删除人脸" in msg:
            res = delete_face()
        elif "我是谁" in msg:
            res = recog_face()
        elif "切换" in msg and "语音" in msg:
            res = switch_asr_mode()
        elif "设置" in msg or "配置" in msg or "模式" in msg:
            with open("data/db/current_asr.txt", "r", encoding="utf-8") as f:
                current_asr = f.read()
            res = f"语音识别模式为{current_asr}，对话语言模型为{prefer_llm}，语音合成引擎为{prefer_tts}，图像识别引擎为{prefer_vlm}"
        elif "确认删除记忆" in msg or "确定删除记忆" in msg:
            res = clear_chat()
        elif "确定退出" in msg or "确认退出" in msg:
            exit_app()
            return
        elif "确认重新启动" in msg or "确定重新启动" in msg:
            reboot()
            return
        elif "确认关机" in msg or "确定关机" in msg:
            shutdown()
            return
        else:
            res = chat_llm(msg)
        with open('data/db/memory.db', 'w', encoding='utf-8') as f:
            json.dump(openai_history, f, ensure_ascii=False, indent=4)
    except Exception as e:
        res = f"服务异常：{e}"
    res = res.replace("#", "").replace("*", "")
    print(f"{mate_name}：{res}")
    play_tts(res)


def chat_dify(msg):  # Dify知识库
    headers = {"Authorization": f"Bearer {dify_key}", "Content-Type": "application/json"}
    data = {"query": msg, "inputs": {}, "response_mode": "blocking", "user": username, "conversation_id": None}
    res = rq.post(f"{dify_ip}/v1/chat-messages", headers=headers, data=json.dumps(data))
    res = res.json()['answer'].strip()
    return res


def chat_anything_llm(msg):  # AnythingLLM知识库
    url = f"{anything_llm_ip}/api/v1/workspace/{anything_llm_ws}/chat"
    headers = {"Authorization": f"Bearer {anything_llm_key}", "Content-Type": "application/json"}
    data = {"message": msg}
    res = rq.post(url, json=data, headers=headers)
    return res.json().get("textResponse")


def clear_chat():  # 删除记忆
    global openai_history
    openai_history = []
    with open('data/db/memory.db', 'w', encoding='utf-8') as f:
        f.write("")
    return "记忆已清空"
