#!-*-coding:utf-8 -*-
"""
@desp:
    nmeatokml.py - Converts an NMEA data file to a KML track

    nmeatokml.py < filename.nmea > filename.kml

@file: nmea2kml.py
@date: 12/18/2019
@author: Chey
"""
from extools import nmeagram
from collections import defaultdict, namedtuple

###################################################################
HEADKML1 = """<?xml version="1.0" encoding="UTF-8"?>"""
HEADKML2 = """<kml xmlns="http://earth.google.com/kml/2.2">"""
MARKICNO = """http://earth.google.com/images/kml-icons/track-directional/track-0.png"""


COLMAPKML = {0: "ffc0c0c0", 1: "AF000000", 3: "ffff9600", 2: "AF00FF00", 4: "AFFF0000", 5: "AF0000FF", 6: "AF00FFFF",
             8: "afffffff", 9: "afffffff"}

BRIEFDESP = {'0': "Sorry! invalid solution", '1': "Oops! single point solution", '3': "What the f**k ?",
             '2': "Good! cors data valid at least", '4': "Excellent! fixed solution", '5': "Nice! float solution",
             '6': "Well! Aided solution"}


###################################################################

def genKmlHeader():
    s = ''
    s += f"""{HEADKML1}\n{HEADKML2}\n"""
    s += f"""<Document>\n"""
    for i in range(7):
        s += f"""<Style id="P{i}">\n"""
        s += f"""<IconStyle>\n"""
        s += f"""<color>{COLMAPKML[i]}</color>\n"""
        s += f"""<scale>{0.7}</scale>\n"""
        s += f"""<Icon><href>{MARKICNO}</href></Icon>\n"""
        s += f"""</IconStyle>\n"""
        s += f"""<LabelStyle><scale>0</scale></LabelStyle>"""
        s += f"""<BalloonStyle>
			<bgColor>ffd5f3fa</bgColor>
			<text><![CDATA[<b><font color="#CC0000" size="+3">$[name]</font></b><br>$[description]</font><br/>]]></text>
		    </BalloonStyle>"""
        s += f"""</Style>\n"""

    return s


def genKmlTrack(llh: dict, header: str)->str:
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
        if len(val) == 10:
            s += f"""{val[4]},{val[5]},{0} """
        else:
            s += f"""{val[0]},{val[1]},{0} """

    s += f"""</coordinates>\n"""
    s += f"""</LineString>\n"""
    s += f"""</Placemark>\n"""
    return s


