import socket
import cv2
import numpy
import signal
import sys
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--port", required=False, type=int, default=5000, help="Port where the server will listen default is 5000")

args = vars(ap.parse_args())

TCP_IP = ''
TCP_PORT = args.get("port")

print("Starting camera...")
capture = cv2.VideoCapture(0)
print("Camera started")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(True)
print("Listening on port {}".format(TCP_PORT))

def handle_conn(conn, capture):
    while True:
        ret, frame = capture.read()

        encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
        result, imgencode = cv2.imencode('.jpg', frame, encode_param)
        data = numpy.array(imgencode)
        stringData = data.tostring()

        conn.send( str(len(stringData)).ljust(16));
        conn.send( stringData );

def signal_handler(signal, frame):
    print("Closing socket...")
    s.close()
    print("Socket closed")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

while True:
    print("Waiting for connection")
    conn, addr = s.accept()
    print("Connected from {} : {}".format(addr[0], addr[1]))

    try:
        handle_conn(conn, capture)
    except:
        pass

    print("Disconnected")




