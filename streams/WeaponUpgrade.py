#!-*-coding:utf-8 -*-

import os
import struct
from struct import pack
import time
import serial
from PyQt5.QtCore import QThread, pyqtSignal
from threading import Thread

sendCompleteOrder = [0x55, 0xAA, 0x02, 0x00, 0x00, 0x02]
SUBFRAME_LEN = 2048


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
    result = 0
    result = bytes[0]
    result += (bytes[1] << 8) & 0xFF00
    return result


def spliceData(packs, index, buff_data):
    splice_buff = bytearray([0x55, 0xAA, 0x01]) + intTobytes_16(len(buff_data) + 4) + intTobytes_16(
        packs) + intTobytes_16(
        index) + buff_data
    return check_sum(splice_buff)

    # read firm file into file buffer


def getDataFromFile(file):
    file_size = os.stat(file).st_size
    print(file_size)
    file_buff = b''
    with open(file, "rb") as f:
        for line in f:
            file_buff += line
    return file_buff, file_size


class UpgradeManager(QThread):
    signal = pyqtSignal(bytes)

    def __init__(self, listener, port, file):
        super().__init__()
        self.repeatTimes = 0
        self.nothing_read_times = 100
        self._sendByte = 0
        self._byteList = []
        self._isUpdating = False
        self._serial = None
        self._listener = listener
        self._serial = serial.Serial(baudrate=115200, timeout=1)
        self._serial.setPort(port)
        self._file = file
        self.readThread = Thread(target=self.readSerial, daemon=True)

    def run(self):
        self._isUpdating = True
        file_buffer, file_size = getDataFromFile(self._file)
        # fill trans buffer
        packs = file_size // SUBFRAME_LEN
        if file_size % SUBFRAME_LEN != 0:
            packs += 1
        print(self._serial)
        self._serial.open()
        self.readThread.start()
        self._serial.write('AT+UPDATE_MODE_H=460800\r\n'.encode())
        time.sleep(2)
        self._serial.close()
        self._serial.baudrate = 460800
        self._serial.open()

        for i in range(packs):
            if i == packs - 1:
                data = file_buffer[i * SUBFRAME_LEN:]
            else:
                data = file_buffer[i * SUBFRAME_LEN:(i + 1) * SUBFRAME_LEN]
            trans_buff = spliceData(packs, i, data)
            self._byteList.append(trans_buff)
            self._sendByte += len(data)
            if self._serial.isOpen():
                self._serial.write(bytes(trans_buff))
                self._serial.flush()
            else:
                break
            # print(''.join(['%02X ' % b for b in bytes(trans_buff)]))
            self._listener(True, self._sendByte)

        for i in range(3):
            self._serial.write(sendCompleteOrder)

    def parseResponse(self, response):
        print('==>', ''.join(['%02X ' % b for b in bytes(response)]))
        if response is None or len(response) <= 0:
            return
        if len(response) <= 0:
            self.nothing_read_times -= 1
        if self.repeatTimes > 20 or self.nothing_read_times <= 0:
            self._isUpdating = False
            if self._listener is not None:
                self._listener(False, b'Oops! update failed... ')
            self._serial.close()
            return

        if b'Saving OK' in response:
            if self._listener is not None:
                self._listener(False, b'update success!!!')
            self._serial.close()

        for i in range(len(response) - 3):
            if response[i] == 0x55 and response[i + 1] == 0xAA and response[i + 2] == 0x10:
                frame = response[i + 3:]

                if frame[2] == 0x01:
                    # self._isUpdating = False
                    #
                    # self._serial.close()
                    return

                elif frame[2] == 0x02:  # resend
                    length = byteToint_16(frame[0:1])
                    if length > len(frame):
                        return
                    size = byteToint_16(frame[3:5])
                    self._sendByte -= (size * SUBFRAME_LEN)
                    self._serial.write(self._byteList[byteToint_16(frame[(i + 5):(i + 7)])])
                    self._sendByte += SUBFRAME_LEN
                    self._listener(True, self._sendByte)
                    for i in range(3):
                        self._serial.write(sendCompleteOrder)
                    self.repeatTimes += 1

                else:
                    print(frame[0], '0: failed')
                    if self._listener is not None:
                        self._listener(False, b'Oops! update failed...')
                    self._isUpdating = False
                    self._serial.close()
                    break

    def readSerial(self):
        while self._isUpdating:
            try:
                if self._serial.isOpen():
                    bytesData = self._serial.readall()
                    time.sleep(0.1)
                    self.parseResponse(bytesData)
            except Exception as e:
                print(e)


if __name__ == '__main__':
    up = UpgradeManager(None, None, None)
    up.parseResponse(
        [0x55, 0xAA, 0x10, 0x01, 0x00, 0x01, 0x12, 0x01, 0x03, 0x00, 0x04, 0x00, 0x05, 0x00, 0x06, 0x00, 0x07, 0x00,
         0x08, 0x00, 0x09, 0x00, 0x0A])

    pass
