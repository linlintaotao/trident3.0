# -*- coding: utf-8 -*-
""" 
 Created on 11/13/2019 3:05 PM
 
 @author : chey
 
"""

from base64 import b64encode
from datetime import datetime
from os import path, stat, makedirs
from sys import argv, exit
from threading import Thread

import serial
import serial.tools.list_ports
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QTextCursor, QIcon
from PyQt5.QtNetwork import QTcpSocket
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog

from extools.nmea2kml import nmeaFileToCoords, genKmlStr
from gui.form import Ui_widget

###################################################################
OPEN = 'Open'
CLOSE = 'Close'
CONNECT = 'Connect'
DISCONNECT = 'Disconnect'

###################################################################

Freq = 2500
DUR = 1000
SEND_BYTES = 0
COLOR_TAB = {'0': 'black', '1': 'red', '2': 'red', '3': 'black', '4': 'green', '5': 'blue', '6': 'yellow'}
SERIAL_WRITE_MUTEX = False


###################################################################


def gettstr():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def sendser(file, serhd):
    global SERIAL_WRITE_MUTEX, SEND_BYTES

    if file is None or serhd is None:
        return False

    SERIAL_WRITE_MUTEX = True
    with open(file, "rb") as f:
        for line in f:
            serhd.write(line)
            SEND_BYTES += len(line)

    SERIAL_WRITE_MUTEX = False


