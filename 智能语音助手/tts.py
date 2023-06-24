import websockets
import asyncio
from datetime import datetime
import re
import uuid

SSML_text = """
<speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml" version="1.0" xml:lang="en-US">
    <voice name="zh-CN-XiaoxiaoNeural">
        <prosody rate="0%" pitch="0%">{}</prosody>
    </voice>
</speak>"""


# 调整时间
def hr_cr(hr):
    corrected = (hr - 1) % 24
    return str(corrected)


# 在正确的位置添加零，即 22:1:5 -> 22:01:05
def fr(input_string):
    corr = ""
    i = 2 - len(input_string)
    while i > 0:
        corr += "0"
        i -= 1
    return corr + input_string


# 生成所有格式正确的 X-Timestamp
def getXTime():
    now = datetime.now()
    return (
        fr(str(now.year))
        + "-"
        + fr(str(now.month))
        + "-"
        + fr(str(now.day))
        + "T"
        + fr(hr_cr(int(now.hour)))
        + ":"
        + fr(str(now.minute))
        + ":"
        + fr(str(now.second))
        + "."
        + str(now.microsecond)[:3]
        + "Z"
    )


# 用于实际与 websocket 通信的异步函数
async def transferMsTTSData(SSML_text, outputPath):
    req_id = uuid.uuid4().hex.upper()
    print(req_id)
    # TOKEN来源 https://github.com/rany2/edge-tts/blob/master/src/edge_tts/constants.py
    # 查看支持声音列表 https://speech.platform.bing.com/consumer/speech/synthesize/readaloud/voices/list?trustedclienttoken=6A5AA1D4EAFF4E9FB37E23D68491D6F4
    TRUSTED_CLIENT_TOKEN = "6A5AA1D4EAFF4E9FB37E23D68491D6F4"
    WSS_URL = (
        "wss://speech.platform.bing.com/consumer/speech/synthesize/"
        + "readaloud/edge/v1?TrustedClientToken="
        + TRUSTED_CLIENT_TOKEN
    )
    endpoint2 = f"{WSS_URL}&ConnectionId={req_id}"
    async with websockets.connect(
        endpoint2,
        extra_headers={
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Origin": "chrome-extension://jdiccldimpdaibmpdkjnbmckianbfold",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.41",
        },
    ) as websocket:
        message_1 = (
            f"X-Timestamp:{getXTime()}\r\n"
            "Content-Type:application/json; charset=utf-8\r\n"
            "Path:speech.config\r\n\r\n"
            '{"context":{"synthesis":{"audio":{"metadataoptions":{'
            '"sentenceBoundaryEnabled":false,"wordBoundaryEnabled":true},'
            '"outputFormat":"audio-24khz-48kbitrate-mono-mp3"'
            "}}}}\r\n"
        )
        await websocket.send(message_1)

        message_2 = (
            f"X-RequestId:{req_id}\r\n"
            "Content-Type:application/ssml+xml\r\n"
            f"X-Timestamp:{getXTime()}Z\r\n"  # This is not a mistake, Microsoft Edge bug.
            "Path:ssml\r\n\r\n"
            f"{SSML_text}"
        )
        await websocket.send(message_2)

        # 检查关闭连接消息
        end_resp_pat = re.compile("Path:turn.end")
        audio_stream = b""
        while True:
            response = await websocket.recv()
            # print(response)
            # 确保消息没有告诉我们停止
            if re.search(end_resp_pat, str(response)) == None:
                # 检查我们的响应是文本数据还是音频字节
                if type(response) == type(bytes()):
                    # Extract binary data
                    try:
                        needle = b"Path:audio\r\n"
                        start_ind = response.find(needle) + len(needle)
                        audio_stream += response[start_ind:]
                    except:
                        pass
            else:
                break
        with open(f"{outputPath}.mp3", "wb") as audio_out:
            audio_out.write(audio_stream)


async def mainSeq(SSML_text, outputPath):
    await transferMsTTSData(SSML_text, outputPath)


class TTS:
    def __init__(self) -> None:
        pass

    def text2speech(text):
        format_text = SSML_text.format(text)
        asyncio.get_event_loop().run_until_complete(
            mainSeq(format_text, "./resources/tts")
        )


if __name__ == "__main__":
    TTS.text2speech("你好")
