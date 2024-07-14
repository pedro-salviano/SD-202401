import random
import string
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

# Connect to the broker
VIDEO_PUB.bind("tcp://localhost:5552")
AUDIO_PUB.bind("tcp://localhost:5553")
TEXT_PUB.bind("tcp://localhost:5554")

VIDEO_SUB.connect("tcp://localhost:5555")
AUDIO_SUB.connect("tcp://localhost:5556")
TEXT_SUB.connect("tcp://localhost:5557")

# Subscribe to all messages
VIDEO_SUB.setsockopt_string(zmq.SUBSCRIBE, "")
AUDIO_SUB.setsockopt_string(zmq.SUBSCRIBE, "")
TEXT_SUB.setsockopt_string(zmq.SUBSCRIBE, "")

AUDIO = pyaudio.PyAudio()

AUDIO_FORMAT = pyaudio.paInt16
AUDIO_CHANNELS = 1
RECORD_RATE = 16000
AUDIO_CHUNK_SIZE = 3200

runningFlag = True
name = ""
identity = ""

def send_cam_video():
    global runningFlag
    global identity

    topic = identity.encode('utf-8')

    cap = cv2.VideoCapture(0)
    while runningFlag:
        ret, frame = cap.read()
        if not ret:
            continue
        _, buffer = cv2.imencode('.jpg', frame)
        VIDEO_PUB.send_multipart([topic, buffer])

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

class MicrophoneRecorder():
    global identity

    def __init__(self, sender):
        self.identity = identity.encode('utf-8')
        self.sender = sender
        self.p = AUDIO
        self.stream = self.p.open(format=AUDIO_FORMAT,
                                  channels=1,
                                  rate=RECORD_RATE,
                                  input=True,
                                  frames_per_buffer=AUDIO_CHUNK_SIZE)

    def read(self):
        data = self.stream.read(AUDIO_CHUNK_SIZE)
        topic = self.identity
        self.sender.send_multipart([topic, data])

    def close(self):
        self.stream.stop_stream()
        self.stream.close()


def send_audio():
    mic = MicrophoneRecorder(AUDIO_PUB)
    while runningFlag:
        mic.read()
    mic.close()

def receive_audio(micPlayBack = False):
    play_stream = AUDIO.open(format=AUDIO_FORMAT, channels=AUDIO_CHANNELS, rate=RECORD_RATE, output=True, frames_per_buffer=AUDIO_CHUNK_SIZE)
    while runningFlag:
        topic, data = AUDIO_SUB.recv_multipart()
        sender_id = topic.decode('utf-8')
        if (data != None) and (sender_id != identity or micPlayBack):
            try:
                play_stream.write(data)
            except Exception as e:
                print("Client Disconnected")
                break
            
    play_stream.stop_stream()
    play_stream.close()

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

    isCam = input("Use device camera?[y/(N)] ").lower() == 'Y'.lower()
    """ serverip = input("Inform broker server ipv4:[Default: localhost] ") """
    micPlayBack = input("Microphone playback?[y/(N)] ").lower() == 'Y'.lower()

    name = input("Identify yourself: ")
    identity = name+id_generator()

    if isCam:
        threading.Thread(target=send_cam_video).start()
    else:
        threading.Thread(target=send_video).start()
    
    threading.Thread(target=receive_video).start()
    threading.Thread(target=send_audio,).start()
    threading.Thread(target=receive_audio, args = (micPlayBack, ), daemon=True).start()
    threading.Thread(target=send_text, daemon=True).start()
    threading.Thread(target=receive_text).start()
    
    while True:
        if(runningFlag == False):
           TEXT_PUB.send_string(f"{name} is leaving")
           AUDIO.terminate()
           break
