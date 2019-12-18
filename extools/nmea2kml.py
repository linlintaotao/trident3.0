#!-*-coding:utf-8 -*-
"""
@desp:
    nmeatokml.py - Converts an NMEA data file to a KML track

    nmeatokml.py < filename.nmea > filename.kml

@file: nmea2kml.py
@date: 12/18/2019
@author: Chey
"""


import os
import sys

from extools import nmeagram

KML_EXT = ".kml"

KML_TEMPLATE = \
"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.0">
<Document>
  <name>NMEA to KML: %s</name>
  <Style id="dwhStyle000">
    <LineStyle id="dwhLineStyleRed6">
      <color>7f0000ff</color>
      <width>6</width>
    </LineStyle>
  </Style>
  <Placemark>
    <name>%s</name>
    <styleUrl>#dwhStyle000</styleUrl>
    <MultiGeometry>
      <LineString>
        <coordinates>
        %s
        </coordinates>
      </LineString>
    </MultiGeometry>
  </Placemark>
</Document>
</kml>
"""


def nmeaFileToCoords(f):
    """Read a file full of NMEA sentences and return a string of lat/lon/z
    coordinates.  'z' is often 0.
    """
    data = []
    for line in f.readlines():
        if line[:6] in ("$GNGGA", "$GNGLL"):
            nmeagram.parseLine(line)
            data.append(str(nmeagram.getField("Longitude")))
            data.append(",")
            data.append(str(nmeagram.getField("Latitude")))
            data.append(",0 ")
    return ''.join(data)


def main():
    # If no args given, assume stdio
    if len(sys.argv) == 1:
        sys.stdout.write(KML_TEMPLATE % ("stdio", "stdio", nmeaFileToCoords(sys.stdin)))

    # If filename is given, use it
    elif len(sys.argv) == 2:

        # The input file should exist
        fn = sys.argv[1]
        assert os.path.exists(fn)

        # Create the KML output file
        fo = open(fn + KML_EXT, 'w')
        fi = open(fn, 'r')
        fo.write(KML_TEMPLATE % (fn, fn, nmeaFileToCoords(fi)))
        fi.close()
        fo.close()

    else:
        sys.stderr.write(__doc__)
        sys.exit(2)


if __name__ == "__main__":
    main()
