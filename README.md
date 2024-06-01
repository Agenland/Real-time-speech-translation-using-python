# Real-time-speech-translation-using-python


#### 简介

一个简单的python程序.使用阿里开源的语音识别模型[paraformer](https://github.com/alibaba-damo-academy/FunASR/wiki/paraformer)进行识别.

项目主要是为了解决在linux系统下的麦克风实时语音识别.但是在各种支持python的系统上都可以使用.


#### 特征

* 离线AI模型识别.
* 识别准确率高，速度快.
* qt界面，一键复制.
* 连续识别，自动断句，无需频繁切换开关.


#### 前置需求

- 4G及以上显存的显卡
- pytorch+CUDA环境
- 麦克风

python环境配置

```bash
pip3 install -r requirements.txt
```


#### 使用

激活对应环境，然后使用以下命令

```bash
python3 RealTime.py
```


第一次运行需要下载[paraformer](https://github.com/alibaba-damo-academy/FunASR/wiki/paraformer)模型.

启动完成之后会弹出QT窗口.

点击开始录音，程序会进入捕捉状态,之后程序会自动捕捉每句话之间的间隔,当你说完一句话以后进行约1.5s的停顿，AI模型就会开始识别，然后将识别结果加入到文本框，之后会等待下一句话.

点击停止录音，程序不再捕捉麦克风声音，停止录音键不会触发识别.


#### 可能需要调整

程序是靠音量大小来识别是否正在说话.因此合适的域值可能会因为硬件的不同和声音增益设置的不同而有所区别.

因此你可能需要更改声音阈值.在python环境下调整RealTime.py搜索silence_threshold,调整其值即可.

程序会在开始录音后在终端输出当前声音信号的信息，格式为  “当前声音， 声音阈值，计数"，这可能有助于找到合适的声音阈值

#### 错误解决
python 3.11 可用， 3.12 不保证
依赖 funasr: pip install funasr

conda 环境下可能有 GLIBCXX_3.4.30' not found
需要建立软链接
cd /home/xxx/anaconda3/envs/decdiff_env/bin/../lib/
mv libstdc++.so.6 libstdc++.so.6.old
ln -s /usr/lib/x86_64-linux-gnu/libstdc++.so.6 libstdc++.so.6



