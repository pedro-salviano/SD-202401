import base64
import random
import string
import sys
from time import sleep
import zmq
import cv2
import pyaudio
import threading
import numpy as np

SALT_SIZE = 16
CONTEXT = zmq.Context()

# Publisher sockets for video, audio, and text
VIDEO_PUB = CONTEXT.socket(zmq.PUB)
AUDIO_PUB = CONTEXT.socket(zmq.PUB)
TEXT_PUB = CONTEXT.socket(zmq.PUB)

# Subscriber sockets for video, audio, and text
VIDEO_SUB = CONTEXT.socket(zmq.SUB)
AUDIO_SUB = CONTEXT.socket(zmq.SUB)
TEXT_SUB = CONTEXT.socket(zmq.SUB)

""" # Connect to the broker
VIDEO_PUB.connect("tcp://192.168.0.149:5555")
AUDIO_PUB.connect("tcp://192.168.0.149:5556")
TEXT_PUB.connect("tcp://192.168.0.149:5557")

VIDEO_SUB.connect("tcp://192.168.0.149:5555")
AUDIO_SUB.connect("tcp://192.168.0.149:5556")
TEXT_SUB.connect("tcp://192.168.0.149:5557") """

# Connect to the broker
VIDEO_PUB.bind("tcp://localhost:5552")
AUDIO_PUB.bind("tcp://localhost:5553")
TEXT_PUB.bind("tcp://localhost:5554")

VIDEO_SUB.connect("tcp://localhost:5555")
AUDIO_SUB.connect("tcp://localhost:5556")
TEXT_SUB.connect("tcp://localhost:5557")

# Subscribe to all messages
VIDEO_SUB.setsockopt_string(zmq.SUBSCRIBE, "")
AUDIO_SUB.setsockopt(zmq.SUBSCRIBE, b'')
TEXT_SUB.setsockopt_string(zmq.SUBSCRIBE, "")

runningFlag = True
name = ""
identity = ""

""" def send_video():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        _, buffer = cv2.imencode('.jpg', frame)
        video_pub.send(buffer.tobytes()) """

def send_video():
    global runningFlag
    global identity

    width, height = 640, 480
    topic = identity.encode('utf-8')
    while runningFlag:
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame = cv2.rectangle(frame, (100, 100), (width-100, height-100), (random.randrange(0,255), random.randrange(0,255), random.randrange(0,255)), -1)
        _, buffer = cv2.imencode('.jpg', frame)

        VIDEO_PUB.send_multipart([topic, buffer])
        sleep(0.1)
        

def receive_video():
    video_windows = {} 
    global runningFlag


    while runningFlag:
        topic, frame = VIDEO_SUB.recv_multipart()
        if frame:
            sender_id = topic.decode('utf-8')
            np_frame = np.frombuffer(frame, dtype=np.uint8)
            img = cv2.imdecode(np_frame, 1)

            if sender_id not in video_windows:
                participant = sender_id[:-SALT_SIZE]
                windowName = f"{participant}`s video"
                video_windows[sender_id] = windowName
                cv2.namedWindow(windowName)
            cv2.imshow(video_windows[sender_id], img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            runningFlag = False
            break
    cv2.destroyAllWindows()

"""def send_audio():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
    while runningFlag:
        print("Sending audio")
        data = stream.read(1024)
        AUDIO_PUB.send(data)

def receive_audio():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True)
    while runningFlag:
        print("Receiveing audio")
        data = AUDIO_SUB.recv()
        stream.write(data) """

def send_text():
    global runningFlag
    while runningFlag:
        text = input()
        if text:
            TEXT_PUB.send((name + ":" + text).encode('utf-8'))
            print("enviado: ", text)

def receive_text():
    global runningFlag
    while runningFlag:
        text = TEXT_SUB.recv()
        if text != "":
            text = text.decode('utf_8')
            print(text)

def id_generator():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(SALT_SIZE))

if __name__ == "__main__":
    name = input("Identify yourself: ")
    identity = name+id_generator()
    threading.Thread(target=send_video).start()
    threading.Thread(target=receive_video).start()
    """threading.Thread(target=send_audio).start()
    threading.Thread(target=receive_audio).start() """
    threading.Thread(target=send_text, daemon=True).start()
    threading.Thread(target=receive_text).start()
    
    while True:
        if(runningFlag == False):
           TEXT_PUB.send_string(f"{name} is leaving")
           
           sys.exit(0)
           break
