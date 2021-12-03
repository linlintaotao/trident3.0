# sys_map = {107: "GPS", 108: "GLO", 109: "GAL", 110: "SBS", 111: "QZS", 112: "BDS", 113: "IRN", 0: ""}
import math

SYS_GPS = 107
SYS_GLO = 108
SYS_GAL = 109
SYS_SBS = 110
SYS_QZS = 111
SYS_CMP = 112
SYS_IRN = 113

CLIGHT = 299792458.0
DAY_SECONDS = 86400
WEEK_SECONDS = 604800
RANGE_MS = CLIGHT * 0.001

P2_10 = 0.0009765625
P2_29 = 1.862645149230957E-09
P2_31 = 4.656612873077393E-10

RTCM3_PREAM = 0xd3
RTCM3_RESVMASK = 0xFC

FREQ1 = 1.57542E9
FREQ2 = 1.22760E9
FREQ5 = 1.17645E9
FREQ6 = 1.27875E9
FREQ7 = 1.20714E9
FREQ8 = 1.191795E9
FREQ9 = 2.492028E9
FREQ1_GLO = 1.60200E9
DFRQ1_GLO = 0.56250E6
FREQ2_GLO = 1.24600E9
DFRQ2_GLO = 0.43750E6
FREQ3_GLO = 1.202025E9
FREQ1a_GLO = 1.600995E9
FREQ2a_GLO = 1.248060E9
FREQ1_CMP = 1.561098E9
FREQ2_CMP = 1.20714E9
FREQ3_CMP = 1.26852E9

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
# msm_sig_cmp = [
#     "", "1I", "1Q", "1X", "", "", "", "6I", "6Q", "6X", "", "",
#     "", "7I", "7Q", "7X", "", "", "", "", "", "5I", "5Q", "5X",
#     "", "", "", "", "", "", "", ""
# ]
msm_sig_cmp = [
    "", "2I", "2Q", "2X", "", "", "", "6I", "6Q", "6X", "", "",
    "", "7I", "7Q", "7X", "", "", "", "", "", "5I", "5Q", "5X",
    "", "", "", "", "", "1D", "1P", "1X"
]

msm_sig_irn = [
    "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
    "", "", "", "", "", "", "5A", "", "", "", "",
    "", "", "", "", "", ""
]

sys_map = {107: "GPS", 108: "GLO", 109: "GAL", 110: "SBS", 111: "QZS", 112: "BDS", 113: "IRN", 0: ""}
sys_sig_map = {107: msm_sig_gps, 108: msm_sig_glo, 109: msm_sig_gal, 110: msm_sig_sbs,
               111: msm_sig_qzs, 112: msm_sig_cmp, 113: msm_sig_irn}

MINPRNGPS = 1
MAXPRNGPS = 32
MINPRNGLO = 1
MAXPRNGLO = 27
MINPRNGAL = 1
MAXPRNGAL = 36
MINPRNQZS = 1
MAXPRNQZS = 10
MINPRNCMP = 1
MAXPRNCMP = 63

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

obscodes = [
    "", "1C", "1P", "1W", "1Y", "1M", "1N", "1S", "1L", "1E",
    "1A", "1B", "1X", "1Z", "2C", "2D", "2S", "2L", "2X", "2P",
    "2W", "2Y", "2M", "2N", "5I", "5Q", "5X", "7I", "7Q", "7X",
    "6A", "6B", "6C", "6X", "6Z", "6S", "6L", "8L", "8Q", "8X",
    "2I", "2Q", "6I", "6Q", "3I", "3Q", "3X", "1I", "1Q", "5A",
    "5B", "5C", "9A", "9B", "9C", "9X", "1D", "5D", "5P", "5Z",
    "6E", "7D", "7P", "7Z", "8D", "8P", "4A", "4B", "4X", ""]


def code2freq_GPS(code):
    if code[0] == '1':
        return 0, FREQ1
    elif code[0] == '2':
        return 1, FREQ2
    elif code[0] == '5':
        return 2, FREQ5
    return -1, 0


def code2freq_GLO(code):
    # todo fcn =1 is not true value
    fcn = 1
    if code[0] == '1':
        return 0, FREQ1_GLO + DFRQ1_GLO * fcn
    elif code[0] == '2':
        return 1, FREQ2_GLO + DFRQ2_GLO * fcn
    elif code[0] == '3':
        return 2, FREQ3_GLO
    elif code[0] == '4':
        return 3, FREQ1a_GLO
    elif code[0] == '6':
        return 4, FREQ2a_GLO
    return -1, 0