def genKmlPoint(llh: dict, header: str)->str:
    s = ''
    i = 1
    if header == 'GGA':
        for utc, val in llh.items():
            ln = len(val)
            s += f"""<Placemark>\n"""
            s += f"""<name>FMI Point {i}</name>"""
            if ln == 9:
                d = val[-1]
                s += f"""<TimeStamp><when>{d[2:4]}/{d[:2]}/{d[-2:]}T{utc}Z</when></TimeStamp>\n"""
            elif ln == 10:
                d = val[2]
                s += f"""<TimeStamp><when>{d[2:4]}/{d[:2]}/{d[-2:]}T{utc}Z</when></TimeStamp>\n"""
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
                s += f"""
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Time </td><td>{utc}</td><td>Date </td><td>{d[2:4]}/{d[:2]}/{d[-2:]}</td></tr>
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Lat  </td><td>{val[1]}</td><td>Stat </td><td>{val[3]}</td></tr>
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Lon  </td><td>{val[0]}</td><td>nSats</td><td>{val[4]}</td></tr>
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Alt  </td><td>{val[2]}</td><td>dAge </td><td>{val[5]}</td></tr>
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Speed</td><td>{val[-3]*0.514}</td><td>head </td><td>{val[-2]}</td></tr>
                     </table>]]></description>\n"""
            elif ln == 10:
                d = val[2]
                s += f"""
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Time </td><td>{utc}</td><td>Date </td><td>{d[2:4]}/{d[:2]}/{d[-2:]}</td></tr>
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Lat  </td><td>{val[5]}</td><td>Stat </td><td>{val[7]}</td></tr>
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Lon  </td><td>{val[4]}</td><td>nSats</td><td>{val[8]}</td></tr>
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Alt  </td><td>{val[6]}</td><td>dAge </td><td>{val[9]}</td></tr>
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Speed</td><td>{val[0]*0.514}</td><td>head </td><td>{val[1]}</td></tr>
                     </table>]]></description>\n"""
            else:
                s += f"""
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Time </td><td>{utc}</td><td>Date </td><td></td></tr>
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Lat  </td><td>{val[1]}</td><td>Stat </td><td>{val[3]}</td></tr>
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Lon  </td><td>{val[0]}</td><td>nSats</td><td>{val[4]}</td></tr>
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Alt  </td><td>{val[2]}</td><td>dAge </td><td>{val[5]}</td></tr>
                     <tr ALIGN=RIGHT><td ALIGN=LEFT>Speed</td><td></td><td>head </td><td></td></tr>
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
                s += f"""<coordinates>{val[4]},{val[5]},{0}</coordinates>\n"""
            else:
                s += f"""<coordinates>{val[0]},{val[1]},{0}</coordinates>\n"""
            s += f"""</Point>\n"""
            s += f"""</Placemark>\n"""
            i += 1

    if header == 'FMI':
        for utc, val in llh.items():
            s += f"""<Placemark>\n"""
            s += f"""<name>FMI Point {i}</name>"""
            s += f"""<TimeStamp><when>{utc}TZ</when></TimeStamp>\n"""
            s += f"""<Snippet></Snippet>\n"""

            s += f"""<description><![CDATA[{BRIEFDESP[val[3]]}\n<table border=1>
                <tr ALIGN=RIGHT><td ALIGN=LEFT>Time </td><td>{utc}</td><td>     </td><td></td></tr>
                <tr ALIGN=RIGHT><td ALIGN=LEFT>Week </td><td>{val[12]}</td><td>SoW  </td><td>{val[13]}</td></tr>
                <tr ALIGN=RIGHT><td ALIGN=LEFT>Lat  </td><td>{val[1]}</td><td>Stat </td><td>{val[3]}</td></tr>
                <tr ALIGN=RIGHT><td ALIGN=LEFT>Lon  </td><td>{val[0]}</td><td>nSats</td><td>{val[4]}</td></tr>
                <tr ALIGN=RIGHT><td ALIGN=LEFT>Alt  </td><td>{val[2]}</td><td>BaseL</td><td>{val[11]}</td></tr>
                <tr ALIGN=RIGHT><td ALIGN=LEFT>Roll </td><td>{val[5]}</td><td>Vn   </td><td>{val[8]}</td></tr>
                <tr ALIGN=RIGHT><td ALIGN=LEFT>Pitch</td><td>{val[6]}</td><td>Ve   </td><td>{val[9]}</td></tr>
                <tr ALIGN=RIGHT><td ALIGN=LEFT>Yaw  </td><td>{val[7]}</td><td>Vu   </td><td>{val[10]}</td></tr>
                </table>]]></description>\n"""
            s += f"""<styleUrl>#P{int(val[3])}</styleUrl>\n"""
            s += f"""<Style><IconStyle><heading>{val[7]}</heading></IconStyle></Style>\n"""
            s += f"""<Point>\n"""
            s += f"""<coordinates>{val[0]},{val[1]},{0}</coordinates>\n"""
            s += f"""</Point>\n"""
            s += f"""</Placemark>\n"""
            i += 1
    return s


def genKmlRear()->str:
    s = ''
    s += f"""</Document>\n"""
    s += f"""</kml>"""
    return s


def genKmlStr(points, header, hasrmc=False)->str:
    s = genKmlHeader()
    s += genKmlTrack(points, header)
    s += genKmlPoint(points, header)
    s += genKmlRear()
    return s


def nmeaFileToCoords(f, header: str, hasrmc=False)->dict:
    """Read a file full of NMEA sentences and return a string of lat/lon/z
    coordinates.  'z' is often 0.
    """
    data = defaultdict(list)
    for line in f.readlines():
        if header == 'GGA':
            if line.startswith(("$GNGGA", "$GPGGA")):
                nmeagram.parseLine(line)
                utc = nmeagram.getField('UtcTime')
                if utc in data.keys(): # if gga first len = 9 else len = 10
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
                data[utc].append(nmeagram.getField("SpeedOverGround"))
                data[utc].append(nmeagram.getField("CourseOverGround"))
                data[utc].append(nmeagram.getField("Date"))

        elif header == 'FMI':
            if line.startswith(("$GPFMI", "$GPFPD")):
                nmeagram.parseLine(line)
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
    fn = "../NMEA/20191220.txt"
    fo = open(fn + '.kml', 'w')

    fi = open(fn, 'r', encoding='utf-8')
    coords = nmeaFileToCoords(fi, 'GGA')
    kml_str = genKmlStr(coords, 'GGA')

    fo.write(kml_str)
    fi.close()
    fo.close()


if __name__ == "__main__":
    main()
