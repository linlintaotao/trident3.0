# -*- coding: utf-8 -*-
""" 
 Created on 12/19/2020 11:07 AM
 
 @author : chey

 use QThread and signal to send result to gui
"""
from PyQt5.QtCore import pyqtSignal, QObject

RTCM3_PREAM = 0xd3
msm_sig_gps = [
    "", "1C", "1P", "1W", "1Y", "1M", "", "2C", "2P", "2W", "2Y", "2M",
    "", "", "2S", "2L", "2X", "", "", "", "", "5I", "5Q", "5X",
    "", "", "", "", "", "1S", "1L", "1X"
]
msm_sig_glo = [
    "", "1C", "1P", "", "", "", "", "2C", "2P", "", "3I", "3Q",
    "3X", "", "", "", "", "", "", "", "", "", "", "",
    "", "", "", "", "", "", "", ""
]
msm_sig_gal = [
    "", "1C", "1A", "1B", "1X", "1Z", "", "6C", "6A", "6B", "6X", "6Z",
    "", "7I", "7Q", "7X", "", "8I", "8Q", "8X", "", "5I", "5Q", "5X",
    "", "", "", "", "", "", "", ""
]
msm_sig_qzs = [
    "", "1C", "", "", "", "", "", "", "6S", "6L", "6X", "",
    "", "", "2S", "2L", "2X", "", "", "", "", "5I", "5Q", "5X",
    "", "", "", "", "", "1S", "1L", "1X"
]
msm_sig_sbs = [
    "", "1C", "", "", "", "", "", "", "", "", "", "",
    "", "", "", "", "", "", "", "", "", "5I", "5Q", "5X",
    "", "", "", "", "", "", "", ""
]
msm_sig_cmp = [
    "", "1I", "1Q", "1X", "", "", "", "6I", "6Q", "6X", "", "",
    "", "7I", "7Q", "7X", "", "", "", "", "", "5I", "5Q", "5X",
    "", "", "", "", "", "", "", ""
]

sys_map = {107: "GPS", 108: "GLO", 109: "GAL", 110: "SBS", 111: "QZS", 112: "BDS"}
sys_sig_map = {107: msm_sig_gps, 108: msm_sig_glo, 109: msm_sig_gal, 110: msm_sig_sbs,
               111: msm_sig_qzs, 112: msm_sig_cmp}

crc24table = (
    0x000000, 0x864CFB, 0x8AD50D, 0x0C99F6, 0x93E6E1, 0x15AA1A,
    0x1933EC, 0x9F7F17, 0xA18139, 0x27CDC2, 0x2B5434, 0xAD18CF,
    0x3267D8, 0xB42B23, 0xB8B2D5, 0x3EFE2E, 0xC54E89, 0x430272,
    0x4F9B84, 0xC9D77F, 0x56A868, 0xD0E493, 0xDC7D65, 0x5A319E,
    0x64CFB0, 0xE2834B, 0xEE1ABD, 0x685646, 0xF72951, 0x7165AA,
    0x7DFC5C, 0xFBB0A7, 0x0CD1E9, 0x8A9D12, 0x8604E4, 0x00481F,
    0x9F3708, 0x197BF3, 0x15E205, 0x93AEFE, 0xAD50D0, 0x2B1C2B,
    0x2785DD, 0xA1C926, 0x3EB631, 0xB8FACA, 0xB4633C, 0x322FC7,
    0xC99F60, 0x4FD39B, 0x434A6D, 0xC50696, 0x5A7981, 0xDC357A,
    0xD0AC8C, 0x56E077, 0x681E59, 0xEE52A2, 0xE2CB54, 0x6487AF,
    0xFBF8B8, 0x7DB443, 0x712DB5, 0xF7614E, 0x19A3D2, 0x9FEF29,
    0x9376DF, 0x153A24, 0x8A4533, 0x0C09C8, 0x00903E, 0x86DCC5,
    0xB822EB, 0x3E6E10, 0x32F7E6, 0xB4BB1D, 0x2BC40A, 0xAD88F1,
    0xA11107, 0x275DFC, 0xDCED5B, 0x5AA1A0, 0x563856, 0xD074AD,
    0x4F0BBA, 0xC94741, 0xC5DEB7, 0x43924C, 0x7D6C62, 0xFB2099,
    0xF7B96F, 0x71F594, 0xEE8A83, 0x68C678, 0x645F8E, 0xE21375,
    0x15723B, 0x933EC0, 0x9FA736, 0x19EBCD, 0x8694DA, 0x00D821,
    0x0C41D7, 0x8A0D2C, 0xB4F302, 0x32BFF9, 0x3E260F, 0xB86AF4,
    0x2715E3, 0xA15918, 0xADC0EE, 0x2B8C15, 0xD03CB2, 0x567049,
    0x5AE9BF, 0xDCA544, 0x43DA53, 0xC596A8, 0xC90F5E, 0x4F43A5,
    0x71BD8B, 0xF7F170, 0xFB6886, 0x7D247D, 0xE25B6A, 0x641791,
    0x688E67, 0xEEC29C, 0x3347A4, 0xB50B5F, 0xB992A9, 0x3FDE52,
    0xA0A145, 0x26EDBE, 0x2A7448, 0xAC38B3, 0x92C69D, 0x148A66,
    0x181390, 0x9E5F6B, 0x01207C, 0x876C87, 0x8BF571, 0x0DB98A,
    0xF6092D, 0x7045D6, 0x7CDC20, 0xFA90DB, 0x65EFCC, 0xE3A337,
    0xEF3AC1, 0x69763A, 0x578814, 0xD1C4EF, 0xDD5D19, 0x5B11E2,
    0xC46EF5, 0x42220E, 0x4EBBF8, 0xC8F703, 0x3F964D, 0xB9DAB6,
    0xB54340, 0x330FBB, 0xAC70AC, 0x2A3C57, 0x26A5A1, 0xA0E95A,
    0x9E1774, 0x185B8F, 0x14C279, 0x928E82, 0x0DF195, 0x8BBD6E,
    0x872498, 0x016863, 0xFAD8C4, 0x7C943F, 0x700DC9, 0xF64132,
    0x693E25, 0xEF72DE, 0xE3EB28, 0x65A7D3, 0x5B59FD, 0xDD1506,
    0xD18CF0, 0x57C00B, 0xC8BF1C, 0x4EF3E7, 0x426A11, 0xC426EA,
    0x2AE476, 0xACA88D, 0xA0317B, 0x267D80, 0xB90297, 0x3F4E6C,
    0x33D79A, 0xB59B61, 0x8B654F, 0x0D29B4, 0x01B042, 0x87FCB9,
    0x1883AE, 0x9ECF55, 0x9256A3, 0x141A58, 0xEFAAFF, 0x69E604,
    0x657FF2, 0xE33309, 0x7C4C1E, 0xFA00E5, 0xF69913, 0x70D5E8,
    0x4E2BC6, 0xC8673D, 0xC4FECB, 0x42B230, 0xDDCD27, 0x5B81DC,
    0x57182A, 0xD154D1, 0x26359F, 0xA07964, 0xACE092, 0x2AAC69,
    0xB5D37E, 0x339F85, 0x3F0673, 0xB94A88, 0x87B4A6, 0x01F85D,
    0x0D61AB, 0x8B2D50, 0x145247, 0x921EBC, 0x9E874A, 0x18CBB1,
    0xE37B16, 0x6537ED, 0x69AE1B, 0xEFE2E0, 0x709DF7, 0xF6D10C,
    0xFA48FA, 0x7C0401, 0x42FA2F, 0xC4B6D4, 0xC82F22, 0x4E63D9,
    0xD11CCE, 0x575035, 0x5BC9C3, 0xDD8538)


