#!-*-coding:utf-8 -*-
"""
@desp:
    nmeatokml.py - Converts an NMEA data file to a KML track

    nmeatokml.py < filename.nmea > filename.kml

@file: nmea2kml.py
@date: 12/18/2019
@author: Chey
"""
from PyQt5.QtCore import QThread, pyqtSignal

from extools import nmeagram
from datetime import datetime
from collections import defaultdict

###################################################################
HEADKML1 = """<?xml version="1.0" encoding="UTF-8"?>"""
HEADKML2 = """<kml xmlns="http://earth.google.com/kml/2.2">"""
MARKICNO = """http://maps.google.com/mapfiles/kml/shapes/airports.png"""

COLMAPKML = {0: "9fc0c0c0", 1: "9F000000", 3: "9fff9600", 2: "9F00FF00", 4: "FFFFFFFF", 5: "FF0055FF", 6: "FF00FFFF",
             8: "9fffffff", 9: "9fffffff"}

BRIEFDESP = {'0': "Sorry! invalid solution", '1': "Oops! single point solution", '3': "What the f**k ?",
             '2': "Good! cors data valid at least", '4': "Excellent! fixed solution", '5': "Nice! float solution",
             '6': "Well! Aided solution"}


###################################################################

def genKmlHeader():
    s = ''
    s += f"""{HEADKML1}\n{HEADKML2}\n"""
    s += f"""<Document>\n"""
    # s += f"""<Folder id="ID1">
    #         <name>Screen Overlays</name>
    #         <visibility>0</visibility>
    #         <open>0</open>
    # 	    <ScreenOverlay>
    # 		<name>FMI Logo</name>
    # 		<visibility>1</visibility>
    # 		<Icon>
    # 			<href>https://www.bing.com/images/search?view=detailV2&ccid=XOIk2Gql&id=0ABD1AEF24B2D573AEDEC25102030C07AAA4AB74&thid=OIP.XOIk2GqlrR_EcPJauMJ1awAAAA&mediaurl=https%3A%2F%2Fmedia.licdn.com%2Fdms%2Fimage%2FC4D0BAQFmI01aNmGBTw%2Fcompany-logo_200_200%2F0%3Fe%3D2159024400&v=beta&t=yuojs1saVS8rWeqt7wYe-S0DhBQgxkL3fvTlj_J-q-w&exph=200&expw=200&q=Logo+FMI+Engineering&simid=608047655134432105&selectedindex=0&adlt=strict&shtp=GetUrl&shid=18d71d22-3a06-4d20-ae72-262b1b63ae11&shtk=Rk1JIEVuZ2luZWVyaW5nIEJWIHwgTGlua2VkSW4%3D&shdk=Rm91bmQgb24gQmluZyBmcm9tIG5sLmxpbmtlZGluLmNvbQ%3D%3D&shhk=WFV8hGP7qOS9GsBGDpGFZ1kDZNtimElXP0E9BlZEeF8%3D&ensearch=1&form=EX0023&shth=OSH.Z6FutzKfGWzualgTBP6V6Q</href>
    # 		</Icon>
    # 		<overlayXY x="0" y="-1" xunits="fraction" yunits="fraction"/>
    # 		<screenXY x="0" y="0" xunits="fraction" yunits="fraction"/>
    # 		<size x="237.0" y="81.0" xunits="pixels" yunits="pixels"/>
    # 	</ScreenOverlay>
    #     </Folder>"""
    for i in range(7):
        s += f"""<Style id="P{i}">\n"""
        s += f"""<IconStyle>\n"""
        s += f"""<color>{COLMAPKML[i]}</color>\n"""
        s += f"""<scale>{0.4}</scale>\n"""
        s += f"""<Icon><href>{MARKICNO}</href></Icon>\n"""
        s += f"""</IconStyle>\n"""
        s += f"""<LabelStyle><scale>0</scale></LabelStyle>"""
        s += f"""<BalloonStyle>
			<bgColor>ffd5f3fa</bgColor>
			<text><![CDATA[<b><font color="#CC0000" size="+3">$[name]</font></b><br>$[description]</font><br/>]]></text>
		    </BalloonStyle>"""
        s += f"""</Style>\n"""

    return s


