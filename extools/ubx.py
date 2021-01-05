import re
from PyQt5.QtCore import QThread, pyqtSignal

GPGGA = "GPGGA,%s,%3.7f,N,%5.7f,E,1,12,2.0,%.6s,M,0,M,0,0000"


def getGGAString(time, lat, lon, height):
    ggaString = GPGGA % (time, lat, lon, height)
    checksum = check_sum(ggaString)
    ggaStr = "$%s*%s\r\n" % (ggaString, checksum)
    # print('sendGGAString', ggaStr)
    return ggaStr


def check_sum(stringToCheck):
    xsum_calc = 0
    for char in stringToCheck:
        xsum_calc = xsum_calc ^ ord(char)
    return "%02X" % xsum_calc


def ddTodm(data):
    dd = float(data)
    dm = int(dd) * 100
    mm = (dd - int(dd)) * 60
    return dm + mm


def parse(time, line):
    data = re.split('[, ]', str(line))
    return getGGAString(time, float(ddTodm(data[5])), float(ddTodm(data[7])), data[9])


class LogReader(QThread):
    signal = pyqtSignal(str)

    def __init__(self, path=None):
        super().__init__()
        self._path = path

    def run(self):
        self.readfile(self._path)

    def readfile(self, path):
        pathRes = path + 'UTG.log'
        with open(path, "rb") as rf:
            lines = rf.readlines()
        with open(pathRes, 'w', encoding="utf-8") as fw:
            for i in range(len(lines)):
                if b'>>> ubx' in lines[i]:
                    try:
                        dataline = re.split('[,\]]', str(lines[i]))
                        print(dataline)
                        nowtime = int(dataline[1])
                        for j in range(20):
                            if b'$GNGGA' in lines[i + j]:
                                readline = str(lines[i + j])
                                time = int(re.split('[,\]]', readline)[1])
                                if time <= (nowtime + 200):
                                    p20time = readline.split(',')[2]
                                    fw.write(parse(p20time, lines[i]))
                                break
                    except Exception as e:
                        print(e)
                        fw.write("error timestamp in header,can't match gga & ubx time\r\n")
                i += 1
        self.signal.emit("parse Log data complete!")


if __name__ == '__main__':
    # readfile()
    pass
