# -*- coding: utf-8 -*-
""" 
 Created on 11/12/2019 3:52 PM
 
 @author : chey
 
"""
import serial
from queue import Queue
from threading import Thread
from optparse import OptionParser
from streams import NtripClient

version = 0.2
NBYTES = 1024

class SerialStream():
    """
    Serial port duplex
    """

    def __init__(self, port, baud, rport=None):
        self.port = port
        self.baud = baud
        self.rport = rport
        self.nmeabuff = Queue()

        self.s = serial.Serial(port=self.port, baudrate=self.baud)
        if self.s.isOpen():
            self.s.close()

        try:
            self.s.open()
        except:
            raise IOError(f"can not open {self.port}@{self.baud}")

    def read(self):
        """
<<<<<<< HEAD
        read nmea from serial Rx buffer into nmea buffer queue
=======
        read nmea from serial Rx buffer
>>>>>>> d87451fcf0a6842a2aa30e6486ac0a09f4339c14
        :return:
        """
        while True:
            data = self.s.readline()
            self.nmeabuff.put(data.decode())
            print(f"{data}")

    def write(self, dataq):
<<<<<<< HEAD

=======
>>>>>>> d87451fcf0a6842a2aa30e6486ac0a09f4339c14
        """
        write rtcm into serial Tx buffer
        :return:
        """
        while True:
            self.s.write(dataq.get())


if __name__ == '__main__':
<<<<<<< HEAD
    # usage example
=======
>>>>>>> d87451fcf0a6842a2aa30e6486ac0a09f4339c14
    usage = "Serial.py [porta] [baud] [portb]"
    parser = OptionParser(version=version, usage=usage)
    parser.add_option("-p", "--port", type="string", dest="port", default="COM20",
                      help="PC serial com port.  Default: %default")
    parser.add_option("-b", "--baud", type=int, dest="baud", default=115200, help="Serial baud rate. Default: %default")
    parser.add_option("-r", "--rvt", type="string", dest="rvt", default=None,
                      help="Revert current serial port data into another one.")

    (options, args) = parser.parse_args(['COM20', '115200'])
    serialArgs = {}
    serialArgs['port'] = options.port
    serialArgs['baud'] = options.baud
    if options.rvt is not None:
        serialArgs['rport'] = options.rvt

    # create ntrip/serial stream  instance
    ntrip = NtripClient.NtripClient(caster="ntrips.feymani.cn", port=2102, mountpoint="Obs", user="feyman-user",
                                    passwd="123456")
    ser = SerialStream(**serialArgs)

    # start thread
    cors = Thread(target=ntrip.readData)
    serx = Thread(target=ser.read)
    serwx = Thread(target=ser.write, args=(ntrip.data,))

    cors.start()
    serx.start()
    serwx.start()
