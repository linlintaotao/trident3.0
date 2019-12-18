#!-*-coding:utf-8 -*-
"""
@desp:
@file: nmeagram.py
@date: 12/18/2019
@author: Chey
"""


# This dict holds the global parsed data
data = {}

def toDecimalDegrees(ddmm):
    """
    Converts a string from ddmm.mmmm or dddmm.mmmm format
    to a float in dd.dddddd format
    """
    if not isinstance(ddmm, str):
        raise("A string type expected")
    splitat = ddmm.find('.') - 2
    return _float(ddmm[:splitat]) + _float(ddmm[splitat:]) / 60.0


def _float(s):
    """
    Returns the float value of string s if it exists,
    or None if s is an empty string.
    """
    if s:
        return float(s)
    else:
        return None


def _int(s):
    """
    Returns the int value of string s if it exists,
    or None if s is an empty string.
    """
    if s:
        return int(s)
    else:
        return None


def calcCheckSum(line):
    """
    Returns the checksum as a one byte integer value.
    In this case the checksum is the XOR of everything after '$' and before '*'.
    """
    s = 0
    for c in line[1:-3]:
        s = s ^ ord(c)
    return s


def parseGGA(fields):
    """
    Parses the Global Positioning System Fix Data sentence fields.
    Stores the results in the global data dict.
    """

    # GGA has 15 fields
    assert len(fields) == 15

    # MsgId = fields[0]
    data['UtcTime'] = fields[1]
    data['Latitude'] = toDecimalDegrees(fields[2])
    data['NsIndicator'] = fields[3]
    data['Longitude'] = toDecimalDegrees(fields[4])
    data['EwIndicator'] = fields[5]
    data['PositionFix'] = fields[6]
    data['SatellitesUsed'] = _int(fields[7])
    data['HorizontalDilutionOfPrecision'] = _float(fields[8])
    data['MslAltitude'] = _float(fields[9])
    data['MslAltitudeUnits'] = fields[10]
    data['GeoidSeparation'] = _float(fields[11])
    data['GeoidSeparationUnits'] = fields[12]
    data['AgeOfDiffCorr'] = _float(fields[13])
    data['DiffRefStationId'] = fields[14]

    # Attend to lat/lon plus/minus signs
    if data['NsIndicator'] == 'S':
        data['Latitude'] *= -1.0
    if data['EwIndicator'] == 'W':
        data['Longitude'] *= -1.0


def parseGLL(fields):
    """
    Parses the Geographic Position-Latitude/Longitude sentence fields.
    Stores the results in the global data dict.
    """

    # GLL has 8 fields
    assert len(fields) == 7

    # MsgId = fields[0]
    data['Latitude'] = toDecimalDegrees(fields[1])
    data['NsIndicator'] = fields[2]
    data['Longitude'] = toDecimalDegrees(fields[3])
    data['EwIndicator'] = fields[4]
    data['UtcTime'] = fields[5]
    data['GllStatus'] = fields[6]

    # Attend to lat/lon plus/minus signs
    if data['NsIndicator'] == 'S':
        data['Latitude'] *= -1.0
    if data['EwIndicator'] == 'W':
        data['Longitude'] *= -1.0


def parseGSA(fields):
    """
    Parses the GNSS DOP and Active Satellites sentence fields.
    Stores the results in the global data dict.
    """

    # GSA has 18 fields
    assert len(fields) == 18

    # MsgId = fields[0]
    data['Mode1'] = fields[1]
    data['Mode2'] = _int(fields[2])
    data['SatCh1'] = _int(fields[3])
    data['SatCh2'] = _int(fields[4])
    data['SatCh3'] = _int(fields[5])
    data['SatCh4'] = _int(fields[6])
    data['SatCh5'] = _int(fields[7])
    data['SatCh6'] = _int(fields[8])
    data['SatCh7'] = _int(fields[9])
    data['SatCh8'] = _int(fields[10])
    data['SatCh9'] = _int(fields[11])
    data['SatCh10'] = _int(fields[12])
    data['SatCh11'] = _int(fields[13])
    data['SatCh12'] = _int(fields[14])
    data['PDOP'] = _float(fields[15])
    data['HDOP'] = _float(fields[16])
    data['VDOP'] = _float(fields[17])


