import soundfile
from espnet2.bin.tts_inference import Text2Speech
text2speech = Text2Speech.from_pretrained("espnet/kan-bayashi_csmsc_tts_train_tacotron2_raw_phn_pypinyin_g2p_phone_train.loss.best")

text = "春江潮水连海平，海上明月共潮生"
speech = text2speech(text)["wav"]
soundfile.write("out.wav", speech.numpy(), text2speech.fs, "PCM_16")