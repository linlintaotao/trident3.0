#!-*-coding:utf-8 -*-

import os
from struct import pack
import time

sendCompleteOrder = [0xAA, 0x55, 0x02, 0x00, 0x00, 0x01]
SUBFRAME_LEN = 2048


def check_sum(buff):
    cs = 0x00
    for b in buff[2:]:
        cs += b
    buff += pack('B', cs & 0xFF)
    return buff


def spliceData(buffHead, buffData):
    spliceBuff = [0x55, 0xAA, 0x01, buffHead, buffData]

    return check_sum(spliceBuff)


class UpgradeManager:

    def __init__(self, listener):

        self._sendByte = 0
        self._byteList = []
        self._isUpdating = False
        self._update = True
        self._listener = listener

    def start(self, file, serial):

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

        serial.baudrate = 460800
        # send buff
        for i in range(packs):
            if i == packs - 1:
                data = file_buff[i * SUBFRAME_LEN:]
            else:
                data = file_buff[i * SUBFRAME_LEN:(i + 1) * SUBFRAME_LEN]
            trans_buff = spliceData(pack('HB', packs, i), data)
            self._byteList.append(trans_buff)
            self._sendByte += len(data)
            serial.write(trans_buff)
            self._listener(self._sendByte)

        # send complete order
        repeatTimes = 0
        while self._update and repeatTimes < 20:
            for i in range(3):
                serial.write(sendCompleteOrder)
            time.sleep(10)
            response = serial.readall()
            for i in range(len(response) - 3):
                if response[i] == 0xAA and response[i + 1] == 0x55 and response[i + 2] == 0x10:
                    frame = response[i + 2:]
                    if frame[0] == 0x01:
                        print('Firmware update success')
                        self._update = False
                        break
                    elif frame[0] == 0x02:  # resend
                        size = int(frame[1])
                        self._sendByte -= (size * SUBFRAME_LEN)
                        for i in range(size):
                            serial.write(self._byteList[frame[i + 2]])
                            self._sendByte += SUBFRAME_LEN
                            self._listener(self._sendByte)
                    else:
                        print(frame[0], '0: failed')
                        self._update = False
            repeatTimes += 1
