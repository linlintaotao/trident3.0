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

###################################################################
HEADKML1 = """<?xml version="1.0" encoding="UTF-8"?>"""
HEADKML2 = """<kml xmlns="http://www.opengis.net/kml/2.2">"""
MARKICNO = """http://maps.google.com/mapfiles/kml/pal5/icon13.png"""

START = """http://maps.google.com/mapfiles/kml/paddle/S.png"""
END = """http://maps.google.com/mapfiles/kml/paddle/E.png"""

COLMAPKML = {0: "ff000000", 1: "ff000000", 3: "ff800080", 2: "ff00ff00", 4: "ffff0000", 5: "ff0000ff", 6: "ff00ffff",
             8: "ffffffff", 9: "ffffffff"}

BRIEFDESP = {'0': "Sorry! invalid solution", '1': "Oops! single point solution", '3': "What the f**k ?",
             '2': "Good! cors data valid at least", '4': "Excellent! fixed solution", '5': "Nice! float solution",
             '6': "Well! Aided solution"}


###################################################################

def genKmlHeader ():
    s = ''
    s += f"""{HEADKML1}\n{HEADKML2}\n"""
    s += f"""<Document>\n"""
    for i in range (7):
        s += f"""<Style id="P{i}">\n"""
        s += f"""  <IconStyle>\n"""
        s += f"""    <color>{COLMAPKML[i]}</color>\n"""
        s += f"""    <scale>{0.5}</scale>\n"""
        s += f"""    <Icon><href>{MARKICNO}</href></Icon>\n"""
        s += f"""  </IconStyle>\n"""
        s += f"""</Style>\n"""
    s += f"""<Style id="P{8}">\n"""
    s += f"""  <IconStyle>\n"""
    s += f"""    <color>{COLMAPKML[8]}</color>\n"""
    s += f"""    <scale>{1.5}</scale>\n"""
    s += f"""    <Icon><href>{START}</href></Icon>\n"""
    s += f"""  </IconStyle>\n"""
    s += f"""</Style>\n"""

    s += f"""<Style id="P{9}">\n"""
    s += f"""  <IconStyle>\n"""
    s += f"""    <color>{COLMAPKML[9]}</color>\n"""
    s += f"""    <scale>{1.5}</scale>\n"""
    s += f"""    <Icon><href>{END}</href></Icon>\n"""
    s += f"""  </IconStyle>\n"""
    s += f"""</Style>\n"""

    return s


def genKmlTrack (llh, header):
    s = ''
    s += f"""<Placemark>\n"""
    s += f"""<name>Rover Track</name>\n"""
    s += f"""<Style>\n"""
    s += f"""<LineStyle>\n"""
    s += f"""<color>{COLMAPKML[2]}</color>\n"""
    s += f"""<width>1.2</width>\n"""
    s += f"""</LineStyle>\n"""
    s += f"""</Style>\n"""
    s += f"""<LineString>\n"""
    s += f"""<coordinates>\n"""

    if header == 'GGA':
        data_len = len (llh) // 7
        for i in range (data_len):
            s += f"""{llh[i * 7]},{llh[i * 7 + 1]},{0} """
    if header == 'FMI':
        data_len = len (llh) // 13
        for i in range (data_len):
            s += f"""{llh[i * 13]},{llh[i * 13 + 1]},{0} """
    s += f"""</coordinates>\n"""
    s += f"""</LineString>\n"""
    s += f"""</Placemark>\n"""
    return s


