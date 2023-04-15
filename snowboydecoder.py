#!/usr/bin/env python

import collections
import pyaudio
import snowboydetect
import time
import wave
import os
import logging
from ctypes import *
from contextlib import contextmanager

logging.basicConfig()
logger = logging.getLogger("snowboy")
logger.setLevel(logging.INFO)
TOP_DIR = os.path.dirname(os.path.abspath(__file__))

RESOURCE_FILE = os.path.join(TOP_DIR, "resources/common.res")
DETECT_DING = os.path.join(TOP_DIR, "resources/ding.wav")
DETECT_DONG = os.path.join(TOP_DIR, "resources/dong.wav")


def py_error_handler(filename, line, function, err, fmt):
    pass


ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)


@contextmanager
def no_alsa_error():
    try:
        asound = cdll.LoadLibrary("libasound.so")
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    except:
        yield
        pass


class RingBuffer(object):
    """用于保存来自 PortAudio 的音频的环形缓冲区"""

    def __init__(self, size=4096):
        self._buf = collections.deque(maxlen=size)

    def extend(self, data):
        """将数据添加到缓冲区的末尾"""
        self._buf.extend(data)

    def get(self):
        """从缓冲区的开头检索数据并清除它"""
        tmp = bytes(bytearray(self._buf))
        self._buf.clear()
        return tmp


def play_audio_file(fname=DETECT_DING):
    """关键词检测到时，播放该声音文件

    :param str fname: wav文件路径
    :return: None
    """
    ding_wav = wave.open(fname, "rb")
    ding_data = ding_wav.readframes(ding_wav.getnframes())
    with no_alsa_error():
        audio = pyaudio.PyAudio()
    stream_out = audio.open(
        format=audio.get_format_from_width(ding_wav.getsampwidth()),
        channels=ding_wav.getnchannels(),
        rate=ding_wav.getframerate(),
        input=False,
        output=True,
    )
    stream_out.start_stream()
    stream_out.write(ding_data)
    time.sleep(0.2)
    stream_out.stop_stream()
    stream_out.close()
    audio.terminate()


