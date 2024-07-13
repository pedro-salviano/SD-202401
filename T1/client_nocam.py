import base64
import random
from time import sleep
import zmq
import cv2
import pyaudio
import threading
import numpy as np

context = zmq.Context()

# Publisher sockets for video, audio, and text
video_pub = context.socket(zmq.PUB)
audio_pub = context.socket(zmq.PUB)
text_pub = context.socket(zmq.PUB)

# Subscriber sockets for video, audio, and text
video_sub = context.socket(zmq.SUB)
audio_sub = context.socket(zmq.SUB)
text_sub = context.socket(zmq.SUB)

""" # Connect to the broker
video_pub.connect("tcp://192.168.0.149:5555")
audio_pub.connect("tcp://192.168.0.149:5556")
text_pub.connect("tcp://192.168.0.149:5557")

video_sub.connect("tcp://192.168.0.149:5555")
audio_sub.connect("tcp://192.168.0.149:5556")
text_sub.connect("tcp://192.168.0.149:5557") """

# Connect to the broker
video_pub.bind("tcp://localhost:5552")
audio_pub.bind("tcp://localhost:5553")
text_pub.bind("tcp://localhost:5554")

video_sub.connect("tcp://localhost:5555")
audio_sub.connect("tcp://localhost:5556")
text_sub.connect("tcp://localhost:5557")

# Subscribe to all messages
video_sub.setsockopt_string(zmq.SUBSCRIBE, "")
audio_sub.setsockopt(zmq.SUBSCRIBE, b'')
text_sub.setsockopt(zmq.SUBSCRIBE, b'')

def send_video():
    width, height = 640, 480
    while True:
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame = cv2.rectangle(frame, (100, 100), (width-100, height-100), (random.randrange(0,255), random.randrange(0,255), random.randrange(0,255)), -1)
        _, buffer = cv2.imencode('.jpg', frame)
        print("sending video frame\n")
        video_pub.send(buffer)
        sleep(0.1)
        

def receive_video():
    while True:
        frame = video_sub.recv()
        if frame:
            print("Receiveing video")
            np_frame = np.frombuffer(frame, dtype=np.uint8)
            img = cv2.imdecode(np_frame, 1)
            cv2.imshow('Video', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

"""def send_audio():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
    while True:
        print("Sending audio")
        data = stream.read(1024)
        audio_pub.send(data)

def receive_audio():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True)
    while True:
        print("Receiveing audio")
        data = audio_sub.recv()
        stream.write(data) """

""" def send_text():
    while True:
        text = input()
        text_pub.send_string(text)
        print("enviado: ", text)

def receive_text():
    while True:
        text = text_sub.recv_string()
        print("Received: ", text) """

if __name__ == "__main__":
    threading.Thread(target=send_video).start()
    threading.Thread(target=receive_video).start()
    """threading.Thread(target=send_audio).start()
    threading.Thread(target=receive_audio).start() """
    """ threading.Thread(target=send_text).start()
    threading.Thread(target=receive_text).start() """