def genKmlTrack(llh: dict, header: str) -> str:
    s = ''
    s += f"""<Placemark>\n"""
    s += f"""<name>Rover Track</name>\n"""
    s += f"""<Style>\n"""
    s += f"""<LineStyle>\n"""
    s += f"""<color>{COLMAPKML[2]}</color>\n"""
    s += f"""<width>1.0</width>\n"""
    s += f"""</LineStyle>\n"""
    s += f"""</Style>\n"""
    s += f"""<LineString>\n"""
    s += f"""<coordinates>\n"""

    for utc, val in llh.items():
        val_len = len(val)
        if val_len not in [14, 10, 9, 6]: continue
        if len(val) == 10:
            s += f"""{val[4]},{val[5]},{0} """
        else:
            s += f"""{val[0]},{val[1]},{0} """

    s += f"""</coordinates>\n"""
    s += f"""</LineString>\n"""
    s += f"""</Placemark>\n"""
    return s


def genKmlPoint(llh: dict, header: str) -> str:
    i = 1
    s, tofo, tolo = '', '', ''
    sol = {'0': 0, '1': 0, '2': 0, '4': 0, '5': 0, '6': 0}
    if header == 'GGA':
        for utc, val in llh.items():
            ln = len(val)
            # in-complate nmea info
            if ln not in [6, 9, 10]: continue

            s += f"""<Placemark>\n"""
            s += f"""<name>FMI Point {i}</name>"""
            if ln == 9:
                d = val[-1]
                s += f"""<TimeStamp><when>{d[2:4]}/{d[:2]}/20{d[-2:]}T{utc}Z</when></TimeStamp>\n"""
            elif ln == 10:
                d = val[2]
                s += f"""<TimeStamp><when>{d[2:4]}/{d[:2]}/20{d[-2:]}T{utc}Z</when></TimeStamp>\n"""
            else:
                s += f"""<TimeStamp><when>{utc}TZ</when></TimeStamp>\n"""

            s += f"""<Snippet></Snippet>\n"""

            if ln == 10:
                s += f"""<description><![CDATA[{BRIEFDESP[val[7]]}\n<TABLE border="1" width="100%" 
                            Align="center">\n"""
            else:
                s += f"""<description><![CDATA[FMI Point {i} {BRIEFDESP[val[3]]}\n<TABLE border="1" width="100%" 
                            Align="center">\n"""
            if ln == 9:
                d = val[-1]
                spd = '{:5.2f}'.format(val[-3] * 0.514)
                lat = '{:10.7f}'.format(val[1])
                lon = '{:10.7f}'.format(val[0])
                alt = '{:6.3f}'.format(val[2])
                s += f"""
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Time</td><td>{utc}</td><td ALIGN=LEFT>Date</td><td>{d[2:4]}/{d[:2]}/{d[-2:]}</td></tr>
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Lat</td><td>{lat}</td><td ALIGN=LEFT>Stat</td><td>{val[3]}</td></tr>
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Lon</td><td>{lon}</td><td ALIGN=LEFT>nSats</td><td>{val[4]}</td></tr>
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Alt</td><td>{alt}</td><td ALIGN=LEFT>dAge</td><td>{val[5]}</td></tr>
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Speed</td><td>{spd}</td><td ALIGN=LEFT>heading</td><td>{val[-2]}</td></tr>
                     </table>]]></description>\n"""
            elif ln == 10:
                d = val[2]
                spd = '{:5.2f}'.format(val[0] * 0.514)
                lat = '{:10.7f}'.format(val[5])
                lon = '{:10.7f}'.format(val[4])
                alt = '{:6.3f}'.format(val[6])
                s += f"""
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Time</td><td>{utc}</td><td ALIGN=LEFT>Date</td><td>{d[2:4]}/{d[:2]}/20{d[-2:]}</td></tr>
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Lat</td><td>{lat}</td><td ALIGN=LEFT>Stat</td><td>{val[7]}</td></tr>
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Lon</td><td>{lon}</td><td ALIGN=LEFT>nSats</td><td>{val[8]}</td></tr>
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Alt</td><td>{alt}</td><td ALIGN=LEFT>dAge</td><td>{val[9]}</td></tr>
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Speed</td><td>{spd}</td><td ALIGN=LEFT>heading</td><td>{val[1]}</td></tr>
                     </table>]]></description>\n"""
            else:
                lat = '{:10.7f}'.format(val[1])
                lon = '{:10.7f}'.format(val[0])
                alt = '{:6.3f}'.format(val[2])
                s += f"""
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Time</td><td>{utc}</td><td ALIGN=LEFT>Date</td><td></td></tr>
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Lat</td><td>{lat}</td><td ALIGN=LEFT>Stat</td><td>{val[3]}</td></tr>
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Lon</td><td>{lon}</td><td ALIGN=LEFT>nSats</td><td>{val[4]}</td></tr>
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Alt</td><td>{alt}</td><td ALIGN=LEFT>dAge</td><td>{val[5]}</td></tr>
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Speed</td><td></td><td ALIGN=LEFT>heading</td><td></td></tr>
                     </table>]]></description>\n"""

            if ln == 10:
                s += f"""<styleUrl>#P{int(val[7])}</styleUrl>\n"""
            else:
                s += f"""<styleUrl>#P{int(val[3])}</styleUrl>\n"""

            if ln == 9:
                s += f"""<Style><IconStyle><heading>{val[-2]}</heading></IconStyle></Style>\n"""
            elif ln == 10:
                s += f"""<Style><IconStyle><heading>{val[1]}</heading></IconStyle></Style>\n"""
            else:
                s += f"""<Style><IconStyle><heading>0</heading></IconStyle></Style>\n"""
            s += f"""<Point>\n"""

            if ln == 10:
                stat = val[7]
                s += f"""<coordinates>{val[4]},{val[5]},{0}</coordinates>\n"""
            else:
                stat = val[3]
                s += f"""<coordinates>{val[0]},{val[1]},{0}</coordinates>\n"""
            s += f"""</Point>\n"""
            s += f"""</Placemark>\n"""
            # nmea info statistics
            if i == 1:
                tofo = utc
            tolo = utc
            sol[stat] += 1
            i += 1

    if header == 'FMI':
        for utc, val in llh.items():
            if len(val) != 14: continue
            s += f"""<Placemark>\n"""
            s += f"""<name>FMI Point {i}</name>"""
            s += f"""<TimeStamp><when>{utc}TZ</when></TimeStamp>\n"""
            s += f"""<Snippet></Snippet>\n"""

            s += f"""<description><![CDATA[{BRIEFDESP[val[3]]}\n<table border=1>
                <tr ALIGN=RIGHT><td ALIGN=LEFT>Time(UTC)</td><td>{utc}</td><td ALIGN=LEFT></td><td></td></tr>
                <tr ALIGN=RIGHT><td ALIGN=LEFT>Week</td><td>{val[12]}</td><td ALIGN=LEFT>SoW(s)</td><td>{val[13]}</td></tr>
                <tr ALIGN=RIGHT><td ALIGN=LEFT>Lat(deg)</td><td>{val[1]}</td><td ALIGN=LEFT>Stat</td><td>{val[3]}</td></tr>
                <tr ALIGN=RIGHT><td ALIGN=LEFT>Lon(deg)</td><td>{val[0]}</td><td ALIGN=LEFT>nSats</td><td>{val[4]}</td></tr>
                <tr ALIGN=RIGHT><td ALIGN=LEFT>Alt(m)</td><td>{val[2]}</td><td ALIGN=LEFT>BaseL(m)</td><td>{val[11]}</td></tr>
                <tr ALIGN=RIGHT><td ALIGN=LEFT>Roll(deg)</td><td>{val[5]}</td><td ALIGN=LEFT>Vn(m/s)</td><td>{val[8]}</td></tr>
                <tr ALIGN=RIGHT><td ALIGN=LEFT>Pitch(deg)</td><td>{val[6]}</td><td ALIGN=LEFT>Ve(m/s)</td><td>{val[9]}</td></tr>
                <tr ALIGN=RIGHT><td ALIGN=LEFT>Yaw(deg)</td><td>{val[7]}</td><td ALIGN=LEFT>Vu(m/s)</td><td>{val[10]}</td></tr>
                </table>]]></description>\n"""
            s += f"""<styleUrl>#P{int(val[3])}</styleUrl>\n"""
            s += f"""<Style><IconStyle><heading>{val[7]}</heading></IconStyle></Style>\n"""
            s += f"""<Point>\n"""
            s += f"""<coordinates>{val[0]},{val[1]},{0}</coordinates>\n"""
            s += f"""</Point>\n"""
            s += f"""</Placemark>\n"""
            # nmea info statistics
            if i == 1:
                tofo = utc
            tolo = utc
            sol[val[3]] += 1
            i += 1
    if i > 1:
        spp_ratio = "{:4.1f}".format(100 * sol['1'] / (i - 1))
        dgps_ratio = "{:4.1f}".format(100 * sol['2'] / (i - 1))
        fix_ratio = "{:4.1f}".format(100 * sol['4'] / (i - 1))
        float_ratio = "{:4.1f}".format(100 * sol['5'] / (i - 1))
        dr_ratio = "{:4.1f}".format(100 * sol['6'] / (i - 1))
        if header == 'GGA':
            stofo = tofo[:2] + ':' + tofo[2:4] + ':' + tofo[4:]
            stolo = tolo[:2] + ':' + tolo[2:4] + ':' + tolo[4:]
            ts = datetime.strptime(tolo, '%H%M%S.%f') - datetime.strptime(tofo, '%H%M%S.%f')
        else:
            tofo_list = tofo.split()
            tolo_list = tolo.split()
            stofo = tofo_list[0] + ' ' + tofo_list[1][:2] + ':' + tofo_list[1][2:4] + ':' + tofo_list[1][4:]
            stolo = tolo_list[0] + ' ' + tolo_list[1][:2] + ':' + tolo_list[1][2:4] + ':' + tolo_list[1][4:]
            ts = datetime.strptime(tolo, '%m/%d/%Y %H%M%S.%f') - datetime.strptime(tofo, '%m/%d/%Y %H%M%S.%f')

        info = f"Total points: {i - 1}\n" \
               f"Time(UTC): {stofo} - {stolo}, duration {ts} \n" \
               f"Solution state: SPP {sol['1']}({spp_ratio}%), DGPS {sol['2']}({dgps_ratio}%)\n" \
               f"FIX {sol['4']}({fix_ratio}%), FLOAT {sol['5']}({float_ratio}%), DR {sol['6']}({dr_ratio}%)"

    return s, info


