# coding= utf-8
import serial
from threading import Thread
from PyQt5.QtCore import QMutex
from PyQt5.QtCore import QThread, pyqtSignal
from time import sleep
import os
import datetime


class SerialThread(QThread):
    signal = pyqtSignal(bytes)

    def __init__(self, iport, baudRate=115200, showLog=False, coldStart=False):
        super().__init__()
        self.mutex = QMutex()
        self._port = iport
        self._baudRate = baudRate
        self._showLog = showLog
        self._read_thread = None
        self._entity = None
        self._file = None
        self._isRunning = True
        self._coldStart = coldStart
        self.writefile = False

    def getPort(self):
        return self._port

    def setFile(self, on=True):
        if on:
            self.writefile = True
        else:
            self.writefile = False
            if self._file is not None:
                self._file.close()
                self._file = None

    def createFile(self):
        if self.writefile and self._file is None:
            path = os.path.join(os.path.abspath('.'),
                                'NMEA/' + self._port.split('/')[-1] + '_' + datetime.datetime.now().strftime(
                                    '%Y%m%d_%H%M%S') + '.nmea')
            self._file = open(path, 'wb')

    def is_running(self):
        return self._entity is not None and self._entity.isOpen() and self._isRunning

    def open_serial(self):
        self._entity = serial.Serial(self._port, self._baudRate, timeout=1)
        # if self._entity.isOpen():
        #     self._entity.close()
        # self._entity.open()

    def send_data(self, data, sleepTime=0):
        if self._entity is None:
            return
        self.mutex.lock()
        if self._entity.is_open and self._isRunning:
            print("send data = %s" % str(data))
            if type(data) is str:
                data = data.encode()
            self._entity.write(data)
            self._entity.flush()
        self.mutex.unlock()
        return

    def notify(self, data):
        try:
            if self._entity is not None and self._entity.is_open and self._isRunning:
                self._entity.write(data)
        except Exception as e:
            print('notify', e)

    def run(self):
        if self._entity is None:
            try:
                self.open_serial()
            except Exception as e:
                self.signal.emit(b'STOP SERIAL')
                print('Exception', e)
                return
        while self._isRunning and self._entity.is_open:
            try:
                data = self._entity.readline()
                self.createFile()

                if self._file:
                    self._file.write(data)
                    self._file.flush()
                if data is not None and len(data) > 0:
                    self.signal.emit(data)
                    if self._coldStart and b'Please Reset' in data:
                        self._coldStart = False
                        sleep(0.5)
                        self._entity.write('AT+COLD_RESET\r\n'.encode())
                        self.signal.emit(b'Auto cold reset,Please waiting...\r\n')

            except Exception as e:
                self.signal.emit(b'READ STOP')
                self._isRunning = False
                continue

    def stop(self):
        self._isRunning = False
        if self._entity is not None:
            self._entity.close()
        if self._file:
            self._file.close()
