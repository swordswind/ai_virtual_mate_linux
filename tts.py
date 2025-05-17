import asyncio
import os
import time
import edge_tts
import librosa
import pygame as pg
import requests as rq
import soundfile as sf
import numpy as np
from threading import Thread
from kokoro_onnx import Kokoro
from misaki import zh
from openai import OpenAI
from config import *

voice_path = 'data/cache/cache_voice'
wav_path = 'data/cache/cache_voice.wav'
kokoro = None
g2p = zh.ZHG2P()


def play_live2d(path):  # 播放Live2D对口型
    try:
        x, sr = librosa.load(path, sr=8000)
        x = x - min(x)
        x = x / max(x)
        x = np.log(x) + 1
        x = x / max(x) * 1.2
        s_time = time.time()
        for _ in range(int(len(x) / 800)):
            it = x[int((time.time() - s_time) * 8000) + 1]
            if it < 0:
                it = 0
            with open("data/cache/cache.txt", "w") as cache_file:
                cache_file.write(str(float(it)))
            time.sleep(0.1)
    except:
        pass
    time.sleep(0.1)
    with open("data/cache/cache.txt", "w") as cache_file:
        cache_file.write("0")


def play_voice(path):  # 播放语音
    pg.init()
    pg.mixer.music.load(path)
    pg.mixer.music.play()
    Thread(target=play_live2d, args=(path,)).start()
    while pg.mixer.music.get_busy():
        pg.time.Clock().tick(1)
    pg.mixer.music.stop()
    pg.quit()


def play_tts(text):  # 语音合成
    async def ms_edge_tts():  # 使用edge_tts进行文本到语音的转换并保存到文件
        communicate = edge_tts.Communicate(text, voice=edge_speaker, rate=edge_rate, pitch=edge_pitch)
        await communicate.save(voice_path)

    text = text.split("</think>")[-1].strip()
    if prefer_tts == "edge-tts":
        asyncio.run(ms_edge_tts())
        play_voice(voice_path)
    elif prefer_tts == "GPT-SoVITS":
        url = f'{gsv_api}/?text={text}&text_language=zh'
        try:
            res = rq.get(url)
            with open(voice_path, 'wb') as f:
                f.write(res.content)
            play_voice(voice_path)
        except Exception as e:
            print(f"GPT-SoVITS整合包API服务器未开启，错误详情：{e}")
    elif prefer_tts == "CosyVoice":
        url = f'{cosy_api}/cosyvoice/?text={text}'
        try:
            res = rq.get(url)
            with open(voice_path, 'wb') as f:
                f.write(res.content)
            play_voice(voice_path)
        except Exception as e:
            print(f"CosyVoice整合包API服务器未开启，错误详情：{e}")
    elif prefer_tts == "Kokoro-TTS":
        try:
            run_kokoro(text)
            play_voice(wav_path)
        except Exception as e:
            print(f"Kokoro-TTS出错，错误详情：{e}")
    elif prefer_tts == "Spark-TTS":
        url = f'{spark_api}/spark/?text={text}'
        try:
            res = rq.get(url)
            with open(voice_path, 'wb') as f:
                f.write(res.content)
            play_voice(voice_path)
        except Exception as e:
            print(f"Spark-TTS整合包API服务器未开启，错误详情：{e}")
    elif prefer_tts == "Index-TTS":
        url = f'{index_api}/indextts/?text={text}'
        try:
            res = rq.get(url)
            with open(voice_path, 'wb') as f:
                f.write(res.content)
            play_voice(voice_path)
        except Exception as e:
            print(f"Index-TTS整合包API服务器未开启，错误详情：{e}")
    elif prefer_tts == "CustomTTS":
        try:
            custom_tts(text)
            play_voice(voice_path)
        except Exception as e:
            print(f"自定义TTS API配置错误，错误详情：{e}")
    elif prefer_tts == "espeak":
        text = text.replace("\n", "")
        try:
            os.system(f"espeak -v zh+f3 {text}")
        except:
            print("您的机器未安装espeak，请执行安装命令\nsudo apt install espeak")


def run_kokoro(text):  # 本地Kokoro-TTS
    global kokoro
    model_path = "data/model/TTS/Kokoro-82M/kokoro-v1.0.fp16.onnx"
    voice_list_path = "data/model/TTS/Kokoro-82M/voices-v1.0.bin"
    if kokoro is None:
        kokoro = Kokoro(model_path, voice_list_path)
    phonemes, _ = g2p(text)
    samples, sample_rate = kokoro.create(text=phonemes, voice=kokoro_speaker, speed=kokoro_speed, is_phonemes=True)
    sf.write(wav_path, samples, sample_rate)


def custom_tts(text):
    client = OpenAI(api_key=custom_tts_key, base_url=custom_tts_url)
    with client.audio.speech.with_streaming_response.create(
            model=custom_tts_model, voice=custom_tts_voice, input=text, response_format="mp3") as response:
        response.stream_to_file(voice_path)