class HotwordDetector(object):
    """Snowboy解码器检测是否为`decoder_model`指定的关键字存在于麦克风输入流中。

    :param decoder_model: 解码器模型文件路径，字符串或字符串列表
    :param resource: 资源文件路径。
    :param sensitivity: 解码器灵敏度，浮点数列表中的一个浮点数。
                        值越大解码器越敏感。 如果提供了一个空列表，则
                        将使用模型中的默认灵敏度。
    :param audio_gain: 将输入量乘以该系数。
    :param apply_frontend: 如果为真，则应用前端处理算法。
    """

    def __init__(
        self,
        decoder_model,
        resource=RESOURCE_FILE,
        sensitivity=[],
        audio_gain=1,
        apply_frontend=False,
    ):
        tm = type(decoder_model)
        ts = type(sensitivity)
        if tm is not list:
            decoder_model = [decoder_model]
        if ts is not list:
            sensitivity = [sensitivity]
        model_str = ",".join(decoder_model)

        self.detector = snowboydetect.SnowboyDetect(
            resource_filename=resource.encode(), model_str=model_str.encode()
        )
        self.detector.SetAudioGain(audio_gain)
        self.detector.ApplyFrontend(apply_frontend)
        self.num_hotwords = self.detector.NumHotwords()

        if len(decoder_model) > 1 and len(sensitivity) == 1:
            sensitivity = sensitivity * self.num_hotwords
        if len(sensitivity) != 0:
            assert self.num_hotwords == len(sensitivity), (
                "number of hotwords in decoder_model (%d) and sensitivity "
                "(%d) does not match" % (self.num_hotwords, len(sensitivity))
            )
        sensitivity_str = ",".join([str(t) for t in sensitivity])
        if len(sensitivity) != 0:
            self.detector.SetSensitivity(sensitivity_str.encode())

        self.ring_buffer = RingBuffer(
            self.detector.NumChannels() * self.detector.SampleRate() * 5
        )

    def start(
        self,
        detected_callback=play_audio_file,
        interrupt_check=lambda: False,
        sleep_time=0.03,
        audio_recorder_callback=None,
        silent_count_threshold=15,
        recording_timeout=100,
    ):
        """
         启动语音检测器。 对于每个 `sleep_time` 秒，它检查
         用于触发关键字的音频缓冲区。 如果检测到，则调用
         `detected_callback`中对应的函数，可以是单个
         函数（单个模型）或回调函数列表（多个楷模）。
         每个循环它还会调用“interrupt_check”——如果它返回
         True，然后跳出循环并返回。

        :param detected_callback: 一个函数或函数列表。 的数量
                                   项目必须匹配模型的数量
                                   `解码器模型`。
        :param interrupt_check: 如果主循环返回 True 的函数
                                 需要停下来。
        :param float sleep_time: 每个循环等待的秒数。
        :param audio_recorder_callback: 如果指定，这将在之后调用
                                         已经说出一个关键字，并且在
                                         紧跟在关键字之后的短语
                                         被记录下来。 该功能将是
                                         传递了文件的名称
                                         短语被记录下来。
        :param silent_count_threshold: 指示必须听到多长时间的静音
                                        标记一个短语的结尾
                                        被记录。
        :param recording_timeout: 限制录音的最大长度。
        :return: None
        """
        self._running = True

        def audio_callback(in_data, frame_count, time_info, status):
            self.ring_buffer.extend(in_data)
            play_data = chr(0) * len(in_data)
            return play_data, pyaudio.paContinue

        with no_alsa_error():
            self.audio = pyaudio.PyAudio()
        self.stream_in = self.audio.open(
            input=True,
            output=False,
            format=self.audio.get_format_from_width(self.detector.BitsPerSample() / 8),
            channels=self.detector.NumChannels(),
            rate=self.detector.SampleRate(),
            frames_per_buffer=2048,
            stream_callback=audio_callback,
        )

        if interrupt_check():
            logger.debug("detect voice return")
            return

        tc = type(detected_callback)
        if tc is not list:
            detected_callback = [detected_callback]
        if len(detected_callback) == 1 and self.num_hotwords > 1:
            detected_callback *= self.num_hotwords

        assert self.num_hotwords == len(detected_callback), (
            "Error: hotwords in your models (%d) do not match the number of "
            "callbacks (%d)" % (self.num_hotwords, len(detected_callback))
        )

        logger.debug("detecting...")

        state = "PASSIVE"
        while self._running is True:
            if interrupt_check():
                logger.debug("detect voice break")
                break
            data = self.ring_buffer.get()
            if len(data) == 0:
                time.sleep(sleep_time)
                continue

            status = self.detector.RunDetection(data)
            if status == -1:
                logger.warning("Error initializing streams or reading audio data")

            # 用于处理关键字后短语记录的小型状态机
            if state == "PASSIVE":
                if status > 0:  # key word found
                    self.recordedData = []
                    self.recordedData.append(data)
                    silentCount = 0
                    recordingCount = 0
                    message = "Keyword " + str(status) + " detected at time: "
                    message += time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime(time.time())
                    )
                    logger.info(message)
                    callback = detected_callback[status - 1]
                    if callback is not None:
                        callback()

                    if audio_recorder_callback is not None:
                        state = "ACTIVE"
                    continue

            elif state == "ACTIVE":
                stopRecording = False
                if recordingCount > recording_timeout:
                    stopRecording = True
                elif status == -2:  # silence found
                    if silentCount > silent_count_threshold:
                        stopRecording = True
                    else:
                        silentCount = silentCount + 1
                elif status == 0:  # voice found
                    silentCount = 0

                if stopRecording == True:
                    fname = self.saveMessage()
                    audio_recorder_callback(fname)
                    state = "PASSIVE"
                    continue

                recordingCount = recordingCount + 1
                self.recordedData.append(data)

        logger.debug("finished.")

    def saveMessage(self):
        """
        将存储在 self.recordedData 中的消息保存到带时间戳的文件中。
        """
        filename = "output" + str(int(time.time())) + ".wav"
        data = b"".join(self.recordedData)

        # 使用 wave 保存数据
        wf = wave.open(filename, "wb")
        wf.setnchannels(1)
        wf.setsampwidth(
            self.audio.get_sample_size(
                self.audio.get_format_from_width(self.detector.BitsPerSample() / 8)
            )
        )
        wf.setframerate(self.detector.SampleRate())
        wf.writeframes(data)
        wf.close()
        logger.debug("finished saving: " + filename)
        return filename

    def terminate(self):
        """
        终止音频流。 用户可以再次调用start()进行检测。
        return: None
        """
        self.stream_in.stop_stream()
        self.stream_in.close()
        self.audio.terminate()
        self._running = False
