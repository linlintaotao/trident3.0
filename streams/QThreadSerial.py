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

    def getPort(self):
        return self._port

    def setFile(self, on=True):
        if on:
            if self._file is None:
                path = os.path.join(os.path.abspath('.'),
                                    'NMEA/' + self._port.split('/')[-1] + '_' + datetime.datetime.now().strftime(
                                        '%Y%m%d_%H%M%S') + '.nmea')
                self._file = open(path, 'wb')
        else:
            if self._file is not None:
                self._file.close()
                self._file = None

    def is_running(self):
        return self._entity.isOpen() & self._isRunning

    def open_serial(self):
        self._entity = serial.Serial(self._port, self._baudRate, timeout=1)
        self._entity.flushInput()
        if self._coldStart:
            self._entity.write('AT+COLD_RESET\r\n'.encode())

    def send_data(self, data, sleepTime=0):
        if self._entity is None:
            return
        self.mutex.lock()
        if self._entity.is_open and self._isRunning:
            print("send data = %s" % str(data))
            if type(data) is str:
                data = data.encode()
            self._entity.write(data)
            sleep(sleepTime)
        self.mutex.unlock()

    def notify(self, data):
        try:
            if self._entity.is_open & self._isRunning:
                self._entity.write(data)
        except Exception as e:
            print(e)

    def run(self):
        if self._entity is None:
            self.open_serial()
        while self._isRunning and self._entity.is_open:
            try:
                data = self._entity.readline()
                if self._file:
                    self._file.write(data)
                    self._file.flush()
                if data is not None and len(data) > 0:
                    self.signal.emit(data)

            except Exception as e:
                print('serial', e)
                self._isRunning = False
                continue

    def stop(self):
        self._isRunning = False
        if self._entity is not None:
            self._entity.close()
        if self._file:
            self._file.flush()
            self._file.close()
