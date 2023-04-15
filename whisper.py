from faster_whisper import WhisperModel

model_size = "medium"
model = WhisperModel(model_size, device="cpu", compute_type="int8")


class ASR:
    def __init__(self) -> None:
        pass

    def speech2text(audio_path):
        segments, info = model.transcribe(audio_path, beam_size=5)
        for segment in segments:
            return segment.text


if __name__ == "__main__":
    audio_path = "./src/test.wav"
    text = ASR.speech2text(audio_path)
    print("【语音识别结果】  %s" % (text))
