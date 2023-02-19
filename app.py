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
import paddle
from paddlenlp.transformers import T5Tokenizer, T5ForConditionalGeneration
from paddlenlp.transformers import AutoTokenizer, T5ForConditionalGeneration


tokenizer = AutoTokenizer.from_pretrained("ClueAI/ChatYuan-large-v1", from_hf_hub=False)
model = T5ForConditionalGeneration.from_pretrained(
    "ClueAI/ChatYuan-large-v1", from_hf_hub=False
)


model.eval()


def preprocess(text):
    text = text.replace("\n", "\\n").replace("\t", "\\t")
    return text


def postprocess(text):
    return text.replace("\\n", "\n").replace("\\t", "\t")


def answer(text, sample=True, top_p=1, temperature=0.7):
    """sample：是否抽样。生成任务，可以设置为True;
    top_p：0-1之间，生成的内容越多样"""
    text = preprocess(text)
    encoding = tokenizer(
        text=[text], truncation=True, padding=True, max_length=768, return_tensors="pd"
    )
    if not sample:
        out = model.generate(
            **encoding,
            return_dict_in_generate=True,
            output_scores=False,
            max_length=512,
            max_new_tokens=512,
            num_beams=1,
            length_penalty=0.4,
        )
    else:
        out = model.generate(
            **encoding,
            return_dict_in_generate=True,
            output_scores=False,
            max_length=512,
            max_new_tokens=512,
            do_sample=True,
            top_p=top_p,
            temperature=temperature,
            no_repeat_ngram_size=3,
        )

    out_text = tokenizer.batch_decode(out[0], skip_special_tokens=True)

    return postprocess(out_text[0])


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
    while time.time() < t + 5:  # 秒
        string_audio_data = stream.read(num_samples)
        my_buf.append(string_audio_data)
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
    print("正在保存音频...\n")
    soundfile.write(firename, speech.numpy(), t2s_model.fs, "PCM_16")
    print("正在播放音频...\n")
    play(firename)


def music(text):
    if text == "播放音乐":
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
        result_text = text2text(text)
        print("机器人回复：{}\n".format(result_text))
        firename = "./resources/none.wav"
        text2speech(result_text=result_text, firename=firename)


def text2text(input_text):
    input_text = "用户：" + input_text + "\n小元："
    print(f"示例".center(50, "="))
    output_text = answer(input_text)
    return output_text


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
        print("语音识别结果：{}\n".format(text))
        music(text)
