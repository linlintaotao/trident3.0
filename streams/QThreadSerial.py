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

    def __init__(self, iport, baudRate=115200, coldStart=False, showLog=False):
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

    def writeReadData(self, data):
        if self.writefile and self._file is None:
            path = os.path.join(os.path.abspath('.'),
                                'NMEA/' + self._port.split('/')[-1] + '_' + datetime.datetime.now().strftime(
                                    '%Y%m%d_%H%M%S') + '.nmea')
            self._file = open(path, 'wb')
            if not self._coldStart:
                self._entity.write('AT+READ_PARA\r\n'.encode())

        if self._file:
            self._file.write(data)
            self._file.flush()

    def is_running(self):
        return self._entity is not None and self._entity.isOpen() and self._isRunning

    def open_serial(self):
        self._entity = serial.Serial(self._port, self._baudRate, timeout=1)

    def send_data(self, data, sleepTime=0):
        self.notify(data)

    def notify(self, data):
        self.mutex.lock()
        try:
            if self._entity is not None and self._entity.is_open and self._isRunning:
                if type(data) is str:
                    data = data.encode()
                self._entity.write(data)
                self._entity.flush()
        except Exception as e:
            print('notify', e)
        self.mutex.unlock()

    def run(self):
        if self._entity is None:
            try:
                self.open_serial()
            except Exception as e:
                self.signal.emit(b'STOP SERIAL')
                print('serial_open', e)
                return
        # times = 0
        while self._isRunning and self._entity.is_open:
            try:
                data = self._entity.readline()

                if data is not None and len(data) > 0:
                    self.signal.emit(data)
                    # print(data)
                    self.writeReadData(data)

                if self._coldStart and (b'You Can Reset Now' in data or b'Extract Success,Please Reset' in data):
                    self._coldStart = False
                    self._entity.write('AT+COLD_RESET\r\n'.encode())
                    self.signal.emit(b'Auto cold reset,Please waiting...\r\n')

            except Exception as e:
                print('serial_read', e)
                self.signal.emit(b'READ STOP')
                self._isRunning = False
                continue

    def stop(self):
        self._isRunning = False
        if self._entity is not None:
            self._entity.close()
        if self._file:
            self._file.close()
