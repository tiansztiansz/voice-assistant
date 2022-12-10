import snowboydecoder
import wave
import sys
import time
import os
from pyaudio import PyAudio, paInt16
from espnet2.bin.asr_inference import Speech2Text
from espnet2.bin.tts_inference import Text2Speech
import soundfile
import time
from pydub import AudioSegment
from pydub.playback import play as play_music
import urllib.request
import pandas as pd
from random import choice


s2t_model = Speech2Text.from_pretrained(
    "espnet/pengcheng_guo_wenetspeech_asr_train_asr_raw_zh_char"
)

t2s_model = Text2Speech.from_pretrained(
    "espnet/kan-bayashi_csmsc_tts_train_tacotron2_raw_phn_pypinyin_g2p_phone_train.loss.best"
)


interrupted = False  # snowboy监听唤醒结束标志
endSnow = False  # 程序结束标志

framerate = 16000  # 采样率
num_samples = 2000  # 采样点
channels = 1  # 声道
sampwidth = 2  # 采样宽度2bytes

FILEPATH = "./resources/audio.wav"  # 录制完成存放音频路径
# music_exit = "./resources/dong.wav"  # 唤醒系统退出语音
music_open = "./resources/ding.wav"  # 唤醒系统打开语音
os.close(sys.stderr.fileno())  # 去掉错误警告


def signal_handler(signal, frame):
    """
    监听键盘结束
    """
    global interrupted
    interrupted = True


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
    print("唤醒成功")
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
    print("开始录音...")
    while time.time() < t + 5:  # 秒
        string_audio_data = stream.read(num_samples)
        my_buf.append(string_audio_data)
    print("录音结束!")
    save_wave_file(FILEPATH, my_buf)
    stream.close()


def speech2text():
    """
    音频转文字
    """
    speech, rate = soundfile.read(FILEPATH)
    text, *_ = s2t_model(speech)[0]
    return text


def text2speech(result_text, firename):
    """
    文字转音频，并实时播放
    """
    speech = t2s_model(result_text)["wav"]
    soundfile.write(firename, speech.numpy(), t2s_model.fs, "PCM_16")
    play(firename)


def music(text):
    if text == "播放音乐":
        music_list = pd.read_csv("./resources/music_list.csv", usecols=["URL"])
        LIST = [i for i in music_list.URL]
        url = choice(LIST)
        filename = "./resources/music.mp3"
        print("正在下载音乐....")
        urllib.request.urlretrieve(url, filename)
        birdsound = AudioSegment.from_mp3(filename)
        print("正在播放音乐...")
        play_music(birdsound)
        print("音乐播放完毕")
    else:
        result_text = "不好意思，你能再说一遍吗"
        firename = "./resources/none.wav"
        text2speech(result_text=result_text, firename=firename)


if __name__ == "__main__":
    while endSnow == False:
        interrupted = False
        # 实例化snowboy，第一个参数就是唤醒识别模型位置
        detector = snowboydecoder.HotwordDetector(
            "./resources/xiaozhixiaozhi.pmdl", sensitivity=0.5
        )
        print("等待唤醒")
        # snowboy监听循环
        detector.start(
            detected_callback=detected,
            interrupt_check=interrupt_callback,
            sleep_time=0.03,
        )
        my_record()  # 唤醒成功开始录音
        text = speech2text()
        print("#### {} #####\n".format(text))
        music(text)