class RtcmParse(QObject):
    """
    rtcm3 parse class, currently only support msm3 ~ msm7 header message and 1005/1006 msg dump
    A more pythonic way of dump binary msgs

    TODO: dump body in later version
    """
    signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._sys = 0
        self._len = 0
        self._nbyte = 0
        self._binstr = ''
        self._msg_type = 0

    def decode(self, _data):
        for byte in _data:
            if self._nbyte == 0:
                if byte != RTCM3_PREAM:
                    continue
                self._binstr += format(byte, '08b')
                self._nbyte += 1
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
            self._msg_type = sys_map[sys]
        else:
            return
        self._msg_type += f' msm{msm}'
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
            posx, posy, posz = [format(self.getbits_38(i) * 1e-4, '.3f') for i in range(i, i + 40 * 3, 40)]
            # developer should show this info in GUI program, this base ECEF position in millimeters
            print(f'msg {msgtype}, pos ecef {posx, posy, posz}, staid {staid}')
            self.signal.emit(f'msg {msgtype}, pos ecef {posx, posy, posz}, staid {staid}')
        else:
            print(f'msg {msgtype} length error!')

    def _dump_msm3(self):
        self._dump_msg_header()

    def _dump_msm4(self):
        self._dump_msg_header()

    def _dump_msm5(self):
        self._dump_msg_header()

    def _dump_msm6(self):
        self._dump_msg_header()

    def _dump_msm7(self):
        self._dump_msg_header()

    def _dump_msg_header(self):
        i = 36
        if i + 157 < self._len * 8:
            i += 42
            sync = self.getbitu(i, 1)
            i += 19
            nsats = sum([self.getbitu(j, 1) for j in range(i, i + 64)])
            i += 64
            siglist = []
            sigs = [self.getbitu(j, 1) for j in range(i, i + 32)]
            for j, sig in enumerate(sigs, 1):
                if sig:
                    siglist.append(sys_sig_map[self._sys][j - 1])
            # developer should show this info in GUI program, these are satellites/signals of each msm messages
            print(f'{self._msg_type}, sync {sync}, sats {nsats:2}, sigs {siglist}')
            self.signal.emit(f'{self._msg_type}, sync {sync}, sats {nsats:2}, sigs {siglist}')
        else:
            # print(f'invalid msg header {self._msg_type}')
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
            return int(bits)
        return int(bits | (~0 << _len))


def test(filepath):
    parse = RtcmParse()
    with open(filepath, 'rb') as fd:
        for data in fd:
            parse.decode(data)


if __name__ == '__main__':
    file = '../NMEA/CORS_20201215_155249.dat'
    test(file)
