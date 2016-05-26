import socket
import cv2
import numpy
import threading

class CameraClient():
    def __init__(self, ip='localhost', port=5000, debug=False):
        self.receiver_thread = ReceiverThread(ip, port, debug)
        self.receiver_thread.start()

    def release(self):
        self.receiver_thread.stop()

    def read(self):
        img = self.receiver_thread.get_latest_img()
        grabbed = False

        if img is not None:
            grabbed = True

        return (grabbed, img)

class ReceiverThread(threading.Thread):
    def __init__(self, ip='localhost', port=5000, debug=False):
        super(ReceiverThread, self).__init__()

        self.daemon = True

        self.ip = ip
        self.port = port

        self.stop_flag = False

        self.debug = debug

        self.dbg("Connecting to {} : {}...".format(ip, port))
        self.sock = socket.socket()
        self.sock.connect((self.ip, self.port))
        self.dbg("Connected")

        self.latest_img = None

        self.img_lock = threading.Lock()

    def stop(self):
        self.stop_flag = True

    def set_latest_img(self, img):
        with self.img_lock:
            self.latest_img = img

    def get_latest_img(self):
        img = None
        with self.img_lock:
            if self.latest_img is not None:
                img = self.latest_img.copy()

        return img

    def run(self):
        while not self.stop_flag:
            length = self.recvall(16)
            stringData = self.recvall(int(length))
            data = numpy.fromstring(stringData, dtype='uint8')
            img=cv2.imdecode(data,1)

            self.set_latest_img(img)

        self.dbg("Closing connection")
        s.close()

    def recvall(self, count):
        buf = b''
        while count:
            newbuf = self.sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf

    def dbg(self, msg):
        if self.debug:
            print msg

if __name__ == "__main__":
    camera = CameraClient(debug=True)

    while True:
        (grabbed, frame) = camera.read()

        if not grabbed:
            continue

        cv2.imshow("Frame", frame)
        
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
