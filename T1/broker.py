import sys
import threading
import zmq


CONTEXT = zmq.Context.instance()

# Sockets for video, audio, and text
SUB_VIDEO_SOCKET = CONTEXT.socket(zmq.XSUB)
SUB_AUDIO_SOCKET = CONTEXT.socket(zmq.XSUB)
SUB_TEXT_SOCKET = CONTEXT.socket(zmq.XSUB)

# Sockets for video, audio, and text
PUB_VIDEO_SOCKET = CONTEXT.socket(zmq.XPUB)
PUB_AUDIO_SOCKET = CONTEXT.socket(zmq.XPUB)
PUB_TEXT_SOCKET = CONTEXT.socket(zmq.XPUB)

# connects the sockets to ports
SUB_VIDEO_SOCKET.bind("tcp://*:5552")
SUB_AUDIO_SOCKET.bind("tcp://*:5553")
SUB_TEXT_SOCKET.bind("tcp://*:5554")

# Bind the sockets to ports
PUB_VIDEO_SOCKET.bind("tcp://*:5555")
PUB_AUDIO_SOCKET.bind("tcp://*:5556")
PUB_TEXT_SOCKET.bind("tcp://*:5557")

runningFlag = False

def video_proxy():
    zmq.proxy(SUB_VIDEO_SOCKET, PUB_VIDEO_SOCKET)

def audio_proxy():
    zmq.proxy(SUB_AUDIO_SOCKET, PUB_AUDIO_SOCKET)

def text_proxy():
    zmq.proxy(SUB_TEXT_SOCKET, PUB_TEXT_SOCKET)

def broker():
    runningFlag = True
    
    try:
        video_proxy_thread = threading.Thread(target=video_proxy, daemon=True)
        audio_proxy_thread = threading.Thread(target=audio_proxy, daemon=True)
        text_proxy_thread = threading.Thread(target=text_proxy, daemon=True)

        video_proxy_thread.start()
        audio_proxy_thread.start()
        text_proxy_thread.start()

        print(f"Broker is working...")

        while runningFlag:
            if runningFlag == True & 0xFF == ord('q'):
                print("Stopping")
                CONTEXT.term()
                break
                
    except KeyboardInterrupt:
        sys.exit(-1)
    finally:
        video_proxy_thread.join()
        audio_proxy_thread.join()
        text_proxy_thread.join()

if __name__ == "__main__":
    broker()