from faster_whisper import WhisperModel

model_size = "medium"
model = WhisperModel(model_size, device="cuda", compute_type="int8")


class ASR:
    def __init__(self) -> None:
        pass

    def speech2text(audio_path):
        segments, info = model.transcribe(audio_path, beam_size=5)
        return segments


if __name__ == "__main__":
    audio_path = "./src/test.wav"
    segments = ASR.speech2text(audio_path)
    for segment in segments:
        print("【语音识别结果】  %s" % (segment.text))