def genKmlPoint (llh, header):
    if header == 'GGA':
        s = ''
        data_len = len (llh) // 7
        i = 0
        s += f"""<Placemark>\n"""
        s += f"""<description><![CDATA[Point #{i}, {BRIEFDESP[llh[i * 7 + 4]]}\n<table border=1>
            <tr><td>Time </td><td>{llh[i * 7 + 3]}</td><td>     </td><td></td></tr>
            <tr><td>Lat  </td><td>{llh[i * 7 + 1]}</td><td>Stat </td><td>{llh[i * 7 + 4]}</td></tr>
            <tr><td>Lon  </td><td>{llh[i * 7]}    </td><td>nSats</td><td>{llh[i * 7 + 5]}</td></tr>
            <tr><td>Alt  </td><td>{llh[i * 7 + 2]}</td><td>dAge </td><td>{llh[i * 7 + 6]}</td></tr>
            </table>]]></description>\n"""
        s += f"""<styleUrl>#P{8}</styleUrl>\n"""
        s += f"""<Point>\n"""
        s += f"""<coordinates>{llh[i * 7]},{llh[i * 7 + 1]},{0}</coordinates>\n"""
        s += f"""</Point>\n"""
        s += f"""</Placemark>\n"""

        for i in range (1, data_len - 1):
            s += f"""<Placemark>\n"""
            s += f"""<description><![CDATA[Point #{i}, {BRIEFDESP[llh[i * 7 + 4]]}\n<table border=1>
                <tr><td>Time </td><td>{llh[i * 7 + 3]}</td><td>     </td><td></td></tr>
                <tr><td>Lat  </td><td>{llh[i * 7 + 1]}</td><td>Stat </td><td>{llh[i * 7 + 4]}</td></tr>
                <tr><td>Lon  </td><td>{llh[i * 7]}    </td><td>nSats</td><td>{llh[i * 7 + 5]}</td></tr>
                <tr><td>Alt  </td><td>{llh[i * 7 + 2]}</td><td>dAge </td><td>{llh[i * 7 + 6]}</td></tr>
                </table>]]></description>\n"""
            s += f"""<styleUrl>#P{int (llh[i * 7 + 4])}</styleUrl>\n"""
            s += f"""<Point>\n"""
            s += f"""<coordinates>{llh[i * 7]},{llh[i * 7 + 1]},{0}</coordinates>\n"""
            s += f"""</Point>\n"""
            s += f"""</Placemark>\n"""

        i = data_len - 1
        s += f"""<Placemark>\n"""
        s += f"""<description><![CDATA[Point #{i}, {BRIEFDESP[llh[i * 7 + 4]]}\n<table border=1>
            <tr><td>Time </td><td>{llh[i * 7 + 3]}</td><td>     </td><td></td></tr>
            <tr><td>Lat  </td><td>{llh[i * 7 + 1]}</td><td>Stat </td><td>{llh[i * 7 + 4]}</td></tr>
            <tr><td>Lon  </td><td>{llh[i * 7]}    </td><td>nSats</td><td>{llh[i * 7 + 5]}</td></tr>
            <tr><td>Alt  </td><td>{llh[i * 7 + 2]}</td><td>dAge </td><td>{llh[i * 7 + 6]}</td></tr>
            </table>]]></description>\n"""
        s += f"""<styleUrl>#P{9}</styleUrl>\n"""
        s += f"""<Point>\n"""
        s += f"""<coordinates>{llh[i * 7]},{llh[i * 7 + 1]},{0}</coordinates>\n"""
        s += f"""</Point>\n"""
        s += f"""</Placemark>\n"""
    if header == 'FMI':
        s = ''
        data_len = len (llh) // 13
        i = 0
        s += f"""<Placemark>\n"""
        s += f"""<description><![CDATA[Point #{i}, {BRIEFDESP[llh[i * 13 + 4]]}\n<table border=1>
            <tr><td>Time </td><td>{llh[i * 13 + 3]}</td><td>     </td><td></td></tr>
            <tr><td>Lat  </td><td>{llh[i * 13 + 1]}</td><td>Stat </td><td>{llh[i * 13 + 4]}</td></tr>
            <tr><td>Lon  </td><td>{llh[i * 13]}    </td><td>nSats</td><td>{llh[i * 13 + 5]}</td></tr>
            <tr><td>Alt  </td><td>{llh[i * 13 + 2]}</td><td>Bl   </td><td>{llh[i * 13 + 12]}</td></tr>
            <tr><td>Roll </td><td>{llh[i * 13 + 6]}</td><td>Vn   </td><td>{llh[i * 13 + 9]}</td></tr>
            <tr><td>Pitch</td><td>{llh[i * 13 + 7]}</td><td>Ve   </td><td>{llh[i * 13 + 10]}</td></tr>
            <tr><td>Yaw  </td><td>{llh[i * 13 + 8]}</td><td>Vu   </td><td>{llh[i * 13 + 11]}</td></tr>
            </table>]]></description>\n"""
        s += f"""<styleUrl>#P{8}</styleUrl>\n"""
        s += f"""<Point>\n"""
        s += f"""<coordinates>{llh[i * 13]},{llh[i * 13 + 1]},{0}</coordinates>\n"""
        s += f"""</Point>\n"""
        s += f"""</Placemark>\n"""

        for i in range (1, data_len - 1):
            s += f"""<Placemark>\n"""
            s += f"""<description><![CDATA[Point #{i}, {BRIEFDESP[llh[i * 13 + 4]]}\n<table border=1>
                <tr><td>Time </td><td>{llh[i * 13 + 3]}</td><td>     </td><td></td></tr>
                <tr><td>Lat  </td><td>{llh[i * 13 + 1]}</td><td>Stat </td><td>{llh[i * 13 + 4]}</td></tr>
                <tr><td>Lon  </td><td>{llh[i * 13]}    </td><td>nSats</td><td>{llh[i * 13 + 5]}</td></tr>
                <tr><td>Alt  </td><td>{llh[i * 13 + 2]}</td><td>Bl   </td><td>{llh[i * 13 + 12]}</td></tr>
                <tr><td>Roll </td><td>{llh[i * 13 + 6]}</td><td>Vn   </td><td>{llh[i * 13 + 9]}</td></tr>
                <tr><td>Pitch</td><td>{llh[i * 13 + 7]}</td><td>Ve   </td><td>{llh[i * 13 + 10]}</td></tr>
                <tr><td>Yaw  </td><td>{llh[i * 13 + 8]}</td><td>Vu   </td><td>{llh[i * 13 + 11]}</td></tr>
                </table>]]></description>\n"""
            s += f"""<styleUrl>#P{int (llh[i * 13 + 4])}</styleUrl>\n"""
            s += f"""<Point>\n"""
            s += f"""<coordinates>{llh[i * 13]},{llh[i * 13 + 1]},{0}</coordinates>\n"""
            s += f"""</Point>\n"""
            s += f"""</Placemark>\n"""

        i = data_len - 1
        s += f"""<Placemark>\n"""
        s += f"""<description><![CDATA[Point #{i}, {BRIEFDESP[llh[i * 13 + 4]]}\n<table border=1>
            <tr><td>Time </td><td>{llh[i * 13 + 3]}</td><td>     </td><td></td></tr>
            <tr><td>Lat  </td><td>{llh[i * 13 + 1]}</td><td>Stat </td><td>{llh[i * 13 + 4]}</td></tr>
            <tr><td>Lon  </td><td>{llh[i * 13]}    </td><td>nSats</td><td>{llh[i * 13 + 5]}</td></tr>
            <tr><td>Alt  </td><td>{llh[i * 13 + 2]}</td><td>Bl   </td><td>{llh[i * 13 + 12]}</td></tr>
            <tr><td>Roll </td><td>{llh[i * 13 + 6]}</td><td>Vn   </td><td>{llh[i * 13 + 9]}</td></tr>
            <tr><td>Pitch</td><td>{llh[i * 13 + 7]}</td><td>Ve   </td><td>{llh[i * 13 + 10]}</td></tr>
            <tr><td>Yaw  </td><td>{llh[i * 13 + 8]}</td><td>Vu   </td><td>{llh[i * 13 + 11]}</td></tr>
            </table>]]></description>\n"""
        s += f"""<styleUrl>#P{9}</styleUrl>\n"""
        s += f"""<Point>\n"""
        s += f"""<coordinates>{llh[i * 13]},{llh[i * 13 + 1]},{0}</coordinates>\n"""
        s += f"""</Point>\n"""
        s += f"""</Placemark>\n"""
    return s


