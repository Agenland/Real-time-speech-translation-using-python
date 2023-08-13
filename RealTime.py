import os
import time
import pyaudio, audioop
import wave
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
import clipboard, pyautogui

from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

# 配置参数
FORMAT = pyaudio.paInt16    # 采样格式为16位整数
CHANNELS = 1                # 单声道
RATE = 44100                # 采样率
CHUNK = 1024                # 每次读取的音频块大小
OUTPUT_FILENAME = "audio.wav"  # 输出文件名



# 初始化paraformer识别模型

inference_pipeline = pipeline(
    task=Tasks.auto_speech_recognition,
    model='damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch')


# 初始化PyAudio
p = pyaudio.PyAudio()


class RecordApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.is_recording = False
        self.frames = []

        self.steam = None

        self.silence_counter = 0
        self.silence_threshold = 10000  # 静音阈值，根据实际情况调整
        self.silence_duration = 1.5  # 静音连续时间，单位：秒

        self.init_ui()

    def init_ui(self):
        self.setGeometry(100, 100, 400, 400)
        self.setWindowTitle("语音识别录音")

        self.record_button = QPushButton("开始录音", self)
        self.record_button.setGeometry(150, 30, 100, 40)
        self.record_button.clicked.connect(self.toggle_recording)

        self.clear_button = QPushButton("清空文本", self)
        self.clear_button.setGeometry(50, 30, 100, 40)
        self.clear_button.clicked.connect(self.clear_text)

        self.copy_button = QPushButton("复制文本", self)
        self.copy_button.setGeometry(250, 30, 100, 40)
        self.copy_button.clicked.connect(self.copy_text)

        self.result_text = QTextEdit(self)
        self.result_text.setGeometry(50, 100, 300, 250)
        self.result_text.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.record_button)
        layout.addWidget(self.clear_button)
        layout.addWidget(self.copy_button)
        layout.addWidget(self.result_text)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


    def toggle_recording(self):
        if not self.is_recording:
            print("开始录音...")
            self.is_recording = True
            self.frames = []
            self.record_button.setText("停止录音")
            self.recording()
        else:
            print("录音结束.")
            self.is_recording = False
            self.record_button.setText("开始录音")
            self._end_stream()


    def detect_silence(self, data):
        rms = audioop.rms(data, 2)  # 计算音频块的RMS值
        if rms < self.silence_threshold:
            self.silence_counter += CHUNK / RATE
        else:
            self.silence_counter = 0

        print(rms,self.silence_threshold,self.silence_counter)

        if self.silence_counter >= self.silence_duration:
            self.silence_counter = 0
            self._recognize()
            

            while self.is_recording:
                data = self.stream.read(CHUNK)
                rms = audioop.rms(data, 2)
                QApplication.processEvents()
                print(rms,self.silence_threshold,self.silence_counter)
                if rms >= self.silence_threshold:
                    break
            
            # 重置stream
            self._end_stream()
            self._start_stream()
                    
    
    def _start_stream(self):
        # 重启音频流
        self.stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)
        self.stream.start_stream()

    def _end_stream(self):
        self.stream.stop_stream()
        self.stream.close()

    def recording(self):
        
        self._start_stream()
        # 记录音频流
        while self.is_recording:
            data = self.stream.read(CHUNK)
            self.frames.append(data)
            self.detect_silence(data)  # 检测静音
            QApplication.processEvents()
            time.sleep(CHUNK / RATE)


    def _recognize(self):

        with wave.open(OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(self.frames))

        self.frames = []

        # 执行语音识别
        rec_result = inference_pipeline(audio_in=OUTPUT_FILENAME)

        # 在文本框中显示识别结果
        try:
            recognized_text = rec_result['text'] + '.\n'
            self.result_text.insertPlainText(recognized_text)

            # 模拟键盘输入，将识别结果输入到活动应用程序
            pyautogui.write(recognized_text)
        except:
            print("no result.")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F2:
            self.toggle_recording()
    
    def clear_text(self):
        self.result_text.clear()

    def copy_text(self):
        clipboard.copy(self.result_text.toPlainText())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RecordApp()
    window.show()
    sys.exit(app.exec_())