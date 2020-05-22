#!-*-coding:utf-8 -*-

import os
import struct
from struct import pack
import time
import serial

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


class UpgradeManager:

    def __init__(self, listener):

        self.repeatTimes = 0
        self._sendByte = 0
        self._byteList = []
        self._isUpdating = False
        self._serial = None
        self._listener = listener

    def start(self, file, serial):
        self._serial = serial
        # read firm file into file buffer
        file_size = os.stat(file).st_size
        file_buff = b''
        with open(file, "rb") as f:
            for line in f:
                file_buff += line

        # fill trans buffer
        packs = file_size // SUBFRAME_LEN
        if file_size % SUBFRAME_LEN != 0:
            packs += 1

        for i in range(packs):
            if i == packs - 1:
                data = file_buff[i * SUBFRAME_LEN:]
            else:
                data = file_buff[i * SUBFRAME_LEN:(i + 1) * SUBFRAME_LEN]
            trans_buff = spliceData(packs, i, data)
            self._byteList.append(trans_buff)
            self._sendByte += len(data)
            self._serial.write(bytes(trans_buff))
            # print(''.join(['%02X ' % b for b in bytes(trans_buff)]))
            self._listener(True, self._sendByte)

    def parseResponse(self, response):
        if self.repeatTimes > 20:
            return
        for i in range(len(response) - 3):
            if response[i] == 0x55 and response[i + 1] == 0xAA and response[i + 2] == 0x10:
                frame = response[i + 3:]
                if frame[0] == 0x01:
                    # print('Firmware update success')
                    # self._update = Fals
                    if self._listener is not None:
                        self._listener(False, self._sendByte)
                    break

                elif frame[0] == 0x02:  # resend
                    size = byteToint_16(frame[1:3])
                    self._sendByte -= (size * SUBFRAME_LEN)
                    for i in range(size):
                        self._serial.write(self._byteList[byteToint_16(frame[(i + 3):(i + 5)])])
                        self._sendByte += SUBFRAME_LEN
                        self._listener(True, self._sendByte)
                    for i in range(3):
                        self._serial.write(sendCompleteOrder)
                    self.repeatTimes += 1

                else:
                    # print(frame[0], '0: failed')
                    if self._listener is not None:
                        self._listener(False, self._sendByte)
                    # self._update = False


if __name__ == '__main__':

    pass
