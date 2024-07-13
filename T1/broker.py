import zmq
from zmq.devices import monitored_queue

from zhelpers import zpipe


def broker():
    context = zmq.Context.instance()
    
    pipe = zpipe(context)

    # Sockets for video, audio, and text
    sub_video_socket = context.socket(zmq.XSUB)
    """ sub_audio_socket = context.socket(zmq.XSUB)
    sub_text_socket = context.socket(zmq.XSUB) """

    # Sockets for video, audio, and text
    pub_video_socket = context.socket(zmq.XPUB)
    """ pub_audio_socket = context.socket(zmq.XPUB)
    pub_text_socket = context.socket(zmq.XPUB) """

    # connects the sockets to ports
    sub_video_socket.connect("tcp://localhost:5552")
    """ sub_audio_socket.connect("tcp://localhost:5553")
    sub_text_socket.connect("tcp://localhost:5554") """
    
    # Bind the sockets to ports
    pub_video_socket.bind("tcp://*:5555")
    """ pub_audio_socket.bind("tcp://*:5556")
    pub_text_socket.bind("tcp://*:5557") """
    
    try:
        zmq.proxy(sub_video_socket, pub_video_socket)
        """ monitored_queue(sub_audio_socket, pub_audio_socket, pipe[0], b'pub', b'sub')
        monitored_queue(sub_text_socket, pub_text_socket, pipe[0], b'pub', b'sub') """
    except KeyboardInterrupt:
        print ("Interrupted")

    del sub_video_socket, pub_video_socket
    """ del sub_audio_socket, pub_audio_socket
    del sub_text_socket, pub_text_socket """
    del pipe
    context.term()

if __name__ == "__main__":
    broker()
