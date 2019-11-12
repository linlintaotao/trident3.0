#!-*-coding:utf-8 -*-
"""
@desp:
    This is heavily based on the NtripPerlClient program written by BKG.
    Then heavily based on a unavco original.
@file: NtripClient.py
@date: 11/11/2019
@author: Chey
"""

import socket
import sys
from queue import Queue
from time import sleep
from base64 import b64encode
from datetime import datetime, timedelta
from optparse import OptionParser

version = 0.2
useragent = "NTRIP FMIPythonClient/%.1f" % version
highVer = True if sys.version_info.major >= 3 else False
# reconnect parameter (fixed values):
factor = 2  # How much the sleep time increases with each failed attempt
maxReconnect = 1
maxReconnectTime = 1200
sleepTime = 1  # So the first one is 1 second
maxConnectTime = 0


class NtripClient(object):
    def __init__(self, buffer=2048, user="", out=None, port=2101, caster="", mountpoint="", passwd="", host=False,
                 lat=40, lon=116, height=54.6, ssl=False, verbose=False, UDP_Port=None, V2=False, headerFile=sys.stderr,
                 headerOutput=False, maxConnectTime=1200):
        self.buffer = buffer
        if user.find(":") == -1:
            user = user + ":" + passwd
        self.user = b64encode(user.encode('utf-8')).decode() if highVer else b64encode(user)
        self.out = out
        self.port = port
        self.caster = caster
        if mountpoint.find("/") == -1:
            mountpoint = "/" + mountpoint
        self.mountpoint = mountpoint
        self.setPosition(lat, lon)
        self.height = height
        self.verbose = verbose
        self.ssl = ssl
        self.host = host
        self.UDP_Port = UDP_Port
        self.V2 = V2
        self.headerFile = headerFile
        self.headerOutput = headerOutput
        self.maxConnectTime = maxConnectTime
        self.data = Queue()
        self.socket = None

        if UDP_Port:
            self.UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.UDP_socket.bind(('', 0))
            self.UDP_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        else:
            self.UDP_socket = None

    def setPosition(self, lat, lon):
        self.flagN = "N"
        self.flagE = "E"
        if lon > 180:
            lon = (lon - 360) * -1
            self.flagE = "W"
        elif (lon < 0 and lon >= -180):
            lon = lon * -1
            self.flagE = "W"
        elif lon < -180:
            lon = lon + 360
            self.flagE = "E"
        else:
            self.lon = lon
        if lat < 0:
            lat = lat * -1
            self.flagN = "S"
        self.lonDeg = int(lon)
        self.latDeg = int(lat)
        self.lonMin = (lon - self.lonDeg) * 60
        self.latMin = (lat - self.latDeg) * 60

    def getMountPointString(self):

        mountPointString = "GET %s HTTP/1.1\r\nUser-Agent: %s\r\nAuthorization: Basic %s\r\n" % (
            self.mountpoint, useragent, self.user)
        #        mountPointString = "GET %s HTTP/1.1\r\nUser-Agent: %s\r\n" % (self.mountpoint, useragent)
        if self.host or self.V2:
            hostString = "Host: %s:%i\r\n" % (self.caster, self.port)
            mountPointString += hostString
        if self.V2:
            mountPointString += "Ntrip-Version: Ntrip/2.0\r\n"
        mountPointString += "\r\n"
        if self.verbose:
            print(mountPointString)

        return mountPointString.encode('utf-8') if highVer else mountPointString

    def getGGAString(self):
        now = datetime.utcnow()
        ggaString = "GPGGA,%02d%02d%04.2f,%02d%011.8f,%1s,%03d%011.8f,%1s,1,05,0.19,+00400,M,%5.3f,M,," % (
            now.hour, now.minute, now.second, self.latDeg, self.latMin, self.flagN, self.lonDeg, self.lonMin,
            self.flagE, self.height)
        checksum = self.calcultateCheckSum(ggaString)
        if self.verbose:
            print("$%s*%s\r\n" % (ggaString, checksum))
        gga = "$%s*%s\r\n" % (ggaString, checksum)
        return gga.encode()

    def calcultateCheckSum(self, stringToCheck):
        xsum_calc = 0
        for char in stringToCheck:
            xsum_calc = xsum_calc ^ ord(char)
        return "%02X" % xsum_calc

    def readData(self):
        reconnectTry = 1
        sleepTime = 1
        reconnectTime = 0
        if self.maxConnectTime > 0:
            EndConnect = timedelta(seconds=self.maxConnectTime)
        try:
            while reconnectTry <= maxReconnect:
                found_header = False
                if self.verbose:
                    sys.stderr.write('Connection {0} of {1}\n'.format(reconnectTry, maxReconnect))

                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if self.ssl:
                    self.socket = ssl.wrap_socket(self.socket)

                error_indicator = self.socket.connect_ex((self.caster, self.port))
                if error_indicator == 0:
                    sleepTime = 1
                    connectTime = datetime.now()

                    self.socket.settimeout(10)
                    self.socket.sendall(self.getMountPointString())
                    while not found_header:
                        casterResponse = self.socket.recv(4096)  # All the data
                        casterResponse = casterResponse.decode('utf-8') if highVer else casterResponse
                        header_lines = casterResponse.split("\r\n")

                        for line in header_lines:
                            if line == "":
                                if not found_header:
                                    found_header = True
                                    if self.verbose:
                                        sys.stderr.write("End Of Header" + "\n")
                            else:
                                if self.verbose:
                                    sys.stderr.write("Header: " + line + "\n")
                            if self.headerOutput:
                                self.headerFile.write(line + "\n")

                        for line in header_lines:
                            if line.find("SOURCETABLE") >= 0:
                                sys.stderr.write("Mount point does not exist")
                                sys.exit(1)
                            elif line.find("401 Unauthorized") >= 0:
                                sys.stderr.write("Unauthorized request\n")
                                sys.exit(1)
                            elif line.find("404 Not Found") >= 0:
                                sys.stderr.write("Mount Point does not exist\n")
                                sys.exit(2)
                            elif line.find("ICY 200 OK") >= 0:
                                # Request was valid
                                self.socket.sendall(self.getGGAString())
                            elif line.find("HTTP/1.0 200 OK") >= 0:
                                # Request was valid
                                self.socket.sendall(self.getGGAString())
                            elif line.find("HTTP/1.1 200 OK") >= 0:
                                # Request was valid
                                self.socket.sendall(self.getGGAString())

                    data = "Initial data"
                    while data:
                        try:
                            data = self.socket.recv(self.buffer)
                            self.data.put(data)
                            if self.out:
                                self.out.write(data)
                            if self.UDP_socket:
                                self.UDP_socket.sendto(data, ('<broadcast>', self.UDP_Port))
                            # print datetime.datetime.now()-connectTime
                            if maxConnectTime:
                                if datetime.now() > connectTime + EndConnect:
                                    if self.verbose:
                                        sys.stderr.write("Connection Timed exceeded\n")
                                    sys.exit(0)

                        except socket.timeout:
                            if self.verbose:
                                sys.stderr.write('Connection TimedOut\n')
                            data = False
                        except socket.error:
                            if self.verbose:
                                sys.stderr.write('Connection Error\n')
                            data = False

                    if self.verbose:
                        sys.stderr.write('Closing Connection\n')
                    self.socket.close()
                    self.socket = None

                    if reconnectTry < maxReconnect:
                        sys.stderr.write("%s No Connection to NtripCaster.  Trying again in %i seconds\n" % (
                            datetime.now(), sleepTime))
                        sleep(sleepTime)
                        sleepTime *= factor

                        if sleepTime > maxReconnectTime:
                            sleepTime = maxReconnectTime

                    reconnectTry += 1
                else:
                    self.socket = None
                    if self.verbose:
                        print("Error indicator: ", error_indicator)

                    if reconnectTry < maxReconnect:
                        sys.stderr.write("%s No Connection to NtripCaster.  Trying again in %i seconds\n" % (
                            datetime.now(), sleepTime))
                        sleep(sleepTime)
                        sleepTime *= factor
                        if sleepTime > maxReconnectTime:
                            sleepTime = maxReconnectTime
                    reconnectTry += 1

        except KeyboardInterrupt:
            if self.socket:
                self.socket.close()
            sys.exit()


