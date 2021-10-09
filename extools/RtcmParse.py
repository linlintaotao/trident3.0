# -*- coding: utf-8 -*-
""" 
 Created on 12/19/2020 11:07 AM
 
 @author : chey

 use QThread and signal to send result to gui
"""
from PyQt5.QtCore import pyqtSignal, QObject

from extools.rtkcmn import *


class RtcmParse(QObject):
    """
    rtcm3 parse class, currently only support msm3 ~ msm7 header message and 1005/1006 msg dump
    A more pythonic way of dump binary msgs

    """
    signal = pyqtSignal(str)
    msmSingnal = pyqtSignal(Obs)

    def __init__(self):
        super().__init__()
        self._sys = 0
        self._len = 0
        self._nbyte = 0
        self._binstr = ''
        self._sys_name = ''
        self._msg_type = 0
        self._tow = ''
        self.obs = Obs()

    def decode(self, _data):
        for byte in _data:
            if self._nbyte == 0:
                if byte != RTCM3_PREAM:
                    continue
                self._binstr += format(byte, '08b')
                self._nbyte = 1
                continue
            self._binstr += format(byte, '08b')
            self._nbyte += 1

            if self._nbyte == 3:
                self._len = self.getbitu(14, 10) + 3

            if self._nbyte < 3 or self._nbyte < (self._len + 3):
                continue

            self._nbyte = 0
            if self.crc_check() != self.getbitu(self._len * 8, 24):
                self._binstr = ''
                continue
            self.dump()
            self._binstr = ''

    def dump(self):
        t = self.getbitu(24, 12)
        msm = t % 10
        sys = t // 10
        if t == 1005 or t == 1006:
            self._dump_base_pos(t)
            return

        if sys in sys_map.keys():
            self._sys_name = sys_map[sys]
        else:
            return
        self._msg_type = f'{self._sys_name} msm {msm}'
        self._sys = sys

        if msm == 3:
            self._dump_msm3()
        elif msm == 4:
            self._dump_msm4()
        elif msm == 5:
            self._dump_msm5()
        elif msm == 6:
            self._dump_msm6()
        elif msm == 7:
            self._dump_msm7()
        else:
            pass
            # print(f'updating soon...')

    def _dump_base_pos(self, msgtype):
        i = 36
        cond = False
        if msgtype == 1005:
            cond = (i + 140 == self._len * 8)
        else:
            cond = (i + 156 <= self._len * 8)
        if cond:
            staid = self.getbitu(i, 12)
            i += 22
            posx, posy, posz = [format(self.getbits_38(i) * 1e-4, '.4f') for i in range(i, i + 40 * 3, 40)]
            # developer should show this info in GUI program, this base ECEF position in millimeters
            # print(f'msg {msgtype}, pos ecef {posx, posy, posz}, staid {staid}')
            # self.signal.emit(f'msg {msgtype}, pos ecef {posx, posy, posz}, staid {staid}')
            self.signal.emit(f'msg %s, pos %s, %s, %s, id %s' % (msgtype, posx, posy, posz, staid))
        else:
            print(f'msg {msgtype} length error!')

    def _dump_msm3(self):
        self._dump_msg_header(3)

    def _dump_msm4(self):
        self._dump_msg_header(4)

    def _dump_msm5(self):
        self._dump_msg_header(5)

    def _dump_msm6(self):
        self._dump_msg_header(6)

    def _dump_msm7(self):
        self._dump_msg_header(7)

    def _dump_msg_header(self, msgtype):
        i = 36
        if i + 157 <= self._len * 8:
            i += 12
            if self._sys == 108:
                _dow = self.getbitu(i, 3)
                _tod = self.getbitu(i, 27)
            else:
                _tow = self.getbitu(i, 30)
                if self._sys == 112:
                    _tow += 14000
                self._tow = f'{_tow}'
            # decode sync bit
            i += 30
            sync = self.getbitu(i, 1)
            # get number of valid sats in current frame
            i += 19
            satList = [self.getbitu(j, 1) for j in range(i, i + 64)]
            nsats = sum(satList)
            # get signal list
            i += 64
            siglist = []
            sigs = [self.getbitu(j, 1) for j in range(i, i + 32)]
            for j, sig in enumerate(sigs, 1):
                if sig:
                    siglist.append(str(sys_sig_map[self._sys][j - 1]))

            # get number of cells of each frame
            i += 32
            signalSize = len(siglist)
            cellMask = [self.getbitu(j, 1) for j in range(i, i + nsats * signalSize)]
            ncells = sum(cellMask)

            # get CN0 、（pseudorange、phaserange)msm7 of each cell
            if msgtype == 4:
                i += nsats * signalSize + nsats * 18 + ncells * 42
                cnos = [self.getbitu(j, 6) for j in range(i, i + ncells * 6, 6)]
            elif msgtype == 5:
                i += nsats * signalSize + nsats * 36 + ncells * 42
                cnos = [self.getbitu(j, 6) for j in range(i, i + ncells * 6, 6)]
            elif msgtype == 6:
                i += nsats * signalSize + nsats * 18 + ncells * 55
                cnos = [self.getbitu(j, 10) * 0.0625 for j in range(i, i + ncells * 10, 10)]
            elif msgtype == 7:
                i += nsats * signalSize
                # range
                satsrange = [self.getbitu(j, 8) * RANGE_MS if self.getbitu(j, 8) != 255 else 0 for j in
                             range(i, i + nsats * 8, 8)]
                i += nsats * 12
                satsRange_m = [self.getbitu(j, 10) * RANGE_MS * P2_10
                               for j in range(i, i + nsats * 10, 10)]
                satsrange = [(satsrange[j] + satsRange_m[j]) if satsrange[j] != 0 else 0 for j in range(nsats)]
                i += nsats * 10
                # rr = [self.getbits(j, 14) * 1.0 if self.getbits(j, 14) != -8192 else 0 for j in
                #       range(i, i + nsats * 14, 14)]
                i += nsats * 14
                # # pseudorange
                # pr = [(self.getbits(j, 20) * RANGE_MS * P2_29) if self.getbits(j, 20) != -524288 else -1e16 for j in
                #       range(i, i + ncells * 20, 20)]
                i += ncells * 20
                cp = [(self.getbits(j, 24) * RANGE_MS * P2_31) if self.getbits(j, 24) != -8388608 else -1e16 for j in
                      range(i, i + ncells * 24, 24)]
                i += ncells * 24
                # lock = [self.getbitu(j, 10) for j in range(i, i + ncells * 10, 10)]
                i += ncells * 10
                # half = [self.getbitu(j, 10) for j in range(i, i + ncells * 1, 1)]
                i += ncells * 1
                cnos = [self.getbitu(j, 10) * 0.0625 for j in range(i, i + ncells * 10, 10)]
                i += ncells * 10
                # rrf = [self.getbits(j, 15) * 0.0001 if self.getbitu(j, 15) != -16384 else -1e16 for j in
                #        range(i, i + ncells * 15, 15)]
                index = 0
                j = 0
                for prn, sat in enumerate(satList, 1):
                    if sat:
                        satId = satno2Id(self._sys, prn)
                        if len(satId) <= 0:
                            continue
                        info = []
                        for k in range(signalSize):
                            if not cellMask[k + index * signalSize]: continue
                            idx, freq = code2freq[self._sys](siglist[k])
                            psed = phase = dloper = 0
                            if idx < 0: continue
                            # if satsrange[index] != 0 and pr[j] > -1E12:
                            #     psed = satsrange[index] + pr[j]
                            if satsrange[index] != 0 and cp[j] > -1E12:
                                phase = (satsrange[index] + cp[j]) * freq / CLIGHT
                            # dloper = -(rr[index] + rrf[j]) * freq / CLIGHT
                            cnr = round(cnos[j])
                            info.append([siglist[k], psed, phase, dloper, cnr])
                            j += 1
                        # if 'R' not in satId:
                        self.obs.addSatInfo(satId, info)
                        # print(satId, info)
                        index += 1
            else:
                cnos = [-1]

            mean_cno = sum(cnos) / len(cnos) if len(cnos) > 0 else 0

            # developer should show this info in GUI program, these are satellites/signals of each msm messages
            sigStr = ",".join(f'%3s' % x for x in siglist)
            # print(f'%s, tow %s, sync %2d, sats %2d, cno mean %2d, sigs [%3s]' %
            #       (self._msg_type, self._tow, sync, nsats, mean_cno, sigStr))
            self.signal.emit(f'%s, tow %s, sync %2d, sats %2d, cno mean %2d, sigs [%3s]' %
                             (self._msg_type, self._tow, sync, nsats, mean_cno, sigStr))
            if sync == 0:
                self.obs.time = self._tow
                # if float(self.obs.time) % 1000 == 0:
                self.msmSingnal.emit(self.obs)
                self.obs.clear()
                self.signal.emit("\n")

    def _dump_msm7_body(self):
        pass

    def crc_check(self):
        crc = 0
        for i in range(self._len):
            crc = ((crc << 8) & 0xFFFFFF) ^ crc24table[(crc >> 16) ^ int(self._binstr[i * 8:i * 8 + 8], 2)]
        return crc

    def getbits_38(self, _pos):
        return self.getbits(_pos, 32) * 64.0 + self.getbitu(_pos + 32, 6)

    def getbitu(self, _pos, _len):
        return int(self._binstr[_pos:_pos + _len], 2)

    def getbits(self, _pos, _len):
        bits = self.getbitu(_pos, _len)
        if _len <= 0 or _len >= 32 or not (bits & (1 << (_len - 1))):
            if self._binstr[_pos] == '1':
                return int(bits) - 2 ** 32
            else:
                return int(bits)
        return int(bits | (~0 << _len))


def rangeArrayAdd(array1, array2):
    if len(array1) < len(array2):
        size = len(array1)
    else:
        size = len(array2)
    result = [(array1[i] + array2[i]) for i in range(size)]
    return result


def test(filepath):
    parse = RtcmParse()
    with open(filepath, 'rb') as fd:
        for data in fd:
            parse.decode(data)


if __name__ == '__main__':
    # import serial
    #
    # # _entity = serial.Serial("/dev/cu.usbserial-1420", 115200, timeout=1)
    rtcmParsce = RtcmParse()

    with open('../NMEA/COM11_20210907_181825.nmea', 'rb') as rf:
        for line in rf.readlines():
            rtcmParsce.decode(line)
