import os
import time
import pyaudio, audioop
import wave
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit
from PyQt5.QtCore import Qt

from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

# 配置参数
FORMAT = pyaudio.paInt16    # 采样格式为16位整数
CHANNELS = 1                # 单声道
RATE = 44100                # 采样率
CHUNK = 1024                # 每次读取的音频块大小
RECORD_SECONDS = 5          # 录制时长（秒）
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
        self.silence_threshold = 5000  # 静音阈值，根据实际情况调整
        self.silence_duration = 1.5  # 静音连续时间，单位：秒

        self.init_ui()

    def init_ui(self):
        self.setGeometry(100, 100, 400, 200)
        self.setWindowTitle("语音识别录音")

        self.record_button = QPushButton("开始录音", self)
        self.record_button.setGeometry(150, 30, 100, 40)
        self.record_button.clicked.connect(self.toggle_recording)

        self.result_text = QTextEdit(self)
        self.result_text.setGeometry(50, 100, 300, 80)


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
            self._recognize()

    def detect_silence(self, data):
        rms = audioop.rms(data, 2)  # 计算音频块的RMS值
        if rms < self.silence_threshold:
            self.silence_counter += CHUNK / RATE
        else:
            self.silence_counter = 0

        # print(rms,self.silence_threshold,self.silence_counter)

        if self.silence_counter >= self.silence_duration:
            self.silence_counter = 0
            self._recognize()
            
            while True:
                data = self.stream.read(CHUNK)
                rms = audioop.rms(data, 2)
                QApplication.processEvents()
                if rms >= self.silence_threshold:
                    self._end_stream()
                    self.recording()  # 重新开始录音
                    break


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

        # 执行语音识别
        rec_result = inference_pipeline(audio_in=OUTPUT_FILENAME)

        # 在文本框中显示识别结果
        self.result_text.setPlainText(rec_result['text'])


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F2:
            self.toggle_recording()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RecordApp()
    window.show()
    sys.exit(app.exec_())