if __name__ == '__main__':
    usage = "NtripClient.py [options] [caster] [port] mountpoint"
    parser = OptionParser(version=version, usage=usage)
    parser.add_option("-u", "--user", type="string", dest="user", default="feyman-user",
                      help="The Ntripcaster username.  Default: %default")
    parser.add_option("-p", "--password", type="string", dest="password", default="123456",
                      help="The Ntripcaster password. Default: %default")
    parser.add_option("-o", "--org", type="string", dest="org",
                      help="Use IBSS and the provided organization for the user. Caster and Port are not needed in this case Default: %default")
    parser.add_option("-b", "--baseorg", type="string", dest="baseorg",
                      help="The org that the base is in. IBSS Only, assumed to be the user org")
    parser.add_option("-t", "--latitude", type="float", dest="lat", default=50.09,
                      help="Your latitude.  Default: %default")
    parser.add_option("-g", "--longitude", type="float", dest="lon", default=8.66,
                      help="Your longitude.  Default: %default")
    parser.add_option("-e", "--height", type="float", dest="height", default=1200,
                      help="Your ellipsoid height.  Default: %default")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Verbose")
    parser.add_option("-s", "--ssl", action="store_true", dest="ssl", default=False, help="Use SSL for the connection")
    parser.add_option("-H", "--host", action="store_true", dest="host", default=False,
                      help="Include host header, should be on for IBSS")
    parser.add_option("-r", "--Reconnect", type="int", dest="maxReconnect", default=1, help="Number of reconnections")
    parser.add_option("-D", "--UDP", type="int", dest="UDP", default=None,
                      help="Broadcast recieved data on the provided port")
    parser.add_option("-2", "--V2", action="store_true", dest="V2", default=False, help="Make a NTRIP V2 Connection")
    parser.add_option("-f", "--outputFile", type="string", dest="outputFile", default=None,
                      help="Write to this file, instead of stdout")
    parser.add_option("-m", "--maxtime", type="int", dest="maxConnectTime", default=None,
                      help="Maximum length of the connection, in seconds")

    parser.add_option("--Header", action="store_true", dest="headerOutput", default=False,
                      help="Write headers to stderr")
    parser.add_option("--HeaderFile", type="string", dest="headerFile", default=None,
                      help="Write headers to this file, instead of stderr.")
    (options, args) = parser.parse_args(['ntrips.feymani.cn', '2102', 'Obs'])
    ntripArgs = {}
    ntripArgs['lat'] = options.lat
    ntripArgs['lon'] = options.lon
    ntripArgs['height'] = options.height
    ntripArgs['host'] = options.host

    if options.ssl:
        import ssl

        ntripArgs['ssl'] = True
    else:
        ntripArgs['ssl'] = False

    if options.org:
        if len(args) != 1:
            print("Incorrect number of arguments for IBSS\n")
            parser.print_help()
            sys.exit(1)
        ntripArgs['user'] = options.user + "." + options.org + ":" + options.password
        if options.baseorg:
            ntripArgs['caster'] = options.baseorg + ".ibss.trimbleos.com"
        else:
            ntripArgs['caster'] = options.org + ".ibss.trimbleos.com"
        if options.ssl:
            ntripArgs['port'] = 52101
        else:
            ntripArgs['port'] = 2101
        ntripArgs['mountpoint'] = args[0]

    else:
        if len(args) != 3:
            print("Incorrect number of arguments for NTRIP\n")
            parser.print_help()
            sys.exit(1)
        ntripArgs['user'] = options.user + ":" + options.password
        ntripArgs['caster'] = args[0]
        ntripArgs['port'] = int(args[1])
        ntripArgs['mountpoint'] = args[2]

    if ntripArgs['mountpoint'][0:1] != "/":
        ntripArgs['mountpoint'] = "/" + ntripArgs['mountpoint']

    ntripArgs['V2'] = options.V2

    ntripArgs['verbose'] = options.verbose
    ntripArgs['headerOutput'] = options.headerOutput

    if options.UDP:
        ntripArgs['UDP_Port'] = int(options.UDP)

    maxReconnect = options.maxReconnect
    maxConnectTime = options.maxConnectTime

    if options.verbose:
        print("Server: " + ntripArgs['caster'])
        print("Port: " + str(ntripArgs['port']))
        print("User: " + ntripArgs['user'])
        print("mountpoint: " + ntripArgs['mountpoint'])
        print("Reconnects: " + str(maxReconnect))
        print("Max Connect Time: " + str(maxConnectTime))
        if ntripArgs['V2']:
            print("NTRIP: V2")
        else:
            print("NTRIP: V1 ")
        if ntripArgs["ssl"]:
            print("SSL Connection")
        else:
            print("Uncrypted Connection")
        print("")

    fileOutput = False
    if options.outputFile:
        f = open(options.outputFile, 'wb')
        ntripArgs['out'] = f
        fileOutput = True

    if options.headerFile:
        h = open(options.headerFile, 'wb')
        ntripArgs['headerFile'] = h
        ntripArgs['headerOutput'] = True

    n = NtripClient(**ntripArgs)
    try:
        n.readData()
    finally:
        if fileOutput:
            f.close()
        if options.headerFile:
            h.close()
