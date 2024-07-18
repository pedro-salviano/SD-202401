import random
import string
from time import sleep, time
import zmq
import cv2
import pyaudio
import threading
import numpy as np
import struct
import math
import zlib

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

AUDIO = pyaudio.PyAudio()

AUDIO_FORMAT = pyaudio.paInt16
AUDIO_CHANNELS = 1
RECORD_RATE = 16000
AUDIO_CHUNK_SIZE = 1024

runningFlag = True
name = ""
identity = ""
room_id = ""

def send_cam_video():
    global runningFlag
    global identity
    global room_id

    cap = cv2.VideoCapture(0)
    topic = (room_id + identity).encode('utf-8')

    while runningFlag:
        ret, frame = cap.read()
        if not ret:
            continue
        
        _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])

        compressed_frame = zlib.compress(buffer, level=1)
        
        VIDEO_PUB.send_multipart([topic, compressed_frame])
        sleep(0.01)
    cap.release()


def send_video():
    global runningFlag
    global identity
    global room_id

    width, height = 640, 480
    topic = (room_id+identity).encode('utf-8')
    while runningFlag:
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame = cv2.rectangle(frame, (100, 100), (width-100, height-100), (random.randrange(0,255), random.randrange(0,255), random.randrange(0,255)), -1)
        
        _, buffer = cv2.imencode('.jpg', frame)

        compressed_frame = zlib.compress(buffer, level=1)
        
        # Enviar como mensagem multipart
        VIDEO_PUB.send_multipart([topic, compressed_frame])
        sleep(0.01)

def receive_video():
    video_windows = {}
    global runningFlag
    global room_id

    while runningFlag:
        try:
            topic, compressed_frame = VIDEO_SUB.recv_multipart()
            if compressed_frame:
                sender_id = topic.decode('utf-8')[len(room_id):]

                try:
                    decompressed_frame = zlib.decompress(compressed_frame)
                except Exception as e:
                    print(f"Erro ao descomprimir dados: {e}")
                    continue
                
                try:
                    jpg_as_np = np.frombuffer(decompressed_frame, dtype=np.uint8)
                    frame = cv2.imdecode(jpg_as_np, flags=cv2.IMREAD_COLOR)
                except Exception as e:
                    print(f"Erro ao decodificar frame: {e}")
                    continue

                if sender_id not in video_windows:
                    participant = sender_id[:-SALT_SIZE]
                    windowName = f"{participant}'s video"
                    video_windows[sender_id] = windowName
                    cv2.namedWindow(windowName)
                
                cv2.imshow(video_windows[sender_id], frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                runningFlag = False
                break

        except Exception as e:
            print(f"Erro ao receber ví­deo: {e}")

    cv2.destroyAllWindows()


class MicrophoneRecorder():
    def __init__(self, sender):
        self.identity = (room_id + identity).encode('utf-8')
        self.sender = sender
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=AUDIO_FORMAT,
                                  channels=AUDIO_CHANNELS,
                                  rate=RECORD_RATE,
                                  input=True,
                                  frames_per_buffer=AUDIO_CHUNK_SIZE)

    def read(self):
        data = self.stream.read(AUDIO_CHUNK_SIZE)
        return data

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

def send_audio():
    mic = MicrophoneRecorder(AUDIO_PUB)
    while runningFlag:
        try:
            mic_data = mic.read()
            topic = mic.identity
            AUDIO_PUB.send_multipart([topic, mic_data])
        except Exception as e:
            print(f"Error sending audio: {e}")
    mic.close()


def receive_audio(micPlayBack=False):
    p = pyaudio.PyAudio()
    try:
        play_stream = p.open(format=AUDIO_FORMAT,
                             channels=AUDIO_CHANNELS,
                             rate=RECORD_RATE,
                             output=True,
                             frames_per_buffer=AUDIO_CHUNK_SIZE)
    except Exception as e:
        print(f"Error opening playback stream: {e}")
        return
    
    while runningFlag:
        try:
            topic, data = AUDIO_SUB.recv_multipart()
            sender_id = topic.decode('utf-8')[len(room_id):]
            if data and (sender_id != identity or micPlayBack):
                play_stream.write(data)
        except Exception as e:
            print(f"Error receiving audio: {e}")
            break
    
    play_stream.stop_stream()
    play_stream.close()
    p.terminate()
    
    while runningFlag:
        try:
            topic, data = AUDIO_SUB.recv_multipart()
            sender_id = topic.decode('utf-8')[len(room_id):]
            if data and (sender_id != identity or micPlayBack):
                play_stream.write(data)
        except Exception as e:
            print(f"Erro ao receber áudio: {e}")
            break
    
    play_stream.stop_stream()
    play_stream.close()
 


def send_text():
    global runningFlag
    global room_id

    while runningFlag:
        text = input()
        if text:
            if text.lower() == "quit":
                runningFlag = False
            else: 
                topic = room_id.encode('utf-8')
                message = f"{name}: {text}".encode('utf-8')
                TEXT_PUB.send_multipart([topic, message])

def receive_text():
    global runningFlag
    while runningFlag:
        topic, text = TEXT_SUB.recv_multipart()
        if text != "":
            text = text.decode('utf_8')
            print(text)

def id_generator():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(SALT_SIZE))

if __name__ == "__main__":

    isCam = input("Use device camera?[y/(N)] ").lower() == 'Y'.lower()
    serverip = input("Inform broker server ipv4 (use the command ipconfig to get it): [Default localhost] ")
    if serverip == "":
        serverip = "localhost"

    # Connect to the broker
    VIDEO_PUB.connect("tcp://" + serverip + ":5552")
    AUDIO_PUB.connect("tcp://" + serverip + ":5553")
    TEXT_PUB.connect("tcp://" + serverip + ":5554")

    VIDEO_SUB.connect("tcp://" + serverip + ":5555")
    AUDIO_SUB.connect("tcp://" + serverip + ":5556")
    TEXT_SUB.connect("tcp://" + serverip + ":5557")

    # Identify the room
    room_id = input("Enter the room ID: ")

    # Subscribe to messages in the room
    VIDEO_SUB.setsockopt_string(zmq.SUBSCRIBE, room_id)
    AUDIO_SUB.setsockopt_string(zmq.SUBSCRIBE, room_id)
    TEXT_SUB.setsockopt_string(zmq.SUBSCRIBE, room_id)

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
    print(f"You are joining the room")
    print(f"To quit call, type [quit]")
    
    topic = room_id.encode('utf-8')
    message = f"{name} joined the call".encode('utf-8')
    TEXT_PUB.send_multipart([topic, message])
    
    while True:
        if(runningFlag == False):
           print(f"You are leaving the room")
           topic = room_id.encode('utf-8')
           message = f"{name} left the call".encode('utf-8')
           TEXT_PUB.send_multipart([topic, message])
           AUDIO.terminate()
           break
