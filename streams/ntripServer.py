# -*- encoding=utf-8 -*-
import base64
import socket
from threading import Thread
import time
from queue import Queue


class NtripServer:

    def __init__(self, ip, port, mountPoint, pwd):
        self.ip = ip
        self.port = port
        self.mountPoint = mountPoint
        self.pwd = pwd
        self.socket = None
        self.running = False
        self.rtcmQueue = Queue(maxsize=100)

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))
        self.thread = Thread(target=self.work, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.socket is not None:
            self.socket.close()

    def work(self):
        self.running = True
        self.socket.send(self.init_msg())
        data = self.socket.recv(1024)
        if b"ICY 200 OK" in data:
            while self.running:
                rtcm = self.rtcmQueue.get()
                if rtcm is not None:
                    self.socket.send(rtcm)
                else:
                    time.sleep(0.05)
            else:
                self.running = False

    def init_msg(self):
        send_msg = "SOURCE %s /%s\r\n" \
                   "Source-Agent: NTRIP NtripServer/1.0\r\n" \
                   "\r\n" % (self.pwd, self.mountPoint)
        return send_msg.encode('utf-8')

    def write(self, data):
        if self.running:
            self.rtcmQueue.put(data)


if __name__ == '__main__':
    ntripServer = NtripServer("ntrips.feymani.cn", 2102, "Obs_x", 123456)
    ntripServer.start()
    while 1:
        ntripServer.write_rtcm("hello world\r\n".encode("utf-8"))
        time.sleep(0.5)
        pass
    ntripServer.stop()
