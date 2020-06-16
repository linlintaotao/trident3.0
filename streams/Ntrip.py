# coding= utf-8

import datetime
import socket
from base64 import b64encode
from queue import Queue
from threading import Thread
from streams.publish import Publisher
from time import sleep
import datetime
import os


class NtripClient(Publisher):

    def __init__(self, ip='ntrips.feymani.cn', port=2102, user='feyman-user', password="123456", mountPoint='Obs',
                 latitude=40, longitude=116, altitude=54.6):
        Publisher.__init__(self)
        '''
        parameters
        '''
        self._ip = ip
        self._port = port
        self._user = user
        self._password = password
        self._mountPoint = mountPoint
        self.setPosition(latitude, longitude)
        self._height = altitude
        self.read_thread = None
        self.check_thread = None
        self._reconnectLimit = 0
        '''
        state
        '''
        self._isRunning = False
        self._reconnect = False
        self._stopByUser = False
        '''
        data
        '''
        self._data = Queue()
        self._socket = None
        self._receiveDataLength = 0

        self.paraValid = True
        self._callback = None

        self._file = None
        self._mountPointList = []

    def setCallback(self, callback):
        self._callback = callback

    def isRunning(self):
        return self._isRunning

    def resetDataLength(self):
        self._receiveDataLength = 0

    def receiveDataLength(self):
        return self._receiveDataLength

    def setLogFile(self, on):
        if on:
            if self._file is None:
                path = os.path.join(os.path.abspath('.'),
                                    'NMEA/' + 'CORS_' + datetime.datetime.now().strftime(
                                        '%Y%m%d_%H%M%S') + '.dat')
                self._file = open(path, 'wb')
        else:
            if self._file is not None:
                self._file.close()
                self._file = None

    def setPosition(self, lat, lon):
        self.flagN = "N"
        self.flagE = "E"
        if lon > 180:
            lon = (lon - 360) * -1
            self.flagE = "W"
        elif 0 > lon >= -180:
            lon = lon * -1
            self.flagE = "W"
        elif lon < -180:
            lon = lon + 360
            self.flagE = "E"
        else:
            self.lon = lon
        if lat < 0:
            lat = lat * -1
            self.flagN = "S"
        self.lonDeg = int(lon)
        self.latDeg = int(lat)
        self.lonMin = (lon - self.lonDeg) * 60
        self.latMin = (lat - self.latDeg) * 60

    def clear(self):
        self._mountPointList.clear()

    def get_mountpoint(self):
        return self._mountPointList

    def set_mount_info(self, mnt):
        user = b64encode((self._user + ":" + str(self._password)).encode('utf-8')).decode()
        mountPointString = "GET /%s HTTP/1.1\r\n" \
                           "User-Agent: %s\r\n" \
                           "Authorization: Basic %s\r\n" % (
                               mnt, "NTRIP FMIPythonClient/1.0", user)
        mountPointString += "\r\n"
        # print(mountPointString)
        _mount_info = mountPointString.encode('utf-8')
        return _mount_info

    def getGGAString(self):
        now = datetime.datetime.utcnow()
        ggaString = "GPGGA,%02d%02d%04.2f,%02d%011.8f,%1s,%03d%011.8f,%1s,1,05,0.19,0,M,%5.3f,M,," % \
                    (now.hour, now.minute, now.second, self.latDeg, self.latMin, self.flagN, self.lonDeg,
                     self.lonMin,
                     self.flagE, self._height)
        checksum = self.check_sum(ggaString)
        ggaStr = "$%s*%s\r\n" % (ggaString, checksum)
        # print('sendGGAString', ggaStr)
        return ggaStr.encode()

    def check_sum(self, stringToCheck):
        xsum_calc = 0
        for char in stringToCheck:
            xsum_calc = xsum_calc ^ ord(char)
        return "%02X" % xsum_calc

    def start(self):

        if self._isRunning is True:
            return
        self._reconnect = False
        try:

            if self._socket is not None:
                self._socket.close()

            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            self._socket.connect((self._ip, self._port))
            self._isRunning = True

            if self.read_thread is not None:
                self.read_thread = None

            self.read_thread = Thread(target=self.receive_data)
            self.read_thread.start()

            self._socket.send(self.set_mount_info(self._mountPoint))
            self._socket.send(self.getGGAString())

        except Exception as e:
            self._isRunning = False
            print("start exp", e)

    def stop(self):
        self._isRunning = False
        self._stopByUser = True
        self.unregisterAll()

        if self._file is not None:
            self._file.flush()
            self._file.close()
            self._file = None

        if self._socket is not None:
            self._socket.close()

    def receive_data(self):

        head = self._socket.recv(1024)
        if b'ICY 200 OK' in head:
            self.start_check()
        elif b'SOURCETABLE 200 OK' in head:
            resp_list = bytes(head).decode().split("\r\n")[6:]
            self._mountPointList = []
            for mnt in resp_list:
                if mnt.startswith('STR;'):
                    self._mountPointList.append(mnt.split(';')[1])
            self._isRunning = False
            return
        else:
            self.paraValid = False
            self._isRunning = False
            # self._callback(False)
            return

        while self._isRunning:
            try:
                data = self._socket.recv(1024)
                if len(data) <= 0:
                    self._reconnectLimit += 1
                else:
                    self._reconnectLimit = 0
                    # 通知所有的串口进行刷新
                    self._receiveDataLength += len(data)
                    self.notifyAll(data)

                    if self._file:
                        self._file.write(data)

                # print(data)
            except Exception as e:
                self._reconnect = True
                self._reconnectLimit += 5
                print('ntrip', e)
                break

    def reconnect(self):

        self._isRunning = False
        self._reconnectLimit = 0
        self._socket.close()
        sleep(3)
        self.start()

    def check(self):

        while self._stopByUser is False and self.paraValid:
            self._reconnectLimit += 1
            if (self._reconnectLimit > 5) | self._reconnect is True:
                self.reconnect()
            try:
                if self._socket is not None:
                    self._socket.send(self.getGGAString())
            except Exception as e:
                print('check', e)
            sleep(5)

    def start_check(self):
        if self.check_thread is None:
            self.check_thread = Thread(target=self.check)
            self.check_thread.start()


if __name__ == '__main__':
    ntrip = NtripClient(ip='lab.ntrip.qxwz.com', port=8002, user="stmicro0010", password='50fcc29', mountPoint='', )
    ntrip.start()