def genKmlRear ():
    s = ''
    s += f"""</Document>\n"""
    s += f"""</kml>"""
    return s


def genKmlStr (points, header):
    s = genKmlHeader ()
    s += genKmlTrack (points, header)
    s += genKmlPoint (points, header)
    s += genKmlRear ()
    return s


def nmeaFileToCoords (f, header):
    """Read a file full of NMEA sentences and return a string of lat/lon/z
    coordinates.  'z' is often 0.
    """
    data = []
    data_append = data.append
    for line in f.readlines ():
        if header == 'GGA':
            if line.startswith(("$GNGGA", "$GPGGA")):
                nmeagram.parseLine (line)
                data_append (nmeagram.getField ("Longitude"))
                data_append (nmeagram.getField ("Latitude"))
                data_append (nmeagram.getField ("MslAltitude"))
                data_append (nmeagram.getField ("UtcTime"))
                data_append (nmeagram.getField ("PositionFix"))
                data_append (nmeagram.getField ("SatellitesUsed"))
                data_append (nmeagram.getField ("AgeOfDiffCorr"))
        elif header == 'FMI':
            if line.startswith("$GPFMI"):
                nmeagram.parseLine (line)
                data_append (nmeagram.getField ("Longitude"))
                data_append (nmeagram.getField ("Latitude"))
                data_append (nmeagram.getField ("MslAltitude"))
                data_append (nmeagram.getField ("UtcTime"))
                data_append (nmeagram.getField ("PositionFix"))
                data_append (nmeagram.getField ("SatellitesUsed"))
                data_append (nmeagram.getField ("roll"))
                data_append (nmeagram.getField ("pitch"))
                data_append (nmeagram.getField ("yaw"))
                data_append (nmeagram.getField ("vn"))
                data_append (nmeagram.getField ("ve"))
                data_append (nmeagram.getField ("vu"))
                data_append (nmeagram.getField ("bl"))

    return data


def nmeaFileTodev (f):
    """Read a file full of NMEA sentences and return a string of lat/lon/z
    coordinates.  'z' is often 0.
    """
    data = []
    data_append = data.append
    for line in f.readlines ():
        if line[:6] in ("$GNGGA", "$GPGGA"):
            nmeagram.parseLine (line)
            data_append (nmeagram.getField ("Latitude"))
            data_append (nmeagram.getField ("Longitude"))
            data_append (nmeagram.getField ("SatellitesUsed"))

    return data


def main ():
    fn = "../NMEA/20191220.txt"
    fo = open (fn + '.kml', 'w')

    fi = open (fn, 'r', encoding='utf-8')
    coords = nmeaFileToCoords (fi)
    kml_str = genKmlStr (coords)

    fo.write (kml_str)
    fi.close ()
    fo.close ()


if __name__ == "__main__":
    main ()
