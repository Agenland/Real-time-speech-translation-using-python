# import speech_recognition as sr
# import keyboard

# recognizer = sr.Recognizer()
# microphone = sr.Microphone()

# with microphone as source:
#     print("请开始说话...")
#     while True:
#         try:
#             audio = recognizer.listen(source)
#             text = recognizer.recognize_(audio, language="zh-CN")
#             print("识别结果:", text)
#         except sr.UnknownValueError:
#             print("无法识别语音")
#         except sr.RequestError as e:
#             print("请求错误：", str(e))
#         if keyboard.is_pressed("q"):
#             print("退出程序")
#             break