class NtripSerialTool(QMainWindow, Ui_widget):
    """
    Ntrip serial tool for testing FMI P20 comb board
    """
    global SERIAL_WRITE_MUTEX

    def __init__(self, parent=None):
        super(NtripSerialTool, self).__init__(parent)
        self.setWindowIcon(QIcon("./gui/i.svg"))
        self._fh = None
        self._imgfile = None
        self._nmeaf = None
        self._fn = ''
        self._dir = 'NMEA'
        self.psol = '0'
        self._getmnt = b''
        self._curgga = b''
        self._caster = ''
        self._port = 0
        self._srxbs = 0
        self._stxbs = 0
        self._nrxbs = 0
        self._ntxbs = 0
        self._val = 0

        self.setupUi(self)
        self.create_items()
        self.create_sigslots()

        if not path.exists(self._dir):
            makedirs(self._dir)

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
        self.pushButton_refresh.clicked.connect(self.ser_refresh)
        self.pushButton_clear.clicked.connect(self.serecv_clear_btclik)
        self.pushButton_close.clicked.connect(self.close_all)
        self.pushButton_stop.clicked.connect(self.stop_all)

        # open image file and send it to P20 navi board
        self.open_file.clicked.connect(self.open_filed)
        self.trans_file.clicked.connect(self.trans_filed)

        # generate kml file
        self.open_nmea_file.clicked.connect(self.open_nmeaf)
        self.gen_kml.clicked.connect(self.write_kml)

        # ntrip client socket re-connection on disconnection
        self.sock.connected.connect(self.sock_conn)
        self.sock.readyRead.connect(self.sock_recv)

        self.textEdit_recv.textChanged.connect(self.text_recv_changed)

    def ser_refresh(self):
        """
        refresh current serial port list
        :return:
        """
        self.cbsport.clear()
        port_list = list(serial.tools.list_ports.comports())
        for port in port_list:
            self.cbsport.addItem(port[0])

    # serial configuration parameters
    def ser_open_btclik(self):
        """
        serial open button clicked handling
        :return:
        """
        if self.pushButton_open.text() == OPEN:
            self.com.port = self.cbsport.currentText()
            self.com.baudrate = int(self.cbsbaud.currentText())
            self.com.bytesize = int(self.cbsdata.currentText())
            self.com.stopbits = int(self.cbsstop.currentText())
            self.com.parity = self.cbsparity.currentText()
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
                self.ReadSerTimer.start(50)

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
        if not self.com.isOpen():
            return

        data = b''
        try:
            data = self.com.readline()
        except Exception as e:
            print(f"{sys._getframe().f_code.co_name}, {e}")

        if data != b'':
            if self.checkBox_savenmea.isChecked():
                if self._fh is None:
                    self._fn = self._dir + '/' + gettstr() + '.log'
                    self._fh = open(self._fn, 'wb')
                else:
                    self._fh.write(data)
            else:
                self._flush_file()
                self._fh.close()
                self._fh = None

            self._curgga = data
            self._srxbs += len(data)
            data = data.decode("utf-8", "ignore")
            self.textEdit_recv.insertPlainText(data)
            self.lineEdit_srx.setText(str(self._srxbs))
            if data.startswith(('$GNGGA', '$GPGGA')):
                self.disp_gga(data)
            elif data.startswith('$GEREF'):
                self.disp_ref(data)
            elif data.startswith('$GNZDA'):
                self.disp_zda(data)
            else:
                pass  # other nmea msgs

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
            if len(seg) < 14:
                return

            now, latdm = seg[1:3]
            londm = seg[4]
            solstat, nsats, dop, hgt = seg[6:10]
            dire = seg[-2]

            if latdm != '' and londm != '':
                if self.checkBox_ggafmt.isChecked():
                    try:
                        lat_deg = float(latdm)
                        lon_deg = float(londm)
                    except TypeError as e:
                        print(f"{e}")
                    else:
                        a = int(lat_deg / 100) + (lat_deg % 100) / 60
                        o = int(lon_deg / 100) + (lon_deg % 100) / 60
                        latdm, londm = "%.7f" % a, "%.7f" % o

                self.set_lebf_color(COLOR_TAB[solstat], 'white')
                self.lineEdit_rovlat.setText(latdm)
                self.lineEdit_rovlon.setText(londm)
                self.lineEdit_rovhgt.setText(hgt)

                self.lineEdit_solstat.setText(solstat)
                self.lineEdit_nsat.setText(nsats)
                self.lineEdit_dop.setText(dop)
                self.lineEdit_dir.setText(dire)
                self.psol = solstat
            else:
                pass  # lat, lon not a float string

    def disp_ref(self, data):
        """
        display geref string
        :param data: ref string
        :return:
        """
        if data.startswith('$GEREF') and data.endswith("\r\n"):
            seg = data.strip("\r\n").split(",")
            if len(seg) < 5:
                return
            blat, blon, bhgt, bid = seg[1:5]
            self.lineEdit_baselat.setText(blat)
            self.lineEdit_baselon.setText(blon)
            self.lineEdit_basehgt.setText(bhgt)
            self.lineEdit_baseid.setText(bid[:-3])

    def disp_zda(self, data):
        if data.startswith('$GNZDA') and data.endswith("\r\n"):
            seg = data.strip("\r\n").split(",")
            if len(seg) < 6:
                return
            hms, day, month, year = seg[1:5]
            self.lineEdit_timenow.setText(month + '/' + day + '/' + hms)

    def set_ser_params(self, enable):
        self.cbsport.setEnabled(enable)
        self.cbsbaud.setEnabled(enable)
        self.cbsdata.setEnabled(enable)
        self.cbsstop.setEnabled(enable)
        self.cbsparity.setEnabled(enable)

    def set_ntrip_params(self, enable):
        self.comboBox_caster.setEnabled(enable)
        self.comboBox_port.setEnabled(enable)
        self.comboBox_mount.setEnabled(enable)
        self.lineEdit_user.setEnabled(enable)
        self.lineEdit_pwd.setEnabled(enable)

    # get ntrip caster params, invoke NtripClient thread
    def ntp_conn_btclik(self):
        if self.pushButton_conn.text() == CONNECT:
            if self.lineEdit_user.text() == '' or self.lineEdit_pwd.text() == '':
                caster, port, mount = 'ntrips.feymani.cn', 2102, 'Obs'
                user, passwd = 'feyman-user', '123456'
            else:
                caster = self.comboBox_caster.currentText()
                port = int(self.comboBox_port.currentText())
                mount = self.comboBox_mount.currentText()
                user = self.lineEdit_user.text()
                passwd = self.lineEdit_pwd.text()

            self._port = port
            self._caster = caster
            self.sock.close()
            self.sock.open(QTcpSocket.ReadWrite)

            # get mount point and try to connect caster
            user = b64encode((user + ":" + passwd).encode('utf-8')).decode()
            self.set_mntp_str(mount, user)
            self.ntp_conn(caster, port)
            self.set_ntrip_params(False)
            self.NtripReconTimer.start(10000)
            self.pushButton_conn.setText(DISCONNECT)

        elif self.pushButton_conn.text() == DISCONNECT:
            self._term_ntrip()
            self.set_ntrip_params(True)
            self.pushButton_conn.setText(CONNECT)

    def atcmd_send_btclik(self):
        if SERIAL_WRITE_MUTEX == False:
            if self.com.isOpen():
                cmd = self.cbatcmd.currentText() + "\r\n"
                if not cmd.startswith('AT+'):
                    QMessageBox.warning(self, "Warning", "AT command start with AT+ ")
                    return

                self.com.write(cmd.encode("utf-8", "ignore"))
                if cmd == "AT+UPDATE_MODE\r\n":
                    self._term_ntrip()
                    self.set_ntrip_params(True)
                    self.pushButton_conn.setText(CONNECT)
            else:
                QMessageBox.warning(self, "Warning", "Open serial port first! ")
        else:
            QMessageBox.information(self, "Info", "Firmware updating......")

    def set_mntp_str(self, mnt, user):
        mountPointString = "GET /%s HTTP/1.1\r\nUser-Agent: %s\r\nAuthorization: Basic %s\r\n" % (
            mnt, "NTRIP FMIPythonClient/1.0", user)
        mountPointString += "\r\n"
        self._getmnt = mountPointString.encode('utf-8')

    def ntp_conn(self, caster, port):
        self.sock.connectToHost(caster, port)
        if not self.sock.waitForConnected(5000):
            msg = self.sock.errorString()
            QMessageBox.critical(self, "Error", msg)
        self.send_ggaTimer.start(10000)

    # sock connect, write get mount point request
    def sock_conn(self):
        try:
            self.sock.write(self._getmnt)
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Socket connect failed, {e}")

    # socket receive data
    def sock_recv(self):
        if SERIAL_WRITE_MUTEX == False:
            rtcm = self.sock.readAll()
            if self.com.isOpen():
                try:
                    self.com.write(rtcm)
                except serial.SerialTimeoutException as e:
                    QMessageBox.critical(self, "Error", f"{e}")
                else:
                    self._stxbs += len(rtcm)
                    self._val += 5
                    self._val = 0 if self._val > 100 else self._val
                    self.progressBar.setValue(self._val)
                    self.lineEdit_stx.setText(str(self._stxbs))
            else:
                pass
        else:
            pass

    # send gga to ntrip server
    def send_gga(self):
        if SERIAL_WRITE_MUTEX == False:
            self._flush_file()
            if self.sock.isOpen():
                if self.checkBox_sendgga.isChecked():
                    if self._curgga.decode("utf-8", "ignore").startswith(("$GNGGA", "$GPGGA")):
                        self.sock.write(self._curgga)

    def ntp_reconn(self):
        if SERIAL_WRITE_MUTEX == False:
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

    def trans_filed(self):
        global SEND_BYTES
        SEND_BYTES = 0
        if self._imgfile is None:
            QMessageBox.warning(self, "Warning", f".enc file first plz!")
        else:
            file_size = stat(self._imgfile).st_size
            self.file_transbar.setRange(0, file_size)
            trans_file = Thread(target=sendser, args=(self._imgfile, self.com))
            trans_file.start()

            self.FileTrans.start(1200)
            self.file_transbar.setValue(0)

    def ShowFilepBarr(self):
        if SERIAL_WRITE_MUTEX is True:
            self.file_transbar.setValue(SEND_BYTES)
        else:
            self.file_transbar.setValue(SEND_BYTES)
            self.FileTrans.stop()

    def open_nmeaf(self):
        filename, filetype = QFileDialog.getOpenFileName(self, "Select file", "./", "All Files (*);;Text Files (*.txt)")
        if filename != "":
            self.nmea_file.setText(filename)
            self._nmeaf = filename

    def write_kml(self):
        self.tokml(self._nmeaf)

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

        exit(0)

    # stop all stream
    def stop_all(self):
        if self.com.isOpen():
            self.com.close()
            self.set_ser_params(True)
            self.pushButton_open.setText(OPEN)

        if self.sock.isOpen():
            self._term_ntrip()
            self.pushButton_conn.setText(CONNECT)

        self._flush_file()

    # terminate ntrip connection
    def _term_ntrip(self):
        self.sock.flush()
        self.sock.close()
        self.send_ggaTimer.stop()
        self.NtripReconTimer.stop()

    def _flush_file(self):
        if self._fh is not None:
            self._fh.flush()

    def tokml(self, fn):
        fnkml = fn + '.kml'
        if path.exists(fnkml):
            over_write = QMessageBox.warning(self, "Warning", f"Over write {fnkml} ?", QMessageBox.No, QMessageBox.Yes)
        else:
            over_write = QMessageBox.Yes

        if over_write == QMessageBox.Yes:
            fo = open(fnkml, 'w')
            with open(fn, 'r', encoding='utf-8') as f:
                coords = nmeaFileToCoords(f)
                kml_str = genKmlStr(coords)
            fo.write(kml_str)
            fo.close()
            QMessageBox.information(self, "Info", f"file {fn} done")


if __name__ == '__main__':
    app = QApplication(argv)
    nst = NtripSerialTool()
    nst.show()
    exit(app.exec_())
