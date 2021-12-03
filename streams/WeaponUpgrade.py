#!-*-coding:utf-8 -*-

import os
import struct
from struct import pack
import time
import serial
from PyQt5.QtCore import QThread, pyqtSignal
from threading import Thread

sendCompleteOrder = [0x55, 0xAA, 0x02, 0x00, 0x00, 0x02]
SUBFRAME_LEN = 2048  # 2048


def check_sum(buff):
    cs = 0
    for b in buff[2:]:
        cs += b
    buff += pack('B', cs & 0xFF)
    return buff


def intTobytes_16(num):
    result = b''
    result = pack('B', num & 0xFF)
    result += pack('B', (num >> 8) & 0xFF)
    return result


def byteToint_16(bytes):
    result = bytes[0]
    result += (bytes[1] << 8) & 0xFF00
    return result


def spliceData(packs, index, buff_data):
    splice_buff = bytearray([0x55, 0xAA, 0x01]) + intTobytes_16(len(buff_data) + 4) + intTobytes_16(
        packs) + intTobytes_16(
        index) + buff_data
    return check_sum(splice_buff)


def getDataFromFile(file):
    file_size = os.stat(file).st_size

    file_buff = b''
    with open(file, "rb") as f:
        file_buff = f.read()
    return file_buff, file_size


class UpgradeManager(QThread):
    signal = pyqtSignal(bool, bytes, int)

    def __init__(self, port, file, updateBaudrate=460800):
        super().__init__()
        self.repeatTimes = 0
        self.nothing_read_times = 100
        self._sendByteLen = 0
        self._byteList = []
        self._serial = None
        self._file = file
        self._isUpdating = True
        self.updateSucess = False
        self._serial = serial.Serial(baudrate=115200, timeout=0.5)
        self._serial.setPort(port)
        self.readThread = Thread(target=self.readSerial, daemon=True)
        self.updateBaudrate = updateBaudrate
        # self.updateBaudrate = 921600

    def run(self):
        file_buffer, file_size = getDataFromFile(self._file)
        # fill trans buffer
        packs = file_size // SUBFRAME_LEN
        if file_size % SUBFRAME_LEN != 0:
            packs += 1
        try:
            self._serial.open()
            self._serial.write(f'AT+UPDATE_MODE_H={self.updateBaudrate}\r\n'.encode())
        except Exception as e:
            self.signal.emit(False, b'serial port open failed! please check', 0)
            return
        readtimes = 60
        while readtimes > 0:
            returnData = self._serial.readline()
            if b"OK" in returnData:
                self.signal.emit(True, b'Send update order success !!!', 0)
                break
            if readtimes <= 10:
                self.signal.emit(False, b'no response,pls try again!', 0)
                if self._serial.isOpen():
                    self._serial.close()
                return

        time.sleep(0.2)
        if self.updateBaudrate != 115200:
            self._serial.close()
            self._serial.baudrate = self.updateBaudrate
            self._serial.open()

        self.readThread.start()
        for i in range(packs):
            if i == packs - 1:
                data = file_buffer[i * SUBFRAME_LEN:]
            else:
                data = file_buffer[i * SUBFRAME_LEN:(i + 1) * SUBFRAME_LEN]
            trans_buff = spliceData(packs, i, data)
            self._byteList.append(trans_buff)
            self._sendByteLen += len(data)
            self.write(bytes(trans_buff))
            self.signal.emit(True, b'', self._sendByteLen)
            if not self._isUpdating:
                break
        for i in range(3):
            self.write(sendCompleteOrder)

    def write(self, bytesData):
        try:
            if self._serial is None:
                return
            if self._serial.isOpen():
                self._serial.write(bytesData)
                # print('write ==>', ''.join(['%02X ' % b for b in bytesData]))
                self._serial.flush()
                time.sleep(0.005)
        except Exception as e:
            print(e)

    def parseResponse(self, response):
        if response is None or len(response) <= 0:
            self.nothing_read_times -= 1
            return
        if self.repeatTimes > 30 or self.nothing_read_times <= 0:
            self._isUpdating = False
            self.signal.emit(False, b'Oops! update failed... ', self._sendByteLen)
            self._serial.close()
            return
        if len(response) < 5: return
        for i in range(len(response) - 3):
            if response[i] == 0x55 and response[i + 1] == 0xAA and response[i + 2] == 0x10:
                frame = response[i + 3:]

                if frame[2] == 0x01:
                    self.signal.emit(True, b'Trans Complete!!!', self._sendByteLen)
                    self._isUpdating = False
                    self.updateSucess = True
                    return

                elif frame[2] == 0x02:  # resend
                    length = byteToint_16(frame[0:2])
                    if length > len(frame) - 3:
                        return
                    size = byteToint_16(frame[3:5])
                    self._sendByteLen -= (size * SUBFRAME_LEN)
                    for i in range(size):
                        self.write(self._byteList[byteToint_16(frame[(i * 2 + 5):(i * 2 + 7)])])
                    self._sendByteLen += SUBFRAME_LEN
                    for j in range(3):
                        self._serial.write(sendCompleteOrder)
                    self._serial.flush()
                    self.repeatTimes += 1
                    continue
                else:
                    self.signal.emit(False, b'Oops! update failed...', self._sendByteLen)
                    self._isUpdating = False
                    self._serial.close()
                    break

    def readSerial(self):
        readSerialMax = 800
        try:
            while self._isUpdating:
                if self._serial.isOpen():
                    bytesData = self._serial.read(2048)
                    time.sleep(0.1)
                    if len(bytesData) > 0:
                        self.parseResponse(bytesData)
                        print(bytesData)
                    else:
                        readSerialMax -= 1
                        if readSerialMax <= 0:
                            self._isUpdating = False
                            self.signal.emit(False, b'Oops! update failed... ', self._sendByteLen)
                            break
                else:
                    break
            if self._serial.isOpen():
                self._serial.close()

            self.signal.emit(False, b'Waiting......' if self.updateSucess else b'please try again',
                             self._sendByteLen)
        except Exception as e:
            print('read serial====', e)
        self._isUpdating = False


if __name__ == '__main__':
    up = UpgradeManager(None, None, None)
    up.parseResponse(
        [0x55, 0xAA, 0x10, 0xF9, 0x03, 0x02, 0xFB, 0x01, 0x01, 0x00, 0x02, 0x00, 0x03, 0x00, 0x04, 0x00, 0x05, 0x00,
         0x08, 0x00, 0x09, 0x00, 0x0A])

    pass
