# -*- coding: utf-8 -*-
""" 
 Created on 11/13/2019 3:05 PM
 
 @author : chey
 
"""
# TODO: more test case

from datetime import datetime
from os import path, stat, makedirs
from sys import argv, exit
from threading import Thread
from functools import partial
from streams.Ntrip import NtripClient
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QTimer, QCoreApplication, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog

from extools.nmea2kml import KmlParse
from gui.mainwindow import Ui_Trident
from gui.multiser import Multiser_Ui_widget
from streams.WeaponUpgrade import UpgradeManager
import sys, traceback

from extools.FmiConfig import FMIConfig

from streams.QThreadSerial import SerialThread

###################################################################
DIR = 'NMEA/'
OPEN = 'Open'
CLOSE = 'Close'
CONNECT = 'Connect'
DISCONNECT = 'Disconnect'

# SWITCH_ON = [0xA0, 0x01, 0x01, 0xA2]
# SWITCH_OFF = [0xA0, 0x01, 0x00, 0xA1]
###################################################################
SEND_BYTES_LEN = 0
SAVE_NMEA = True
ENABLE_TOOL_BTN = True
SERIAL_PORT_LIST = []
SERIAL_WRITE_MUTEX = False
SERIAL_SET = [None, None, None, None]
LABEL_SHOW_LIST = [None, None, None, None]
FIRM_UPDATE_LIST = [False, False, False, False]

COLOR_TAB = {'0': 'gray', '1': 'red', '2': '#55aaff', '3': 'black', '4': 'green', '5': 'blue', '6': '#ff55ff'}

NTRIP = [None]

LAT_LON = [40, 116]

VERSION = "2.3.3"

NTRIP_CONFIG = 'NTRIP'


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


def sendser(file, serhd):
    global SERIAL_WRITE_MUTEX, SEND_BYTES_LEN

    if file is None or serhd is None:
        return False

    SERIAL_WRITE_MUTEX = True
    with open(file, "rb") as f:
        for line in f:
            serhd.send_data(line, sleepTime=0)
            SEND_BYTES_LEN += len(line)
    QThread.sleep(1)
    SERIAL_WRITE_MUTEX = False


class MultiSerial(QMainWindow, Multiser_Ui_widget):
    def __init__(self, parent=None):
        global ENABLE_TOOL_BTN
        ENABLE_TOOL_BTN = False

        super(MultiSerial, self).__init__(parent)
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
        self.btnConntet = [self.pushButton_open_1, self.pushButton_open_2, self.pushButton_open_3,
                           self.pushButton_open_4]
        self.com = [None for _ in range(nsers)]

        # self.ReadSerTimer = [QTimer() for _ in range(nsers)]
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

            self.com[spn] = SerialThread(iport=self.cbsport[spn].currentText(),
                                         baudRate=int(self.cbsbaud[spn].currentText()))
            if spn == 0:
                self.com[spn].signal.connect(self.read_ser0)
            elif spn == 1:
                self.com[spn].signal.connect(self.read_ser1)
            elif spn == 2:
                self.com[spn].signal.connect(self.read_ser2)
            elif spn == 3:
                self.com[spn].signal.connect(self.read_ser3)
            self.com[spn].setFile()
            self.com[spn].start()
            SERIAL_SET[spn] = self.com[spn]
            if NTRIP[0] is not None:
                NTRIP[0].register(self.com[spn])
            self.set_ser_params(False, spn)
            btn.setText(CLOSE)
            self._text[spn].clear()

        elif btn.text() == CLOSE:
            self.onClose((self.com[spn], spn))

    def onClose(self, serialTuple):
        spn = serialTuple[1]
        if NTRIP[0] is not None:
            NTRIP[0].unregister(serialTuple[0])
        self.com[spn].stop()
        SERIAL_PORT_LIST[spn] = None
        self.LBshow[spn].setText("closed")
        self.set_ser_params(True, spn)
        self._fh = [None for _ in range(4)]
        self._fn = ['' for _ in range(4)]
        self.btnConntet[spn].setText(OPEN)

    def read_ser0(self, data):
        self.read_ser(data, 0)

    def read_ser1(self, data):
        self.read_ser(data, 1)

    def read_ser2(self, data):
        self.read_ser(data, 2)

    def read_ser3(self, data):
        self.read_ser(data, 3)

    def read_ser(self, data, n):
        data = data.decode("utf-8", "ignore")

        if 'STOP SERIAL' in data:
            self.onClose((self.com[n], n))
            QMessageBox.critical(self, "error", f"can not open serial {self.cbsport[n].currentText()}")
            return
        elif 'READ STOP' in data:
            self.onClose((self.com[n], n))
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
                except Exception as e:
                    print(e)
                    return
                else:
                    a = int(lat_deg / 100) + (lat_deg % 100) / 60
                    o = int(lon_deg / 100) + (lon_deg % 100) / 60
                    latdm, londm = "%.8f" % a, "%.8f" % o

                stat = "{0:8s},{1:2d},{2:1d},{3:<3s}".format(now, int(nsats), int(solstat), dage)
                self.LEstat[n].setText(stat)
                self._text[n].insertPlainText(data)
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
        for com in self.com:
            if com is not None:
                com.stop()
        global ENABLE_TOOL_BTN
        ENABLE_TOOL_BTN = True
        self._exit = True


