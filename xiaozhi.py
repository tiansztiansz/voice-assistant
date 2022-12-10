import snowboydecoder
import wave
import sys
import time
import os
from pyaudio import PyAudio, paInt16
from espnet2.bin.asr_inference import Speech2Text
import soundfile
import time

model = Speech2Text.from_pretrained(
    "espnet/pengcheng_guo_wenetspeech_asr_train_asr_raw_zh_char"
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
    text, *_ = model(speech)[0]
    return text


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