def genKmlRear() -> str:
    s = ''
    s += f"""</Document>\n"""
    s += f"""</kml>"""
    return s


def genKmlStr(points, header) -> str:
    s = genKmlHeader()
    try:
        s += genKmlTrack(points, header)
        kml, info = genKmlPoint(points, header)
    except Exception as e:
        print(f'generate kml error {e}')
    s += kml
    s += genKmlRear()
    return s, info


def nmeaFileToCoords(f, header: str) -> dict:
    """Read a file full of NMEA sentences and return a string of lat/lon/z
    coordinates.  'z' is often 0.
    """
    data = defaultdict(list)
    for line in f.readlines():
        if header == 'GGA':
            # TODO find GGA string in mixed line strings
            if line.startswith(("$GNGGA", "$GPGGA")):
                nmeagram.parseLine(line)
                if int(nmeagram.getField("Longitude")) == 0 or int(nmeagram.getField("Latitude")) == 0 or int(
                        nmeagram.getField("PositionFix")) == 0:
                    continue
                utc = nmeagram.getField('UtcTime')
                if utc in data.keys():  # if gga first len = 9 else len = 10(rmc first)
                    data[utc].append(True)
                data[utc].append(nmeagram.getField("Longitude"))
                data[utc].append(nmeagram.getField("Latitude"))
                data[utc].append(nmeagram.getField("MslAltitude"))
                data[utc].append(nmeagram.getField("PositionFix"))
                data[utc].append(nmeagram.getField("SatellitesUsed"))
                data[utc].append(nmeagram.getField("AgeOfDiffCorr"))
            elif line.startswith(("$GNRMC", "$GPRMC")):
                nmeagram.parseLine(line)
                utc = nmeagram.getField('UtcTime')
                if int(nmeagram.getField("Longitude")) == 0 or int(nmeagram.getField("Latitude")) == 0:
                    continue
                data[utc].append(nmeagram.getField("SpeedOverGround"))
                data[utc].append(nmeagram.getField("CourseOverGround"))
                data[utc].append(nmeagram.getField("Date"))

        elif header == 'FMI':
            vidx = line.find("$GPFMI")
            if vidx == -1:
                vidx = line.find("$GPFPD")
            if vidx != -1:
                line = line[vidx:]

            if line.startswith(("$GPFMI", "$GPFPD")):
                nmeagram.parseLine(line)
                if int(nmeagram.getField("Longitude")) == 0 or int(nmeagram.getField("Latitude")) == 0 or int(
                        nmeagram.getField("PositionFix")) == 0:
                    continue
                utc = nmeagram.getField('UtcTime')
                data[utc].append(nmeagram.getField("Longitude"))
                data[utc].append(nmeagram.getField("Latitude"))
                data[utc].append(nmeagram.getField("MslAltitude"))
                data[utc].append(nmeagram.getField("PositionFix"))
                data[utc].append(nmeagram.getField("SatellitesUsed"))
                data[utc].append(nmeagram.getField("roll"))
                data[utc].append(nmeagram.getField("pitch"))
                data[utc].append(nmeagram.getField("yaw"))
                data[utc].append(nmeagram.getField("vn"))
                data[utc].append(nmeagram.getField("ve"))
                data[utc].append(nmeagram.getField("vu"))
                data[utc].append(nmeagram.getField("bl"))
                data[utc].append(nmeagram.getField("week"))
                data[utc].append(nmeagram.getField("sow"))
    return data


