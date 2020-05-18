# -*- coding: utf-8 -*-
""" 
 Created on 11/13/2019 3:05 PM
 
 @author : chey
 
"""
# TODO: more test case

from base64 import b64encode
from datetime import datetime
from os import path, stat, makedirs
from sys import argv, exit
from threading import Thread
from functools import partial
# from matplotlib.pyplot import figure, plot, title, xlabel, ylabel, show, grid, subplots, axhline

import serial
import serial.tools.list_ports
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QTextCursor, QIcon
from PyQt5.QtNetwork import QTcpSocket
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog

from extools.nmea2kml import nmeaFileToCoords, genKmlStr
# from extools.comp_gga_analysis import genComp
from gui.form import Ui_widget
from gui.multiser import Multiser_Ui_widget

###################################################################
DIR = 'NMEA/'
OPEN = 'Open'
CLOSE = 'Close'
CONNECT = 'Connect'
DISCONNECT = 'Disconnect'

# SWITCH_ON = [0xA0, 0x01, 0x01, 0xA2]
# SWITCH_OFF = [0xA0, 0x01, 0x00, 0xA1]
###################################################################
SEND_BYTES = 0
SAVE_NMEA = False
ENABLE_TOOL_BTN = True
SERIAL_PORT_LIST = []
SERIAL_WRITE_MUTEX = False
SERIAL_SET = [None, None, None, None]
LABEL_SHOW_LIST = [None, None, None, None]
FIRM_UPDATE_LIST = [False, False, False, False]

COLOR_TAB = {'0': 'gray', '1': 'red', '2': '#55aaff', '3': 'black', '4': 'green', '5': 'blue', '6': '#ff55ff'}


###################################################################

