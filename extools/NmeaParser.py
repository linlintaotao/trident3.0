# parse NMEA data
import math


def parseGGA(GGA):
    GGA = GGA.strip("\r\n")
    if checkSum(GGA):
        splitData = GGA.split(',')
        now, latdm = splitData[1:3]
        londm = splitData[4]
        solstat, nsats, dop, hgt = splitData[6:10]
        dage = splitData[-2]

        return now, latdm, londm, solstat, nsats, dop, hgt, dage
    else:
        return []


def parseRMC(RMC):
    pass


def parseGSA(GSA):
    pass


def parseGSV(GSV):
    pass


def parseFMI(FMI):
    pass


def checkSum(data):
    if data is None or len(data) <= 0:
        return False
    try:
        if isinstance(data, str):
            checkData = data
        else:
            checkData = data.decode()
        checkData = checkData.strip('\r\n')
        if checkData[-3] != '*':
            return False
        xsum_calc = 0
        for char in checkData:
            if char == '$':
                continue
            if char == '*':
                break
            xsum_calc = xsum_calc ^ ord(char)
        return ("%02X" % xsum_calc) == checkData[-2:]
    except Exception as e:
        return False


def dformate(latlon):
    latlon = math.floor(latlon / 100) + (latlon % 100) / 60.0
    return round(latlon, 9)


def drefomate(latlon):
    latlon = (latlon - int(latlon)) * 60 + int(latlon) * 100
    return latlon