def nmeaFileTodev(f):
    """Read a file full of NMEA sentences and return a string of lat/lon/z
    coordinates.  'z' is often 0.
    """
    data = []
    data_append = data.append
    for line in f.readlines():
        if line[:6] in ("$GNGGA", "$GPGGA"):
            nmeagram.parseLine(line)
            data_append(nmeagram.getField("Latitude"))
            data_append(nmeagram.getField("Longitude"))
            data_append(nmeagram.getField("SatellitesUsed"))

    return data


def main():
    fn = "../NMEA/COM3_20200723_175744.nmea"
    fo = open(fn + '.kml', 'w')

    fi = open(fn, 'r', encoding='utf-8')
    coords = nmeaFileToCoords(fi, 'GGA')
    kml_str, info = genKmlStr(coords, 'GGA')

    fo.write(kml_str)
    fi.close()
    fo.close()


class KmlParse(QThread):
    singal = pyqtSignal(str)

    def __init__(self, fileName, header='GGA'):
        super().__init__()
        self.fn = fileName
        self.head = header

    def run(self):
        info = None
        try:
            fnkml = self.fn + '.kml'
            fnkmz = self.fn + '.kmz'
            fo = open(fnkml, 'w')
            with open(self.fn, 'r', encoding='utf-8') as f:
                coords = nmeaFileToCoords(f, self.head)
                kml_str, info = genKmlStr(coords, self.head)
                fo.write(kml_str)
                fo.flush()
                fo.close()
            from os import remove
            from zipfile import ZipFile, ZIP_DEFLATED
            with ZipFile(fnkmz, 'w', compression=ZIP_DEFLATED) as kmz:
                kmz.write(fnkml)
            remove(fnkml)
        except Exception as e:
            print(e)
        self.singal.emit(info)


if __name__ == "__main__":
    main()