def gettstr() -> str:
    """
    get current host time string
    :return:
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def refresh_ser() -> list:
    """
    refresh current host serial port
    :return:
    """
    port_list = list(serial.tools.list_ports.comports())
    return port_list


def update_mulfirmware(file: str, serhd: serial.Serial, sn: int) -> None:
    """
    multi-serial firmware update
    :param file:
    :param serhd:
    :return:
    """
    global LABEL_SHOW_LIST, SERIAL_WRITE_MUTEX
    if file is None or serhd is None:
        return False

    if LABEL_SHOW_LIST[sn] is not None:
        LABEL_SHOW_LIST[sn].setText("updating...")
        LABEL_SHOW_LIST[sn].setStyleSheet("{ background-color : red; color : black; }")

    SERIAL_WRITE_MUTEX = False
    with open(file, "rb") as f:
        for line in f:
            serhd.write(line)

    SERIAL_WRITE_MUTEX = True
    if LABEL_SHOW_LIST[sn] is not None:
        LABEL_SHOW_LIST[sn].setText("done!")
        LABEL_SHOW_LIST[sn].setStyleSheet("{ background-color : green; color : black; }")


def update_firmware(file: str, serhd: serial.Serial) -> None:
    """
    send file to serial handler
    :param file: binary file
    :param serhd: serial handler
    :return:
    """
    global SERIAL_WRITE_MUTEX, SEND_BYTES

    if file is None or serhd is None:
        return False

    SERIAL_WRITE_MUTEX = True
    with open(file, "rb") as f:
        for line in f:
            serhd.write(line)
            SEND_BYTES += len(line)

    SERIAL_WRITE_MUTEX = False


class MultiSerial(QMainWindow, Multiser_Ui_widget):
    def __init__(self, parent=None):
        global ENABLE_TOOL_BTN
        ENABLE_TOOL_BTN = False

        super(MultiSerial, self).__init__(parent)
        # self.setWindowFlags(Qt.WindowStaysOnBottomHint)
        self.setFixedSize(780, 580)
        self._exit = False
        self.setupUi(self)
        self.create_items(4)
        self.create_slots()
        self.port_refresh()

    def set_ser_params(self, enable, spn):
        self.cbsport[spn].setEnabled(enable)
        self.cbsbaud[spn].setEnabled(enable)
        self.cbsattr[spn].setEnabled(enable)

    def port_refresh(self):
        """
        refresh current serial port list
        :return:
        """
        for port in self.cbsport:
            port.clear()

        for com in SERIAL_PORT_LIST:
            for port in self.cbsport:
                port.addItem(com)

    def create_items(self, nsers):
        self._fh = [None for _ in range(4)]
        self._fn = ['' for _ in range(4)]

        self._check = [self.cb_firmu1, self.cb_firmu2, self.cb_firmu3, self.cb_firmu4]
        self._text = [self.textEdit_1, self.textEdit_2, self.textEdit_3, self.textEdit_4]
        self.cbsport = [self.cs_port_1, self.cs_port_2, self.cs_port_3, self.cs_port_4]
        self.cbsbaud = [self.cs_baud_1, self.cs_baud_2, self.cs_baud_3, self.cs_baud_4]
        self.cbsattr = [self.cs_attrs_1, self.cs_attrs_2, self.cs_attrs_3, self.cs_attrs_4]
        self.com = [serial.Serial() for _ in range(nsers)]

        self.ReadSerTimer = [QTimer() for _ in range(nsers)]
        self.LEllh = [self.lineEdit_llh1, self.lineEdit_llh2, self.lineEdit_llh3, self.lineEdit_llh4]
        self.LEstat = [self.lineEdit_stat1, self.lineEdit_stat2, self.lineEdit_stat3, self.lineEdit_stat4]
        self.LBshow = [self.label, self.label_2, self.label_3, self.label_4]

    def create_slots(self):
        # button click signal
        self.pushButton_open_1.clicked.connect(partial(self.on_button, (self.pushButton_open_1, 0)))
        self.pushButton_open_2.clicked.connect(partial(self.on_button, (self.pushButton_open_2, 1)))
        self.pushButton_open_3.clicked.connect(partial(self.on_button, (self.pushButton_open_3, 2)))
        self.pushButton_open_4.clicked.connect(partial(self.on_button, (self.pushButton_open_4, 3)))

        # text received signal
        self.textEdit_1.textChanged.connect(partial(self.on_txtchange, self.textEdit_1))
        self.textEdit_2.textChanged.connect(partial(self.on_txtchange, self.textEdit_2))
        self.textEdit_3.textChanged.connect(partial(self.on_txtchange, self.textEdit_3))
        self.textEdit_4.textChanged.connect(partial(self.on_txtchange, self.textEdit_4))

    def on_button(self, btntup):
        """
        serial open button clicked handling
        :return:
        """
        btn = btntup[0]
        spn = btntup[1]
        if btn.text() == OPEN:
            self.com[spn].port = self.cbsport[spn].currentText()
            self.com[spn].baudrate = int(self.cbsbaud[spn].currentText())

            attrs = self.cbsattr[spn].currentText().split('/')
            self.com[spn].bytesize = int(attrs[0])
            self.com[spn].stopbits = int(attrs[2])
            self.com[spn].parity = attrs[1]
            self.com[spn].timeout = 0

            self.com[spn].close()
            try:
                self.com[spn].open()
                SERIAL_SET[spn] = self.com[spn]
            except serial.SerialException:
                QMessageBox.critical(self, "error", f"can not open serial {self.com[spn].port}")
            else:
                self.set_ser_params(False, spn)
                btn.setText(CLOSE)
                self.ReadSerTimer[spn].timeout.connect(partial(self.on_read, (self.com[spn], spn)))
                self.ReadSerTimer[spn].start(20)
                self._text[spn].clear()

        elif btn.text() == CLOSE:
            self.ReadSerTimer[spn].stop()
            self.com[spn].close()
            self.LBshow[spn].setText("closed")
            self.set_ser_params(True, spn)
            self._fh = [None for _ in range(4)]
            self._fn = ['' for _ in range(4)]
            btn.setText(OPEN)

    def on_read(self, stup):
        global SAVE_NMEA
        s = stup[0]
        n = stup[1]

        if not s.isOpen(): return
        data = s.readline()

        if data != b'':
            if SAVE_NMEA:
                if self._fh[n] is None:
                    if self._fn[n] == '':
                        self._fn[n] = DIR + s.port + '_' + gettstr()
                    self._fh[n] = open(self._fn[n] + '.nmea', 'wb')
                else:
                    self._fh[n].write(data)
                    self._fh[n].flush()
            else:
                self._fn = ['' for _ in range(4)]
                for f in self._fh:
                    if f is not None:
                        f.write(data)
                        f.flush()
                self._fh = [None for _ in range(4)]

            # decode received data
            data = data.decode("utf-8", "ignore")
            self._text[n].insertPlainText(data)
            self.LBshow[n].setText("serial recv...")

            # display info
            if data.startswith(('$GNGGA', '$GPGGA')):
                self.disp_gga(data, n)

            # check firmware update
            if self._check[n].isChecked():
                FIRM_UPDATE_LIST[n] = True
                LABEL_SHOW_LIST[n] = self.LBshow[n]
            else:
                FIRM_UPDATE_LIST[n] = False
                LABEL_SHOW_LIST[n] = None

    def disp_gga(self, data, n):
        """
        display gga string
        :param data: gga string
        :return:
        """
        if data.startswith(('$GNGGA', '$GPGGA')) and data.endswith("\r\n"):
            seg = data.strip("\r\n").split(",")
            if len(seg) < 14: return

            now, latdm = seg[1:3]
            londm = seg[4]
            solstat, nsats, dop, hgt = seg[6:10]
            dage = seg[-2]
            dage = dage if dage != '' else '0'

            if latdm != '' and londm != '':
                try:
                    lat_deg = float(latdm)
                    lon_deg = float(londm)
                except TypeError as e:
                    return
                else:
                    a = int(lat_deg / 100) + (lat_deg % 100) / 60
                    o = int(lon_deg / 100) + (lon_deg % 100) / 60
                    latdm, londm = "%.8f" % a, "%.8f" % o

                stat = "{0:8s},{1:2d},{2:1d},{3:<3s}".format(now, int(nsats), int(solstat), dage)
                self.LEstat[n].setText(stat)

                if float(dage) > 30:
                    self.LEstat[n].setStyleSheet('background-color:#ff557f; color:white')
                else:
                    self.LEstat[n].setStyleSheet('background-color:white; color:black')

                bg = COLOR_TAB[solstat]
                self.LEllh[n].setStyleSheet('background-color:' + bg + '; color:white')

                llh = "{0:10s},{1:11s},{2:5s}".format(latdm, londm, hgt)
                self.LEllh[n].setText(llh)

            else:
                pass  # lat, lon not a float string

    def on_txtchange(self, txtup):
        txtup.moveCursor(QTextCursor.End)

    def closeEvent(self, event):
        for f in self._fh:
            if f is not None:
                f.flush()

        global ENABLE_TOOL_BTN
        ENABLE_TOOL_BTN = True
        self._exit = True


############################################################################################
class NtripSerialTool(QMainWindow, Ui_widget):
    """
    Ntrip serial tool for testing FMI P20 comb board
    """
    global SERIAL_WRITE_MUTEX, ENABLE_TOOL_BTN

    def __init__(self, parent=None):
        super(NtripSerialTool, self).__init__(parent)
        self.setWindowIcon(QIcon("./gui/i.svg"))
        self.setFixedSize(950, 590)
        self._fh = None
        self._fhcors = None
        self._imgfile = None
        self._nmeaf = None
        self._fn = ''

        self._cold_reseted = False
        self._mnt_updated = False
        self._getmnt = b''
        self._curgga = b''
        self._caster = ''
        self._port = 0
        self._srxbs = 0
        self._stxbs = 0
        self._nrxbs = 0
        self._ntxbs = 0
        self._val = 0

        self._ggacnt = 0
        self._cold_resets = 0

        self._cold_reset_cnt = 0
        self.setupUi(self)
        self.create_items()
        self.create_sigslots()
        self.ser_refresh()
        if not path.exists(DIR):
            makedirs(DIR)

    def create_items(self):
        """
        create serial, socket, timer instance
        :return:
        """
        self.com = serial.Serial()
        self.sock = QTcpSocket()

        self.ReadSerTimer = QTimer(self)
        self.ReadSerTimer.timeout.connect(self.read_ser_data)

        self.send_ggaTimer = QTimer(self)
        self.send_ggaTimer.timeout.connect(self.send_gga)

        self.NtripReconTimer = QTimer(self)
        self.NtripReconTimer.timeout.connect(self.ntp_reconn)

        self.FileTrans = QTimer(self)
        self.FileTrans.timeout.connect(self.ShowFilepBarr)

    def create_sigslots(self):
        """
        connect signal with slots
        :return:
        """
        self.pushButton_open.clicked.connect(self.ser_open_btclik)
        self.pushButton_conn.clicked.connect(self.ntp_conn_btclik)
        self.pushButton_atcmd.clicked.connect(self.atcmd_send_btclik)
        self.pushButton_clear.clicked.connect(self.serecv_clear_btclik)
        self.pushButton_close.clicked.connect(self.close_all)
        self.pushButton_stop.clicked.connect(self.stop_all)

        # serial refresh button pressed
        self.pushButton_refresh.clicked.connect(self.ser_refresh)

        # tool button pressed
        self.toolButton.clicked.connect(self.mulser_control)

        # self.cbsport.mousePressEvent()

        # open image file and send it to P20 navi board
        self.open_file.clicked.connect(self.open_filed)
        self.trans_file.clicked.connect(self.trans_filed)

        # generate kml file
        self.open_nmea_file.clicked.connect(self.open_nmeaf)
        self.gen_kml.clicked.connect(self.write_kml)

        # ntrip client socket re-connection on disconnection
        self.sock.connected.connect(self.sock_conn)
        self.sock.readyRead.connect(self.sock_recv)

        # s serial received text changed
        self.textEdit_recv.textChanged.connect(self.text_recv_changed)

    def ser_refresh(self):
        """
        refresh current serial port list
        :return:
        """
        self.cbsport.clear()
        port_list = refresh_ser()
        for port in port_list:
            if port[0] not in SERIAL_PORT_LIST:
                SERIAL_PORT_LIST.append(port[0])
            self.cbsport.addItem(port[0])

    # serial configuration parameters
    def ser_open_btclik(self):
        """
        serial open button clicked handling
        :return:
        """
        if self.pushButton_open.text() == OPEN:
            attrs = self.cbsdata.currentText().split('/')

            self.com.port = self.cbsport.currentText()
            self.com.baudrate = int(self.cbsbaud.currentText())
            self.com.bytesize = int(attrs[0])
            self.com.stopbits = int(attrs[2])
            self.com.parity = attrs[1]
            self.com.timeout = 0

            self.com.close()
            try:
                self.com.open()
            except serial.SerialException as e:
                QMessageBox.critical(self, "error", f"can not open serial {self.com.port}")
            else:
                self.set_ser_params(False)
                self.pushButton_open.setText(CLOSE)
                self.pushButton_refresh.setEnabled(False)
                self.ReadSerTimer.start(20)

            self.textEdit_recv.clear()
            self.textEdit_recv.clear()
        elif self.pushButton_open.text() == CLOSE:
            self.ReadSerTimer.stop()
            self.com.close()
            self.set_ser_params(True)
            self.pushButton_open.setText(OPEN)
            self.pushButton_refresh.setEnabled(True)

    def read_ser_data(self):
        """
        serial port reading
        :return:
        """
        global SAVE_NMEA
        SAVE_NMEA = self.checkBox_savenmea.isChecked()
        if not self.com.isOpen(): return
        data = self.com.readline()

        if data != b'':
            if self.checkBox_savenmea.isChecked():
                if self._fh is None:
                    if self._fn == '':
                        self._fn = DIR + self.com.port + '_' + gettstr()
                    self._fh = open(self._fn + '.nmea', 'wb')
                else:
                    self._fh.write(data)
            else:
                self._fn = ''
                if self._fh is not None:
                    self._flush_file()
                    self._fh.close()
                    self._fh = None

            self._curgga = data
            self._srxbs += len(data)
            data = data.decode("utf-8", "ignore")
            self.textEdit_recv.insertPlainText(data)
            self.lineEdit_srx.setText(str(self._srxbs))

            try:
                if data.startswith(('$GNGGA', '$GPGGA')):
                    self.disp_gga(data)
                elif data.startswith("$GPFMI"):
                    self.disp_fmi(data)
                elif data.startswith("$GNTXT"):
                    self._cold_reseted = False
            except Exception as e:
                pass  # print(e)


    def set_lebf_color(self, bg, fg):
        self.lineEdit_rovlat.setStyleSheet('background-color:' + bg + '; color:' + fg)
        self.lineEdit_rovlon.setStyleSheet('background-color:' + bg + '; color:' + fg)
        self.lineEdit_rovhgt.setStyleSheet('background-color:' + bg + '; color:' + fg)
        self.lineEdit_solstat.setStyleSheet('background-color:' + bg + '; color:' + fg)

    def disp_gga(self, data):
        """
        display gga string
        :param data: gga string
        :return:
        """
        if data.startswith(('$GNGGA', '$GPGGA')) and data.endswith("\r\n"):
            seg = data.strip("\r\n").split(",")
            if len(seg) < 15: return

            now, latdm = seg[1:3]
            londm = seg[4]
            solstat, nsats, dop, hgt = seg[6:10]
            dage = seg[-2]

            # if solstat == '4':
            #     self._ggacnt += 1
            # if self._ggacnt >= 10:
            #     self._ggacnt = 0
            #     self._cold_resets += 1
            #     self.com.write('AT+COLD_RESET\r\n'.encode("utf-8", "ignore"))
            #     self.com.write('AT+COLD_RESET\r\n'.encode("utf-8", "ignore"))
            #     self.com.write('AT+COLD_RESET\r\n'.encode("utf-8", "ignore"))
            #     self.com.write('AT+COLD_RESET\r\n'.encode("utf-8", "ignore"))
            #     print(f'device cold reset cnt {self._cold_resets}')

            if latdm != '' and londm != '':
                if self.checkBox_ggafmt.isChecked():
                    try:
                        lat_deg = float(latdm)
                        lon_deg = float(londm)
                    except TypeError as e:
                        return
                    else:
                        a = int(lat_deg / 100) + (lat_deg % 100) / 60
                        o = int(lon_deg / 100) + (lon_deg % 100) / 60
                        latdm, londm = "%.7f" % a, "%.7f" % o

                self.set_lebf_color(COLOR_TAB[solstat], 'white')
                self.lineEdit_rovlat.setText(latdm)
                self.lineEdit_rovlon.setText(londm)
                self.lineEdit_rovhgt.setText(hgt)
                self.lineEdit_solstat.setText(solstat)
                self.lineEdit_sats.setText(nsats)
                self.lineEdit_time.setText(now)
                self.lineEdit_dage.setText(dage)
                dage = dage if dage != '' else '0'
                if float(dage) > 30:
                    self.lineEdit_dage.setStyleSheet('background-color:#ff557f;color:white')
                else:
                    self.lineEdit_dage.setStyleSheet('background-color:white;color:black')
                if int(nsats) < 5:
                    self.lineEdit_sats.setStyleSheet('background-color:#ff5500;color:white')
                else:
                    self.lineEdit_sats.setStyleSheet('background-color:white;color:black')
            else:
                pass  # lat, lon not a float string

    def disp_fmi(self, data):
        seg = data.strip("\r\n").split(",")
        if len(seg) < 14: return
        week, sow = seg[1:3]
        y, p, r = seg[3:6]
        # seg[6:9]
        ve, vn, vu = seg[9:12]
        bl = seg[12]
        self.lineEdit_wk.setText(week)
        self.lineEdit_sow.setText(sow)
        self.lineEdit_yaw.setText(y)
        self.lineEdit_pitch.setText(p)
        self.lineEdit_roll.setText(r)
        self.lineEdit_ve.setText(ve)
        self.lineEdit_vn.setText(vn)
        self.lineEdit_vu.setText(vu)
        self.lineEdit_bl.setText(bl)

    def set_ser_params(self, enable):
        self.cbsport.setEnabled(enable)
        self.cbsbaud.setEnabled(enable)
        self.cbsdata.setEnabled(enable)

    def set_ntrip_params(self, enable):
        self.comboBox_caster.setEnabled(enable)
        self.comboBox_port.setEnabled(enable)
        self.comboBox_mount.setEnabled(enable)
        self.lineEdit_user.setEnabled(enable)
        self.lineEdit_pwd.setEnabled(enable)

    # get ntrip caster params, invoke NtripClient thread
    def ntp_conn_btclik(self):
        if self.pushButton_conn.text() == CONNECT:
            caster = self.comboBox_caster.currentText()
            port = int(self.comboBox_port.currentText())
            mount = self.comboBox_mount.currentText()

            if self.lineEdit_user.text() == '' or self.lineEdit_pwd.text() == '':
                user, passwd = 'feyman-user', '123456'
            else:
                user = self.lineEdit_user.text()
                passwd = self.lineEdit_pwd.text()

            self._port = port
            self._caster = caster

            self.sock.open(QTcpSocket.ReadWrite)

            # get mount point and try to connect caster
            user = b64encode((user + ":" + passwd).encode('utf-8')).decode()
            self.set_mntp_str(mount, user)
            self.ntp_conn(caster, port)
            self.set_ntrip_params(False)
            self.NtripReconTimer.start(20000)
            self.pushButton_conn.setText(DISCONNECT)

        elif self.pushButton_conn.text() == DISCONNECT:
            self._term_ntrip()

    # at command button handle
    def atcmd_send_btclik(self):
        if not SERIAL_WRITE_MUTEX:
            cmd = self.cbatcmd.currentText() + "\r\n"
            if not cmd.startswith(('AT+', '$J')):
                QMessageBox.warning(self, "Warning", "Only support Feynman and H command")
                return
            # while in firmware update mode, terminate ntrip first
            if cmd in ["AT+UPDATE_MODE\r\n", "AT+UPDATE_SHELL\r\n", "AT+UPDATE_MODE_H=115200\r\n"]:
                self._term_ntrip()

            # re-direct to other serial port
            if '>' in cmd:
                _cmd, _port = cmd.strip("\r\n").split('>')
                _cmd = _cmd.strip() + "\r\n"
                _port = _port.strip().lower().split(',')

                if _port[0] == 'all':
                    _s = [s.port for s in SERIAL_SET if s is not None and s.isOpen]
                    _ss = ', '.join(_s)
                    ret = QMessageBox.information(self, "Info", f"send {_cmd} to {_ss}", QMessageBox.No,
                        QMessageBox.Yes)
                    if ret == QMessageBox.No:
                        return
                    if self.com.isOpen():
                        self.com.write(cmd.encode("utf-8", "ignore"))

                for s in SERIAL_SET:
                    # support all serial port config
                    if _port[0] == 'all':
                        if s is not None and s.isOpen():
                            s.write(_cmd.encode("utf-8", "ignore"))
                    else:
                        # port list must startswith 'com
                        for p in _port:
                            if not p.startswith('com'):
                                QMessageBox.warning(self, "Warning", "cmd as: AT+THIS_PORT>coma,comb")
                                return
                        # config each specified serial port
                        if s is not None and s.isOpen() and s.port.lower() in _port:
                            s.write(_cmd.encode("utf-8", "ignore"))
            else:
                if self.com.isOpen():
                    self.com.write(cmd.encode("utf-8", "ignore"))
                else:
                    QMessageBox.warning(self, "Warning", "Open serial port first! ")
        else:
            QMessageBox.information(self, "Info", "Firmware updating......")

    # generate sync mount point string
    def set_mntp_str(self, mnt, user):
        mountPointString = "GET /%s HTTP/1.1\r\nUser-Agent: %s\r\nAuthorization: Basic %s\r\n" % (
            mnt, "NTRIP FMIPythonClient/1.0", user)
        mountPointString += "\r\n"
        self._getmnt = mountPointString.encode('utf-8')

    # connect to host
    def ntp_conn(self, caster, port):
        self.sock.connectToHost(caster, port)
        if not self.sock.waitForConnected(5000):
            msg = self.sock.errorString()
            QMessageBox.critical(self, "Error", msg)
        self.send_ggaTimer.start(10000)

    # sock connect, write get mount point request
    def sock_conn(self):
        self.sock.write(self._getmnt)

    # socket receive data
    def sock_recv(self):
        if not SERIAL_WRITE_MUTEX:
            rtcm = self.sock.readAll()

            # source cors host mount point
            if self._mnt_updated is False and b'SOURCETABLE 200 OK' in rtcm:
                resp_list = bytes(rtcm).decode().split("\r\n")[6:]
                self.comboBox_mount.removeItem(0)
                for mnt in resp_list:
                    if mnt.startswith('STR;'):
                        self.comboBox_mount.addItem(mnt.split(';')[1])
                self._term_ntrip()
                self._mnt_updated = True
                return
            # log cors rtcm data into file self._fhcors
            if self.checkBox_logcos.isChecked():
                if self._fhcors is None:
                    if self._fn == '':
                        self._fn = DIR + gettstr()
                    self._fhcors = open(self._fn + '.cors', 'wb')
                else:
                    self._fhcors.write(rtcm)
            else:
                if self._fhcors is not None:
                    self._flush_file()
                    self._fhcors.close()
                    self._fhcors = None

            # write rtcm data into serial
            if self.com.isOpen():
                n = self.com.write(rtcm)
                self._stxbs += n
                self.lineEdit_stx.setText(str(self._stxbs))
            else:
                pass

            # write rtcm data into multi serial
            for _com in SERIAL_SET:
                if _com is not None and _com.isOpen():
                    _w = _com.port == self.com.port and not self.com.isOpen()
                    if _w or _com.port != self.com.port:
                        _com.write(rtcm)

            self._val += 5
            self.progressBar.setValue(self._val % 100)
        else:
            pass

    # send gga to ntrip server
    def send_gga(self):
        if not SERIAL_WRITE_MUTEX:
            self._flush_file()
            if self.sock.isOpen():
                if self._curgga.decode("utf-8", "ignore").startswith(("$GNGGA", "$GPGGA")):
                    self.sock.write(self._curgga)

    # ntirp reconnection
    def ntp_reconn(self):
        if not SERIAL_WRITE_MUTEX:
            if self.sock.state() == QTcpSocket.UnconnectedState:
                self.pushButton_conn.click()
                self.pushButton_conn.click()

    # clear serial received data
    def serecv_clear_btclik(self):
        self._srxbs = 0
        self._stxbs = 0
        self.textEdit_recv.clear()
        self._flush_file()

    # text cursor at end
    def text_recv_changed(self):
        if self.checkBox_autoScoll.isChecked():
            self.textEdit_recv.moveCursor(QTextCursor.End)

    def open_filed(self):
        QMessageBox.information(self, "Info", f"Please confirm P20 is in the update mode!", QMessageBox.Ok)

        filename, filetype = QFileDialog.getOpenFileName(self, "Select file", "./", "All Files (*);;Text Files (*.txt)")
        if filename != "" and not filename.endswith(".enc"):
            QMessageBox.warning(self, "Warning", f"Please select proper .enc file", QMessageBox.Ok)
            return
        else:
            self.lineEdit_filename.setText(filename)
            self._imgfile = filename

    # send file to serial
    def trans_filed(self):
        global SEND_BYTES
        SEND_BYTES = 0
        if self._imgfile is None:
            QMessageBox.warning(self, "Warning", f".enc file first plz!")
        else:
            info = ""
            mulcom_list = []
            for i, _com in enumerate(zip(SERIAL_SET, FIRM_UPDATE_LIST)):
                if _com[1] and _com[0] is not None and _com[0].isOpen():
                    mulcom_list.append((_com, i))
                    info += _com[0].port
                    info += " "
            info += self.com.port
            ret = QMessageBox.warning(self, "Warning", f"update serial {info}", QMessageBox.No, QMessageBox.Yes)
            if ret == QMessageBox.No:
                return

            file_size = stat(self._imgfile).st_size
            self.file_transbar.setRange(0, file_size)
            Thread(target=update_firmware, args=(self._imgfile, self.com)).start()

            # _com = (serial, update firm check box)
            for _port in mulcom_list:
                Thread(target=update_mulfirmware, args=(self._imgfile, _port[0][0], _port[1])).start()

            self.FileTrans.start(1200)
            self.file_transbar.setValue(0)

    def ShowFilepBarr(self):
        if SERIAL_WRITE_MUTEX:
            self.file_transbar.setValue(SEND_BYTES)
        else:
            self.file_transbar.setValue(SEND_BYTES)
            self.FileTrans.stop()

    # close window
    def close_all(self):
        if self.com.isOpen():
            self.ReadSerTimer.stop()
            self.com.flush()
            self.com.close()

        if self.sock.isOpen():
            self._term_ntrip()

        if self._fh is not None:
            self._fh.flush()
            self._fh.close()

        if self._fhcors is not None:
            self._fhcors.flush()
            self._fhcors.close()

        exit(0)

    # stop all stream
    def stop_all(self):
        if self.com.isOpen():
            self.com.close()
            self.set_ser_params(True)
            self.pushButton_open.setText(OPEN)

        if self.sock.isOpen():
            self._term_ntrip()

        self._flush_file()

    # terminate ntrip connection
    def _term_ntrip(self):
        self.sock.flush()
        self.sock.close()
        self.send_ggaTimer.stop()
        self.NtripReconTimer.stop()
        self.set_ntrip_params(True)
        self.progressBar.setValue(0)
        self.pushButton_conn.setText(CONNECT)

    # flush recorded nmea file
    def _flush_file(self):
        if self._fh is not None:
            self._fh.flush()
        if self._fhcors is not None:
            self._fhcors.flush()

    # get extools combo selection
    def write_kml(self):
        select = self.comboBox_extools.currentText()
        if self._nmeaf is None:
            QMessageBox.information(self, "Info", f"Invalid file, select one first")
            return
        if select.startswith('1 - '):
            QMessageBox.information(self, "Info", f"Convert {self._nmeaf} gga to kml")
            self.tokml(self._nmeaf, 'GGA')
        elif select.startswith('2 - '):
            QMessageBox.information(self, "Info", f"Convert {self._nmeaf} fmi to kml")
            self.tokml(self._nmeaf, 'FMI')
        else:
            QMessageBox.information(self, "Info", f"To be continued...")

    # extools file browser
    def open_nmeaf(self):
        filename, filetype = QFileDialog.getOpenFileName(self, "Select file", "./", "All Files (*);;Text Files (*.txt)")
        if filename != "":
            self._nmeaf = filename

    # extools nmea to kml
    def tokml(self, fn, header='GGA'):
        fnkml = fn + '.kml'
        if path.exists(fnkml):
            over_write = QMessageBox.warning(self, "Warning", f"Over write {fnkml} ?", QMessageBox.No, QMessageBox.Yes)
        else:
            over_write = QMessageBox.Yes

        if over_write == QMessageBox.Yes:
            fo = open(fnkml, 'w')
            with open(fn, 'r', encoding='utf-8') as f:
                coords = nmeaFileToCoords(f, header)
                kml_str, info = genKmlStr(coords, header)

            fo.write(kml_str)
            fo.flush()
            fo.close()

            QMessageBox.information(self, "Info", f"{fnkml} done\n"
                                                  f"Statistics\n{info}")

    # def ana_nmea(self, nmea, header):
    #     # gga analysis
    #     cnt = 0
    #     sol = {'0': 0, '1': 0, '2': 0, '4': 0, '5': 0, '6': 0}
    #     tofo, tolo = '', ''
    #     if header == 'GGA':
    #         for utc, val in nmea.items():
    #             val_len = len(val)
    #             # first and last obs time
    #             if cnt == 0:
    #                 tofo = utc
    #             tolo = utc
    #             # solution stat statistics
    #             cnt += 1
    #             if val_len == 10:
    #                 stat = val[7]
    #             else:
    #                 stat = val[3]
    #             sol[stat] += 1
    #     else:
    #         for utc, val in nmea.items():
    #             # first and last obs time
    #             if cnt == 0:
    #                 tofo = utc
    #             tolo = utc
    #             # solution stat statistics
    #             cnt += 1
    #             sol[val[3]] += 1
    #     spp_ratio = "{:4.1f}".format(100 * sol['1'] / cnt)
    #     dgps_ratio = "{:4.1f}".format(100 * sol['2'] / cnt)
    #     fix_ratio = "{:4.1f}".format(100 * sol['4'] / cnt)
    #     float_ratio = "{:4.1f}".format(100 * sol['5'] / cnt)
    #     dr_ratio = "{:4.1f}".format(100 * sol['6'] / cnt)
    #     if header == 'GGA':
    #         stofo = tofo[:2] + ':' + tofo[2:4] + ':' + tofo[4:]
    #         stolo = tolo[:2] + ':' + tolo[2:4] + ':' + tolo[4:]
    #         ts = datetime.strptime(tolo, '%H%M%S.%f') - datetime.strptime(tofo, '%H%M%S.%f')
    #     else:
    #         tofo_list = tofo.split()
    #         tolo_list = tolo.split()
    #         stofo = tofo_list[0] + ' ' + tofo_list[1][:2] + ':' + tofo_list[1][2:4] + ':' + tofo_list[1][4:]
    #         stolo = tolo_list[0] + ' ' + tolo_list[1][:2] + ':' + tolo_list[1][2:4] + ':' + tolo_list[1][4:]
    #         ts = datetime.strptime(tolo, '%m/%d/%Y %H%M%S.%f') - datetime.strptime(tofo, '%m/%d/%Y %H%M%S.%f')
    #
    #     s = f"Total points: {cnt}\n" \
    #         f"Time(UTC): {stofo} - {stolo}, duration {ts} \n" \
    #         f"Solution state: SPP {sol['1']}({spp_ratio}%), DGPS {sol['2']}({dgps_ratio}%)\n" \
    #         f"FIX {sol['4']}({fix_ratio}%), FLOAT {sol['5']}({float_ratio}%), DR {sol['6']}({dr_ratio}%)"
    #     return s

    # def devmap(self, fn):
    #     if fn is None:
    #         QMessageBox.critical(self, "Error", f"Invalid file {fn}, select a gga file first")
    #         return
    #
    #     with open(fn, 'r', encoding='utf-8') as f:
    #         ll = nmeaFileTodev(f)
    #
    #     figure("figure 1 deviation map")
    #     plot(ll[::3], ll[1::3], c='b', marker='+', markersize=5)
    #     title(f"{fn.split('/')[-1]} - deviation map ")
    #     xlabel("Lat / deg")
    #     ylabel("Lon / deg")
    #     grid(True)
    #     show()
    #
    #     figure("figure 2 # of sats used")
    #     plot(range(len(ll) // 3), ll[2::3], c='c')
    #     title(f"{fn.split('/')[-1]} - # of sats used ")
    #     ylabel("# of sats")
    #     grid(True)
    #     show()

    # def gtcmp(self, fn):
    #     if fn is None or self._fn is None:
    #         QMessageBox.critical(self, "Error", f"Compare {fn} with {self._fn}")
    #         return
    #
    #     ymd = self._fn.split('/')[-1]
    #     y = int(ymd[:4])
    #     m = int(ymd[4:6])
    #     d = int(ymd[6:8])
    #     dts_total_diff, hz_diff,_ = genComp(fn, self._fn, [y, m, d])
    #
    #     fig = figure('Each direction info', figsize=(10, 8))
    #     ax = fig.add_subplot(111)
    #     ax1 = fig.add_subplot(311)
    #     ax2 = fig.add_subplot(312)
    #     ax3 = fig.add_subplot(313)
    #
    #     ax1.plot(dts_total_diff[0], c='b', label='north')
    #     ax2.plot(dts_total_diff[1], c='g', label='east')
    #     ax3.plot(dts_total_diff[2], c='r', label='zenith')
    #
    #     ax1.legend()
    #     ax2.legend()
    #     ax3.legend()
    #
    #     ax1.grid(True)
    #     ax2.grid(True)
    #     ax3.grid(True)
    #
    #     # Turn off axis lines and ticks of the big subplot
    #     ax.spines['top'].set_color('none')
    #     ax.spines['bottom'].set_color('none')
    #     ax.spines['left'].set_color('none')
    #     ax.spines['right'].set_color('none')
    #     ax.tick_params(labelcolor='w', top=False, bottom=False, left=False, right=False)
    #     ax.set_xlabel('Local time - 12/23/2019')
    #     ax.set_ylabel('Difference / m')
    #     ax.set_title("Each direction difference")
    #
    #     # plot horizontal errors
    #     fig, axn = subplots('horizontal info')
    #
    #     hz_diff[0].plot(color='c', label='horizontal')
    #     axhline(y=1, color='r', linestyle='-.', lw=1.2, label='1 m error line')
    #     fig.text(0.75, 0.25, 'Powered by Feynman Innovation', fontsize=12, color='gray', ha='right', va='bottom',
    #              alpha=0.4)
    #
    #     axn.set_title("Horizontal difference plot")
    #     axn.set_xlabel('Local time - 10/09/2019')
    #     axn.set_ylabel('Difference / m')
    #
    #     axn.legend(fontsize='small', ncol=1)
    #     axn.grid(True)
    #
    #     # plot horizontal cdf
    #     fig, axh = subplots('horizontal cdf')
    #     axh.set_title('Horizontal difference cdf plot')
    #     hz_diff[0].hist(cumulative=True, density=True, bins=400, histtype='step', linewidth=2.0, label="Horizontal cdf")
    #
    #     axhline(y=.95, c='r', linestyle='-.', lw=1.2, label='95% prob line')
    #     axhline(y=.68, c='g', linestyle='-.', lw=1.2, label='68% prob line')
    #     fig.text(0.75, 0.25, 'Powered by Feynman Innovation', fontsize=12, color='gray', ha='right', va='bottom',
    #              alpha=0.4)
    #
    #     axh.set_xlabel('Error / m')
    #     axh.set_ylabel('Likelihood of horizontal difference / m')
    #     axh.legend(fontsize='small', ncol=1)
    #     axh.grid(True)
    #
    #     show()

    def mulser_control(self):
        # check  toolButton is valid
        if not ENABLE_TOOL_BTN: return
        dialog = MultiSerial()
        dialog.show()


if __name__ == '__main__':
    app = QApplication(argv)
    nst = NtripSerialTool()
    nst.show()
    exit(app.exec_())
