import snowboydecoder
import wave
import sys
import time
import os
from pyaudio import PyAudio, paInt16
import time
from pydub import AudioSegment
from pydub.playback import play as play_music
import urllib.request
import pandas as pd
from random import choice
from chatyuan import ChatYuan
from whisper import ASR
from tts import TTS


interrupted = False  # snowboy监听唤醒结束标志
endSnow = False  # 程序结束标志
framerate = 16000  # 采样率
num_samples = 2000  # 采样点
channels = 1  # 声道
sampwidth = 2  # 采样宽度2bytes
FILEPATH = "./resources/sst.wav"  # 录制完成存放音频路径
music_open = "./resources/ding.wav"  # 唤醒系统打开语音
os.close(sys.stderr.fileno())  # 去掉错误警告


def interrupt_callback():
    """
    监听唤醒
    """
    global interrupted
    return interrupted


def detected():
    """
    唤醒成功
    """
    play(music_open)
    global interrupted
    interrupted = True
    detector.terminate()


def play(filename):
    """
    播放音频
    """
    wf = wave.open(filename, "rb")  # 打开audio.wav
    p = PyAudio()  # 实例化 pyaudio
    # 打开流
    stream = p.open(
        format=p.get_format_from_width(wf.getsampwidth()),
        channels=wf.getnchannels(),
        rate=wf.getframerate(),
        output=True,
    )
    data = wf.readframes(1024)
    while data != b"":
        data = wf.readframes(1024)
        stream.write(data)
    # 释放IO
    stream.stop_stream()
    stream.close()
    p.terminate()


def save_wave_file(filepath, data):
    """
    存储文件
    """
    wf = wave.open(filepath, "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(sampwidth)
    wf.setframerate(framerate)
    wf.writeframes(b"".join(data))
    wf.close()


def my_record():
    """
    录音
    """
    pa = PyAudio()
    stream = pa.open(
        format=paInt16,
        channels=channels,
        rate=framerate,
        input=True,
        frames_per_buffer=num_samples,
    )
    my_buf = []
    t = time.time()
    print("正在录音...\n")
    while time.time() < t + 3:  # 秒
        string_audio_data = stream.read(num_samples)
        my_buf.append(string_audio_data)
    save_wave_file(FILEPATH, my_buf)
    stream.close()


def speech2text():
    """
    音频转文字
    """
    text = ASR.speech2text(FILEPATH)
    print("【语音识别结果】  %s\n" % (text))
    return text


def text2speech(text):
    """
    文字转音频，并实时播放
    """
    TTS.text2speech(text)
    print("正在保存音频...\n")
    birdsound = AudioSegment.from_mp3("resources/tts.mp3")
    print("正在回答问题...\n")
    play_music(birdsound)


def music(text):
    if text == ("播放音乐" or "播放音樂"):
        music_list = pd.read_csv("./resources/music_list.csv", usecols=["URL"])
        LIST = [i for i in music_list.URL]
        url = choice(LIST)
        filename = "./resources/music.mp3"
        print("正在下载音乐....\n")
        urllib.request.urlretrieve(url, filename)
        birdsound = AudioSegment.from_mp3(filename)
        print("正在播放音乐...\n")
        play_music(birdsound)
    else:
        result_text = ChatYuan.text2text(text)
        print("【机器人回复】  {}\n".format(result_text))
        text2speech(result_text)


if __name__ == "__main__":
    while endSnow == False:
        interrupted = False
        # 实例化snowboy，第一个参数就是唤醒识别模型位置
        detector = snowboydecoder.HotwordDetector(
            "./resources/xiaozhixiaozhi.pmdl", sensitivity=0.5
        )
        print("等待唤醒...\n")
        # snowboy监听循环
        detector.start(
            detected_callback=detected,
            interrupt_check=interrupt_callback,
            sleep_time=0.03,
        )
        my_record()  # 唤醒成功开始录音
        text = speech2text()
        music(text)
