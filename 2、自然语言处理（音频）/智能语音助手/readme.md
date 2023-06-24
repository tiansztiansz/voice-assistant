<!-- 标题 -->
<h1 align="center">智能语音助手</h1>

<!-- 图标 -->
<p align="center">
  <a href="https://space.bilibili.com/28606893">
    bilibili
  </a>&nbsp; &nbsp; 
  <a href="https://github.com/tiansztiansz">
    github
  </a>&nbsp; &nbsp;
  <a href="https://huggingface.co/tiansz">
    huggingface
  </a>
</p>

<!-- 项目介绍 -->
<p align="center">基于 Snowboy、Whisper、ChatYuan 和 Azure TTS 的智能语音助手</p>



<br>

<!-- 项目使用说明 -->
## 如何使用
首先确保系统环境为 Ubuntu 20.04 及以上！

打开终端并克隆本仓库：
```bash
git clone https://github.com/tiansztiansz/voice-assistant.git
```
进入当前项目目录，然后安装依赖包：
```bash
pip install -r requirements.txt
```
接着运行主程序：
```bash
python3 app.py
```

当你看到程序显示“等待唤醒”字样时，则表明你已成功运行了程序！

接着尝试唤醒它吧，请说“小智小智”。当听到 ding 的语音提示时，请尝试说“广州在哪里”来向它提问。

或者当你想听歌的时候，请尝试说“播放音乐”

<br>


## 智能音箱实现
可在淘宝购买【带麦克风】的蓝牙音箱，连接电脑后即可实现智能音箱的效果。



<br>

<!-- 待办事项 -->
## 待办事项
- [ ]  修改唤醒时的语音
- [ ]  语音转文字的提示
- [ ]  文字转文字的提示
- [ ]  文字转语音的提示


<br>


<!-- 参考资料 -->
## 参考资料
[训练唤醒模型](https://snowboy.hahack.com/)

[唤醒后录制音频](https://www.passerma.com/article/54/#2.%E6%A0%91%E8%8E%93%E6%B4%BE%E5%BD%95%E5%88%B6%E5%A3%B0%E9%9F%B3%E4%B8%8A%E4%BC%A0%E7%99%BE%E5%BA%A6)

[如何使用snowboy](https://www.bilibili.com/video/BV1pr4y1U7cE/?spm_id_from=333.1007.top_right_bar_window_default_collection.content.click&vd_source=06eafedcfca50f6eabb7b3d6b61ecfe3)

[音乐如何下载](https://link.hhtjim.com/)


[chatyuan](https://github.com/clue-ai/ChatYuan)

[killed错误](https://www.cnblogs.com/tiansz/p/17134831.html)

[kaggle-AI](https://github.com/tiansztiansz/kaggle-AI)