def parseGSV(fields):
    """
    Parses the GNSS Satellites in View sentence fields.
    Stores the results in the global data dict.
    """

    # GSV has a variable number of fields
    numfields = len(fields)
    assert numfields in (8, 12, 16, 20)

    # MsgId = fields[0]
    data['NumMsgs'] = _int(fields[1])
    data['MsgNum'] = _int(fields[2])
    data['SatsInView'] = fields[3]

    # Create struct (only needed first time this is called)
    if 'SatelliteId' not in data.keys():
        data['SatelliteId'] = {}
        data['Elevation'] = {}
        data['Azimuth'] = {}
        data['Snr'] = {}

    # Calculate index offset
    nn = 0
    n = 4 * (int(fields[2]) - 1)

    data['SatelliteId'][n] = _int(fields[4])
    data['Elevation'][n] = _int(fields[5])
    data['Azimuth'][n] = _int(fields[6])
    data['Snr'][n] = _int(fields[7])

    if numfields >= 12:
        nn = n + 1
        data['SatelliteId'][nn] = _int(fields[8])
        data['Elevation'][nn] = _int(fields[9])
        data['Azimuth'][nn] = _int(fields[10])
        data['Snr'][nn] = _int(fields[11])

    if numfields >= 16:
        nn = n + 2
        data['SatelliteId'][nn] = _int(fields[12])
        data['Elevation'][nn] = _int(fields[13])
        data['Azimuth'][nn] = _int(fields[14])
        data['Snr'][nn] = _int(fields[15])

    if numfields == 20:
        nn = n + 3
        data['SatelliteId'][nn] = _int(fields[16])
        data['Elevation'][nn] = _int(fields[17])
        data['Azimuth'][nn] = _int(fields[18])
        data['Snr'][nn] = _int(fields[19])

    # If this is the last GSV sentence in this series,
    # erase old fields when fewer satellites are received than last series
    if fields[1] == fields[2]:
        while nn < len(data['SatelliteId']):
            del data['SatelliteId'][nn]
            del data['Elevation'][nn]
            del data['Azimuth'][nn]
            del data['Snr'][nn]
            nn += 1


def parseRMC(fields):
    """
    Parses the Recommended Minimum Specific GNSS Data sentence fields.
    Stores the results in the global data dict.

    WARNING: This parsing is based on an actual SiRFstar III RMC sentence
    which differs from SiRF's NMEA manual revision 1.3 (Jan. 2005).
    The actual data has one extra empty field after Magnetic Variation.
    """

    # RMC has 13 fields
    assert len(fields) == 13

    # MsgId = fields[0]
    data['UtcTime'] = fields[1]
    data['RmcStatus'] = fields[2]
    data['Latitude'] = toDecimalDegrees(fields[3])
    data['NsIndicator'] = fields[4]
    data['Longitude'] = toDecimalDegrees(fields[5])
    data['EwIndicator'] = fields[6]
    data['SpeedOverGround'] = _float(fields[7])
    data['CourseOverGround'] = _float(fields[8])
    data['Date'] = fields[9]
    data['MagneticVariation'] = fields[10]
    data['UnknownEmptyField'] = fields[11]
    data['RmcMode'] = fields[12]

    # Attend to lat/lon plus/minus signs
    if data['NsIndicator'] == 'S':
        data['Latitude'] *= -1.0
    if data['EwIndicator'] == 'W':
        data['Longitude'] *= -1.0


def parseVTG(fields):
    """
    Parses the Course Over Ground and Ground Speed sentence fields.
    Stores the results in the global data dict.
    """

    # VTG has 10 fields
    assert len(fields) == 10

    # MsgId = fields[0]
    data['Course0'] = _float(fields[1])
    data['Reference0'] = fields[2]
    data['Course1'] = _float(fields[3])
    data['Reference1'] = fields[4]
    data['Speed0'] = _float(fields[5])
    data['Units0'] = fields[6]
    data['Speed1'] = _float(fields[7])
    data['Units1'] = fields[8]
    data['VtgMode'] = fields[9]


def parseLine(line):
    """
    Parses an NMEA sentence, sets fields in the global structure.
    Raises an AssertionError if the checksum does not validate.
    Returns the type of sentence that was parsed.
    """

    # Get rid of the \r\n if it exists
    line = line.rstrip()

    # Validate the sentence using the checksum
    assert calcCheckSum(line) == int(line[-2:], 16)

    # Pick the proper parsing function
    parseFunc = {
        "$GNGGA": parseGGA,
        "$GNGLL": parseGLL,
        "$GNGSA": parseGSA,
        "$GNGSV": parseGSV,
        "$GNRMC": parseRMC,
        "$GNVTG": parseVTG,
        }[line[:6]]

    # Call the parser with fields split and the tail chars removed.
    # The characters removed are the asterisk, the checksum (2 bytes) and \n\r.
    parseFunc(line[-3].split(','))
    # Return the type of sentence that was parsed
    return line[3:6]


def getField(fieldname):
    """
    Returns the value of the named field.
    """
    return data[fieldname]
