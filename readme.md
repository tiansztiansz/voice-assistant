<!-- 标题 -->
<h1 align="center">智能语音助手</h1>


<!-- 图标 -->
<p align="center">
  <a href="https://github.com/tiansztiansz/tiansztiansz/blob/main/wechat_alipay.png">
    <img alt="License" src="src/捐赠.svg" />
  </a>&nbsp; &nbsp; 
  <a href="https://github.com/tiansztiansz/voice-assistant/blob/main/LICENSE">
    <img alt="License" src="src/license.svg" />
  </a>&nbsp; &nbsp; 
  <a href="https://space.bilibili.com/28606893?spm_id_from=333.1007.0.0">
    <img alt="bilibili图标" src="src/BILIBILI_LOGO.svg" />
  </a>&nbsp; &nbsp; 
  <a href="https://www.cnblogs.com/tiansz/">
    <img alt="博客园" src="src/博客园.jpg" />
  </a>&nbsp; &nbsp;
  <a href="https://www.douyin.com/user/MS4wLjABAAAAqkpp6UyrANDXFStAMWuRPp7FU4zHfyq0_OYPoC75_qQ">
    <img alt="抖音" src="src/抖音.svg" />
  </a>&nbsp; &nbsp;
  <a href="https://www.kaggle.com/tiansztianszs">
    <img alt="kaggle" src="src/kaggle.svg" />
  </a>
</p>


<!-- 项目介绍 -->
<p align="center">基于 Snowboy、Whisper、ChatYuan 和 Azure TTS 的智能语音助手</p>

<br>

<!-- 演示视频 -->
<p align="center">
  <img src="src/语音助手显示视频.gif">
</p>



<br>

<!-- 项目使用说明 -->
## 如何使用
首先确保系统环境为 Ubuntu 20.04 及以上，并安装依赖包如下：
```bash
pip install -r requirements.txt
```
接着运行主程序：
```bash
python3 app.py
```

<br>

## 目录结构

```
.
├── LICENSE              # 协议
├── _snowboydetect.so    # 依赖文件
├── app.py               # 主程序
├── chatyuan.py          # 聊天模块
├── readme.md            # 自述文件
├── requirements.txt     # 依赖包
├── resources           
│   ├── common.res       # 依赖文件
│   ├── ding.wav         # 唤醒时的启动音频
│   ├── music.mp3        # 音乐文件
│   ├── music_list.csv   # 音乐下载链接
│   ├── sst.wav          # 语音转文本的音频
│   ├── tts.mp3          # 文本转语音的音频
│   └── xiaozhixiaozhi.pmdl  # 唤醒模型
├── snowboy-detect-swig.cc   # 依赖文件
├── snowboy-detect-swig.i    # 依赖文件
├── snowboy-detect-swig.o    # 依赖文件
├── snowboydecoder.py        # 唤醒模块
├── snowboydetect.py         # 唤醒模块
├── src                      # 其他文件夹
│   ├── BILIBILI_LOGO.svg
│   ├── kaggle.svg
│   ├── license.svg
│   ├── 博客园.jpg
│   ├── 抖音.svg
│   ├── 捐赠.svg
│   └── 语音助手显示视频.gif
├── tts.py        # 文字转语音模块
└── whisper.py    # 语音转文本模块
```


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

<br>

<!-- 赞助 -->
## 赞助

如果这个项目对你有帮助，请给一个⭐️！

如果资金充裕，能否考虑请小弟喝杯[奶茶🧋](https://github.com/tiansztiansz/tiansztiansz/blob/main/wechat_alipay.png)


