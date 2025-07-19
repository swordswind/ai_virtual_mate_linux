# AI引擎选择
prefer_asr = "RealTime"  # 语音识别模式，可选项：RealTime/WakeWord/OFF
prefer_llm = "ZhipuAI"  # 对话语言模型，可选项：ZhipuAI/OpenAI/Ollama/LM Studio/AnythingLLM/Dify/RKLLM
prefer_tts = "edge-tts"  # 语音合成引擎，可选项：edge-tts/GPT-SoVITS/CosyVoice/Kokoro-TTS/Spark-TTS/Index-TTS/CustomTTS/espeak/OFF
prefer_vlm = "ZhipuAI"  # 图像识别引擎，可选项：ZhipuAI/OpenAI/Ollama/QwenVL/GLM-V/Janus/YOLO-OCR/OFF
prefer_ase = "OFF"  # 主动感知对话，可选项：ON/OFF
# 基本信息设置
username = "开拓者"  # 用户名
mate_name = "小月"  # 虚拟伙伴名称
# 虚拟伙伴人设
prompt = "请你扮演小月，与开拓者对话。小月是一个活泼可爱的的少女，乐观好奇，随身携带相机记录冒险。在对话中，你将作为小月，隐藏自己是程序的事实，使用角色语气交流，全程称对方为开拓者。注意保持角色一致，不能提及任何关于自己是语言模型或人工智能的话题。你的回答不要包含emoji，尽量不要超过100个字"
prompt = prompt + "/no_think"  # 设置为非思考模式(对于混合推理模型)
state_port = 5260  # 主机状态网页端口
live2d_port = 5261  # 2D角色网页端口
mmd_port = 5262  # 3D角色网页端口
# 语音识别设置
speech_end_wait_time = 2  # 语音识别结束等待时间
wake_word = "你好"  # 唤醒词
mic_num = 0  # 麦克风编号
# ZhipuAI设置
glm_url = "https://open.bigmodel.cn/api/paas/v4"  # ZhipuAI地址base_url
glm_key = "xxxxx.xxxxx"  # ZhipuAI密钥api_key
glm_llm_model = "glm-4-flash-250414"  # ZhipuAI大语言模型llm-model
glm_vlm_model = "glm-4v-flash"  # ZhipuAI视觉语言模型vlm-model
# OpenAI兼容设置
openai_url = "https://api.siliconflow.cn/v1"  # OpenAI兼容地址base_url
openai_key = "sk-xxxxxxxxxx"  # OpenAI兼容密钥api_key
openai_llm_model = "Qwen/Qwen3-8B"  # OpenAI兼容大语言模型llm-model
openai_vlm_model = "Pro/Qwen/Qwen2.5-VL-7B-Instruct"  # OpenAI兼容视觉语言模型vlm-model
# Ollama和LM Studio设置
ollama_url = "http://127.0.0.1:11434"  # Ollama地址host
ollama_llm_model = "qwen3:0.6b"  # Ollama大语言模型llm-model
ollama_vlm_model = "qwen2.5vl:3b"  # Ollama视觉语言模型vlm-model
lmstudio_url = "http://192.168.31.254:1234"  # LM Studio地址
# 知识库设置
anything_llm_ip = "http://192.168.31.254:3001"  # AnythingLLM地址
anything_llm_ws = "aivm"  # AnythingLLM工作区
anything_llm_key = "在AnythingLLM获取"  # AnythingLLM密钥
dify_ip = "http://127.0.0.1"  # Dify地址
dify_key = "app-xxxxxxxxxx"  # Dify密钥
# 语音合成设置
edge_speaker = "zh-CN-XiaoyiNeural"  # edge-tts音色，可选项：zh-CN-XiaoyiNeural/ja-JP-NanamiNeural等，具体用命令edge-tts --list-voices查询
edge_rate = "+0%"  # edge-tts语速
edge_pitch = "+10Hz"  # edge-tts音高
kokoro_speaker = "zf_xiaoyi"  # Kokoro-TTS音色，可选项：zf_xiaobei/zf_xiaoni/zf_xiaoxiao/zf_xiaoyi/zm_yunjian/zm_yunxi/zm_yunxia/zm_yunyang
kokoro_speed = 1.0  # Kokoro-TTS语速
gsv_api = "http://192.168.31.254:9880"  # GPT-SoVITS地址
cosy_api = "http://192.168.31.254:9881"  # CosyVoice地址
spark_api = "http://192.168.31.254:9883"  # Spark-TTS地址
index_api = "http://192.168.31.254:9884"  # Index-TTS地址
custom_tts_url = "https://api.siliconflow.cn/v1"  # 自定义TTS地址
custom_tts_model = "FunAudioLLM/CosyVoice2-0.5B"  # 自定义TTS模型
custom_tts_voice = "FunAudioLLM/CosyVoice2-0.5B:alex"  # 自定义TTS音色
custom_tts_key = "sk-xxxxxxxxxx"  # 自定义TTS密钥
# 图像识别设置
cam_num = 0  # 摄像头编号
qwenvl_api = "http://192.168.31.254:8086"  # QwenVL地址
glmv_api = "http://192.168.31.254:8085"  # GLM-V地址
janus_api = "http://192.168.31.254:8082"  # Janus地址
# Home Assistant设置
ha_api = "http://127.0.0.1:8123"  # Home Assistant地址
ha_key = 'xxxx.xxxx.xxxx-xxxx'  # Home Assistant长期访问令牌
entity_id = "button.yeelink_cn_xxxxxxxxx_lamp4_toggle_a_2_1"  # Home Assistant实体ID
# 其他设置
net_num = 1  # 无线网卡编号
weather_city = "杭州"  # 天气城市
rkllm_url = "http://127.0.0.1:8079"  # RKLLM地址
# 机器人设置
embody_ai_switch = "OFF"  # 机器人开关，可选项：ON/OFF
radar_port = "/dev/ttyACM0"  # 激光雷达串口号
robot_port = '/dev/ttyACM1'  # 机器人串口号
move_gear = 1  # 机器人移动档位(1-6)
rotate_gear = 1  # 机器人旋转档位(1-6)
control_port = 5263  # 控制网页端口