def code2freq_GAL(code):
    if code[0] == '1':
        return 0, FREQ1
    elif code[0] == '7':
        return 1, FREQ7
    elif code[0] == '5':
        return 2, FREQ5
    elif code[0] == '6':
        return 3, FREQ6
    elif code[0] == '8':
        return 4, FREQ8
    return -1, 0


def code2freq_QZS(code):
    if code[0] == '1':
        return 0, FREQ1
    elif code[0] == '2':
        return 1, FREQ2
    elif code[0] == '5':
        return 2, FREQ5
    elif code[0] == '6':
        return 3, FREQ6
    return -1, 0


def code2freq_BDS(code):
    if len(code) < 1:
        return -1, 0
    if code[0] == '1':
        return 0, FREQ1
    elif code[0] == '2':
        return 0, FREQ1_CMP
    elif code[0] == '7':
        return 1, FREQ2_CMP
    elif code[0] == '5':
        return 2, FREQ5
    elif code[0] == '6':
        return 3, FREQ3_CMP
    elif code[0] == '8':
        return 4, FREQ8
    return -1, 0


code2freq = {
    107: code2freq_GPS,
    108: code2freq_GLO,
    109: code2freq_GAL,
    111: code2freq_QZS,
    112: code2freq_BDS
}


def satno2Id(sys, prn):
    if prn <= 0:
        return 0
    if sys is SYS_GPS:
        if MINPRNGPS < prn < MAXPRNGPS:
            return "G%2d" % (prn - MINPRNGPS + 1)
    elif sys is SYS_GLO:
        if MINPRNGLO < prn < MAXPRNGLO:
            return "R%02d" % (prn - MINPRNGLO + 1)
    elif sys is SYS_GAL:
        if MINPRNGAL < prn < MAXPRNGAL:
            return "E%02d" % (prn - MINPRNGAL + 1)
    elif sys is SYS_QZS:
        if MINPRNQZS < prn < MAXPRNQZS:
            return "J%02d" % (prn - MINPRNQZS + 1)
    elif sys is SYS_CMP:
        if MINPRNCMP < prn < MAXPRNCMP:
            return "C%02d" % (prn - MINPRNCMP + 1)

    return ""


def obs2code(sig):
    for i in range(len(obscodes)):
        if obscodes[i] == sig:
            return i
    return -1


class Obs:

    def __init__(self):
        self.time = None
        self.satList = {}

    def addSatInfo(self, sat, satInfo):
        self.satList[sat] = satInfo

    def getSatList(self):
        return self.satList

    def clear(self):
        self.time = ''
        self.satList.clear()


a = 6378137.0
e2 = 0.0066943799013


def LatLon2XY(latitude, longitude):
    # 将经纬度转换为弧度
    latitude2Rad = (math.pi / 180.0) * latitude
    beltNo = int((longitude + 1.5) / 3.0)  # 计算3度带投影度带号
    L = beltNo * 3  # 计算中央经线
    l0 = longitude - L  # 经差
    tsin = math.sin(latitude2Rad)
    tcos = math.cos(latitude2Rad)
    t = math.tan(latitude2Rad)
    m = (math.pi / 180.0) * l0 * tcos
    et2 = e2 * pow(tcos, 2)
    et3 = e2 * pow(tsin, 2)
    X = 111132.9558 * latitude - 16038.6496 * math.sin(2 * latitude2Rad) + 16.8607 * math.sin(
        4 * latitude2Rad) - 0.0220 * math.sin(6 * latitude2Rad)
    N = a / math.sqrt(1 - et3)

    x = X + N * t * (0.5 * pow(m, 2) + (5.0 - pow(t, 2) + 9.0 * et2 + 4 * pow(et2, 2)) * pow(m, 4) / 24.0 + (
            61.0 - 58.0 * pow(t, 2) + pow(t, 4)) * pow(m, 6) / 720.0)
    y = 500000 + N * (m + (1.0 - pow(t, 2) + et2) * pow(m, 3) / 6.0 + (
            5.0 - 18.0 * pow(t, 2) + pow(t, 4) + 14.0 * et2 - 58.0 * et2 * pow(t, 2)) * pow(m, 5) / 120.0)

    return x, y


radius = 6371000
D2R = 0.017453292519943295


def diffN(latX, latY):
    return (latY - latX) * D2R * radius


def diffE(lonX, lonY):
    return (lonY - lonX) * D2R * radius * math.cos(lonX * D2R)