############################################################################################
class NtripSerialTool(QMainWindow, Ui_Trident):
    """
    Ntrip serial tool for testing FMI P20 comb board
    """
    global SERIAL_WRITE_MUTEX, ENABLE_TOOL_BTN

    def __init__(self, parent=None):
        super(NtripSerialTool, self).__init__(parent)
        self.setWindowIcon(QIcon("./gui/i.svg"))
        self.setWindowTitle(f"Trident %s fmi@feyman.cn" % VERSION)
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
        self.ntrip = None
        self._ggacnt = 0
        self._cold_resets = 0

        self._cold_reset_cnt = 0
        self.upgrade = None
        self.setupUi(self)
        self.create_items()
        self.create_sigslots()
        self.ser_refresh()
        self.com = None
        self.ntrip = None
        self.clearLimit = 200
        self._update_H = False
        if not path.exists(DIR):
            makedirs(DIR)
        self.params = ""
        self.wait_para = False
        self.loadConfig()

    def loadConfig(self):
        self.config = FMIConfig()
        ntripIps = self.config.getGroupKeys(NTRIP_CONFIG)
        if ntripIps is None:
            return
        casterChildren = self.comboBox_caster.children()
        for ip in ntripIps:
            if ip not in casterChildren:
                self.comboBox_caster.addItem(ip)

    def resizeEvent(self, QResizeEvent):

        if self.Infos.width() < self.Infos.minimumWidth() + 200:
            ## 隐藏平方差
            self.lat_std.setVisible(False)
            self.lon_std.setVisible(False)
            self.alt_std.setVisible(False)
            self.v_std.setVisible(False)
            self.label_lat.setVisible(False)
            self.label_lon.setVisible(False)
            self.label_alt.setVisible(False)
            self.label_v_std.setVisible(False)

            self.label_R.setVisible(False)
            self.label_P.setVisible(False)
            self.label_Y.setVisible(False)
            self.r_std.setVisible(False)
            self.p_std.setVisible(False)
            self.y_std.setVisible(False)
            pass
        else:
            ## 显示平方差
            self.lat_std.setVisible(True)
            self.lon_std.setVisible(True)
            self.alt_std.setVisible(True)
            self.v_std.setVisible(True)
            self.label_lat.setVisible(True)
            self.label_lon.setVisible(True)
            self.label_alt.setVisible(True)
            self.label_v_std.setVisible(True)

            self.label_R.setVisible(True)
            self.label_P.setVisible(True)
            self.label_Y.setVisible(True)
            self.r_std.setVisible(True)
            self.p_std.setVisible(True)
            self.y_std.setVisible(True)
            pass

    def create_items(self):
        """
            timer instance
        """
        self.ntripDataTimer = QTimer(self)
        self.ntripDataTimer.timeout.connect(self.ntp_state)

        self.FileTrans = QTimer(self)
        self.FileTrans.timeout.connect(self.ShowFilepBarr)

    def ntp_state(self):
        if not SERIAL_WRITE_MUTEX:
            if self.ntrip.isRunning():
                if self._stxbs != self.ntrip.receiveDataLength():
                    self._stxbs = self.ntrip.receiveDataLength()
                    self._val += 5
                self._val = 0 if self._val > 100 else self._val
                self.progressBar.setValue(self._val)
                self.lineEdit_stx.setText(str(self._stxbs))
                self.pushButton_conn.setText(self.ntrip.getState())

            else:
                self._term_ntrip()
                if len(self.ntrip.get_mountpoint()) > 0:
                    self.comboBox_mount.clear()
                    for port in self.ntrip.get_mountpoint():
                        self.comboBox_mount.addItem(port)
                    self.ntrip.clear()

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
        # open image file and send it to P20 navi board
        self.open_file.clicked.connect(self.open_filed)
        self.trans_file.clicked.connect(self.trans_filed)
        # generate kml file
        self.open_nmea_file.clicked.connect(self.open_nmeaf)
        self.gen_kml.clicked.connect(self.write_kml)
        # s serial received text changed
        self.textEdit_recv.textChanged.connect(self.text_recv_changed)
        # save nmea、Cors
        self.checkBox_savenmea.clicked.connect(self.save_nmea)
        # self.checkBox_logcos.clicked.connect(self.save_cors)
        self.comboBox_caster.editTextChanged.connect(self.caster_change)

    def caster_change(self):
        casterStr = self.comboBox_caster.currentText()
        value = self.config.getValue(NTRIP_CONFIG, key=casterStr)
        if value is not None and len(value) > 0:
            listNtripInfo = value.split(":")
            self.comboBox_port.setEditText(listNtripInfo[0])
            self.comboBox_mount.setEditText(listNtripInfo[1])
            self.lineEdit_user.setText(listNtripInfo[2])
            self.lineEdit_pwd.setText(listNtripInfo[3])

    def save_caster(self, key, value):
        self.config.saveNtripValue(NTRIP_CONFIG, key, value)

    def save_nmea(self):
        if self.com is not None:
            self.com.setFile(self.checkBox_savenmea.isChecked())

    # def save_cors(self):
    #     if self.ntrip is not None and self.ntrip.isRunning():
    #         self.ntrip.setLogFile(self.checkBox_logcos.isChecked())

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
    def ser_open_btclik(self, coldRestart=False):
        """
        serial open button clicked handling
        :return:
        """
        if self.pushButton_open.text() == OPEN:
            self.com = SerialThread(iport=self.cbsport.currentText(),
                                    baudRate=int(self.cbsbaud.currentText()), coldStart=coldRestart)
            self.com.signal.connect(self.read_ser_data)
            self.com.start()
            if self.checkBox_savenmea.isChecked():
                self.com.setFile(on=True)
            if self.ntrip is not None and self.ntrip.isRunning():
                self.ntrip.register(self.com)
            self.set_ser_params(False)
            if not coldRestart:
                self.textEdit_recv.clear()

        elif self.pushButton_open.text() == CLOSE:
            self.com.stop()
            if self.ntrip is not None:
                self.ntrip.unregister(self.com)
            self.set_ser_params(True)

    def read_ser_data(self, data):

        if 'STOP SERIAL' in str(data):
            self.set_ser_params(True)
            if self.ntrip is not None:
                self.ntrip.unregister(self.com)
            QMessageBox.critical(self, "error", f"can not open serial {self.cbsport.currentText()}")
            return
        elif 'READ STOP' in str(data):
            self.set_ser_params(True)
            if self.ntrip is not None:
                self.ntrip.unregister(self.com)
            return

        """
        serial port reading
        :return:
        """
        if data != b'':
            self._curgga = data
            self.clearLimit -= 1
            if self.clearLimit == 0:
                self.textEdit_recv.clear()
                self.clearLimit = 300
            self._srxbs += len(data)
            data = data.decode("utf-8", "ignore")
            try:
                if data.startswith(('$GNGGA', '$GPGGA')):
                    self.disp_gga(data)
                elif data.startswith("$GPFMI"):
                    self.disp_fmi(data)
                elif data.startswith("$GNTXT"):
                    self._cold_reseted = False

                if data.startswith("$"):
                    if len(self.params) > 0 and self.wait_para:
                        self.wait_para = False
                        QMessageBox.information(self, "FMI_PARA", self.params)
                else:
                    if self.wait_para:
                        self.params += data
            except Exception as e:
                print("parse exception", e)
            data = data.strip("\r\n")
            self.textEdit_recv.append(data)
            self.lineEdit_srx.setText(str(self._srxbs))

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
            if len(seg) < 15:
                return

            now, latdm = seg[1:3]
            londm = seg[4]
            solstat, nsats, dop, hgt = seg[6:10]
            dage = seg[-2]

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
                        LAT_LON[0] = a
                        LAT_LON[1] = o
                        if self.ntrip is not None:
                            self.ntrip.setPosition(lat=a, lon=o)
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
        week, sow = seg[2:4]
        lat, lon, alt = seg[4:7]
        latstd, lonstd, altstd = seg[7:10]
        ve, vn, vu, vstd = seg[10:14]
        y, p, r = seg[14:17]
        ystd, pstd, rstd = seg[17:20]
        bl = seg[20]

        # print(week, sow, latstd, lonstd, altstd, ve, vn, vu, vstd, y, p, r, ystd, pstd, rstd)
        if self.lat_std.isVisible():
            self.lat_std.setText(latstd)
            self.lon_std.setText(lonstd)
            self.alt_std.setText(altstd)
            self.v_std.setText(vstd)
            self.y_std.setText(ystd)
            self.p_std.setText(pstd)
            self.r_std.setText(rstd)

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
        # self.cbsdata.setEnabled(enable)
        self.pushButton_open.setText(OPEN if enable else CLOSE)
        self.pushButton_refresh.setEnabled(enable)

    def set_ntrip_params(self, enable):
        self.comboBox_caster.setEnabled(enable)
        self.comboBox_port.setEnabled(enable)
        self.comboBox_mount.setEnabled(enable)
        self.lineEdit_user.setEnabled(enable)
        self.lineEdit_pwd.setEnabled(enable)

    # get ntrip caster params, invoke NtripClient thread
    def ntp_conn_btclik(self):
        if self.pushButton_conn.text() == CONNECT:

            if self.ntrip is not None and self.ntrip.isRunning():
                self.ntrip.stop()
                self.ntrip = None
                return

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
            self.ntrip = NtripClient(ip=self._caster, port=self._port, user=user, password=passwd, mountPoint=mount,
                                     latitude=LAT_LON[0], longitude=LAT_LON[1])
            # if self.checkBox_logcos.isChecked():
            self.ntrip.setLogFile(True)
            self.ntrip.start()
            self.ntrip.register(self.com)
            NTRIP[0] = self.ntrip
            for entity in SERIAL_SET:
                self.ntrip.register(entity)
            self.set_ntrip_params(False)
            self.ntripDataTimer.start(1200)
            self.pushButton_conn.setText(DISCONNECT)

            if len(mount) > 0 and "Source Table" not in mount:
                value = f"%s:%s:%s:%s" % (port, mount, user, passwd)
                self.save_caster(self._caster, value)

        else:
            self._term_ntrip()

    # at command button handle
    def atcmd_send_btclik(self):
        if not SERIAL_WRITE_MUTEX:
            cmd = self.cbatcmd.currentText() + "\r\n"
            # if not cmd.startswith(('AT+', '$J')):
            #     QMessageBox.warning(self, "Warning", "Only support Feyman and H command")
            #     return
            # while in firmware update mode, terminate ntrip first
            if cmd in ["AT+UPDATE_MODE\r\n", "AT+UPDATE_SHELL\r\n", "AT+UPDATE_MODE_H\r\n"]:
                self._term_ntrip()
            elif 'AT+READ_PARA' in cmd:
                self.params = ""
                self.wait_para = True

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
                    if self.com.is_running():
                        self.com.send_data(cmd.encode("utf-8", "ignore"))

            else:
                if self.com is not None and self.com.is_running():

                    order = self.config.getCmdComb(cmd)
                    if isinstance(order, list):
                        for cmd in order:
                            self.com.send_data(cmd.encode("utf-8", "ignore"))
                            QThread.msleep(100)
                    else:
                        self.com.send_data(cmd.encode("utf-8", "ignore"))
                    # if 'AT+VEH_MODE' in cmd:
                    #     for cmd in ['AT+NAVI_RATE=5\r\n', 'AT+GPGGA=UART1,1\r\n', 'AT+GPRMC=UART1,1\r\n',
                    #                 'AT+GPREF=UART1,0.1\r\n', 'AT+WORK_MODE=13\r\n', 'AT+DR_TIME=600\r\n',
                    #                 'AT+ALIGN_VEL=3\r\n', 'AT+RTK_DIFF=5\r\n', 'AT+SAVE_ALL\r\n',
                    #                 'AT+READ_PARA\r\n', 'AT+WARM_RESET\r\n']:
                    #         self.com.send_data(cmd.encode("utf-8", "ignore"))
                    #         QThread.msleep(100)
                    # elif 'AT+UAV_MODE' in cmd:
                    #     for cmd in ['AT+NAVI_RATE=10\r\n', 'AT+GPGGA=UART1,10\r\n', 'AT+GPRMC=UART1,10\r\n',
                    #                 'AT+GPREF=UART1,0.1\r\n', 'AT+WORK_MODE=8\r\n', 'AT+DR_TIME=10\r\n',
                    #                 'AT+ALIGN_VEL=0.5\r\n', 'AT+RTK_DIFF=5\r\n', 'AT+SAVE_ALL\r\n',
                    #                 'AT+READ_PARA\r\n', 'AT+WARM_RESET\r\n']:
                    #         self.com.send_data(cmd.encode("utf-8", "ignore"))
                    #         QThread.msleep(100)
                    # else:
                    #     self.com.send_data(cmd.encode("utf-8", "ignore"))
                else:
                    QMessageBox.warning(self, "Warning", "Open serial port first! ")
        else:
            QMessageBox.information(self, "Info", "Firmware updating......")

    def serecv_clear_btclik(self):
        self._srxbs = 0
        self._stxbs = 0
        self.textEdit_recv.clear()

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Return:
            self.atcmd_send_btclik()

    # text cursor at end
    def text_recv_changed(self):
        if self.checkBox_autoScoll.isChecked():
            self.textEdit_recv.moveCursor(QTextCursor.End)

    def open_filed(self):
        self._term_ntrip()
        filename, filetype = QFileDialog.getOpenFileName(self, "Select file", "./", "All Files (*);;Text Files (*.txt)")
        if filename != "" and not filename.endswith(".enc"):
            QMessageBox.warning(self, "Warning", f"Please select proper .enc file", QMessageBox.Ok)
            return
        else:
            self.lineEdit_filename.setText(filename)
            self._imgfile = filename

    def update_firm2(self, file: str, serhd, baudrate) -> None:
        global SERIAL_WRITE_MUTEX
        if file is None or serhd is None:
            return
        SERIAL_WRITE_MUTEX = True
        self.upgrade = UpgradeManager(port=serhd, file=file, updateBaudrate=baudrate)
        self.upgrade.signal.connect(self.updateTrans)
        self.upgrade.start()

    # send file to serial
    def trans_filed(self):
        global SEND_BYTES_LEN
        SEND_BYTES_LEN = 0
        if self._imgfile is None:
            QMessageBox.warning(self, "Warning", f".enc file first plz!")
        else:
            info = self.cbsport.currentText()
            file_size = stat(self._imgfile).st_size
            self.file_transbar.setRange(0, file_size)

            if 'AT+UPDATE_MODE' in self.cbatcmd.currentText() or 'AT+UPDATE_SHELL' in self.cbatcmd.currentText():
                self._update_H = False
                ret = QMessageBox.warning(self, "Warning", f"update serial {info}", QMessageBox.No, QMessageBox.Yes)
                if ret == QMessageBox.No:
                    return
                Thread(target=sendser, args=(self._imgfile, self.com)).start()
                # sendser(self._imgfile, self.com)
            else:
                ret = QMessageBox.warning(self, "Warning", f"Is this Evk support Blue-Tooth?",
                                          QMessageBox.No,
                                          QMessageBox.Yes)
                baudrate = 115200
                if ret == QMessageBox.No:
                    baudrate = 460800
                self.ser_open_btclik()
                self._update_H = True
                Thread(target=self.update_firm2, args=(self._imgfile, info, baudrate)).start()
            self.FileTrans.start(200)
            self.file_transbar.setValue(0)

    def ShowFilepBarr(self):
        # print(SERIAL_WRITE_MUTEX)
        try:
            if SERIAL_WRITE_MUTEX:
                self.file_transbar.setValue(SEND_BYTES_LEN)
            else:
                self.FileTrans.stop()
                self.updateComplete()
        except KeyboardInterrupt as e:
            print(e)

    def updateComplete(self):
        if self._update_H:
            self.ser_open_btclik(coldRestart=self.checkBox_reset.isChecked())
        # else:
        #     self.com.send_data('AT+COLD_RESET\r\n')

    # close window
    def close_all(self):
        self.stop_all()
        exit(0)

    # stop all stream
    def stop_all(self):
        # self.pushButton_refresh.setEnabled(True)
        if self.com is not None and self.com.is_running():
            self.com.stop()
            self.set_ser_params(True)
            # self.pushButton_open.setText(OPEN)
        self._term_ntrip()

    # terminate ntrip connection
    def _term_ntrip(self):
        if self.ntrip is not None:
            self.ntrip.stop()

        NTRIP[0] = None
        self.ntripDataTimer.stop()
        self.set_ntrip_params(True)
        self.progressBar.setValue(0)
        self.pushButton_conn.setText(CONNECT)

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
            kmlparser = KmlParse(fn, header)
            kmlparser.singal.connect(self.showMessage)
            kmlparser.start()
            kmlparser.exec()

    def showMessage(self, info):
        QMessageBox.information(self, "Info", f"Parse KML done\n"
                                              f"Statistics\n{info}")

    def updateTrans(self, isUpdateing, sendBytes, dataLen):
        global SEND_BYTES_LEN, SERIAL_WRITE_MUTEX
        SERIAL_WRITE_MUTEX = isUpdateing
        if len(sendBytes) > 0:
            self.textEdit_recv.append(sendBytes.decode('utf-8', 'ignore'))
        SEND_BYTES_LEN = dataLen

    def mulser_control(self):
        # check  toolButton is valid
        if not ENABLE_TOOL_BTN: return
        dialog = MultiSerial()
        dialog.show()

    def closeEvent(self, QCloseEvent):
        self.close_all()


def my_excepthook(ex_cls, ex, tb):
    # import traceback
    error.start()


def showDialog():
    errBox = QMessageBox(QMessageBox.Critical, 'ERROR', 'Oops!!! \r\n'
                                                        'There’s something wrong with Trident !!!\r\n'
                                                        'You can send err.log under NMEA to FMI for repair ！')
    app.exit(errBox.exec_())


class Error(QThread):
    signal = pyqtSignal()

    def __init__(self):
        super().__init__()

    def run(self):
        traceback.print_last(file=open('NMEA/err.log', 'w+'))
        self.signal.emit()


if __name__ == '__main__':
    sys.excepthook = my_excepthook
    error = Error()
    error.signal.connect(showDialog)

    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(argv)
    nst = NtripSerialTool()
    nst.show()
    exit(app.exec_())
