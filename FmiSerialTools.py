# -*- coding: utf-8 -*-
""" 
 Created on 11/13/2019 3:05 PM
 
 @author : chey
 
"""

"""
TODO:   1. log cors data 
        2. multi serial port support
"""

from base64 import b64encode
from datetime import datetime
from os import path, stat, makedirs
from sys import argv, exit
from threading import Thread
# from matplotlib.pyplot import figure, plot, title, xlabel, ylabel, show, grid, subplots, axhline

import serial
import serial.tools.list_ports
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QTextCursor, QIcon
from PyQt5.QtNetwork import QTcpSocket
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog

from extools.nmea2kml import nmeaFileToCoords, genKmlStr
# from extools.comp_gga_analysis import genComp
from gui.form import Ui_widget
from gui.multiser import MUi_widget

###################################################################
OPEN = 'Open'
CLOSE = 'Close'
CONNECT = 'Connect'
DISCONNECT = 'Disconnect'

###################################################################

Freq = 2500
DUR = 1000
SEND_BYTES = 0
COLOR_TAB = {'0': 'black', '1': 'red', '2': 'red', '3': 'black',
             '4': 'green', '5': 'blue', '6': 'yellow'}
SERIAL_WRITE_MUTEX = False


###################################################################
# TODO   misc plots, compare with ground truth file

def gettstr():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def refresh_ser():
    port_list = list(serial.tools.list_ports.comports())
    return port_list

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


class MultiSerial(QMainWindow, MUi_widget):
    def __init__(self, parent=None):
        super(MultiSerial, self).__init__(parent)
        self.setupUi(self)
        self.ser_refresh()

    def ser_refresh(self):
        """
        refresh current serial port list
        :return:
        """
        self.cbsport.clear()
        self.cbsport_2.clear()
        self.cbsport_3.clear()
        self.cbsport_4.clear()
        port_list = refresh_ser()
        for port in port_list:
            self.cbsport.addItem(port[0])
            self.cbsport_2.addItem(port[0])
            self.cbsport_3.addItem(port[0])
            self.cbsport_4.addItem(port[0])




class NtripSerialTool(QMainWindow, Ui_widget):
    """
    Ntrip serial tool for testing FMI P20 comb board
    """
    global SERIAL_WRITE_MUTEX

    def __init__(self, parent=None):
        super(NtripSerialTool, self).__init__(parent)
        self.setWindowIcon(QIcon("./gui/i.svg"))
        self._fh = None
        self._fhcors = None
        self._imgfile = None
        self._nmeaf = None
        self._fn = ''
        self._dir = 'NMEA'

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

        self._cold_reset_cnt = 0
        self.setupUi(self)
        self.create_items()
        self.create_sigslots()
        self.ser_refresh()
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
        self.pushButton_clear.clicked.connect(self.serecv_clear_btclik)
        self.pushButton_close.clicked.connect(self.close_all)
        self.pushButton_stop.clicked.connect(self.stop_all)

        self.pushButton_multi.clicked.connect(self.mulser_control)
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

        self.textEdit_recv.textChanged.connect(self.text_recv_changed)

    def ser_refresh(self):
        """
        refresh current serial port list
        :return:
        """
        self.cbsport.clear()
        port_list = refresh_ser()
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
                self.pushButton_multi.setEnabled(False)
                self.ReadSerTimer.start(50)

        elif self.pushButton_open.text() == CLOSE:
            self.ReadSerTimer.stop()
            self.com.close()
            self.set_ser_params(True)
            self.pushButton_open.setText(OPEN)
            self.pushButton_multi.setEnabled(True)

    def read_ser_data(self):
        """
        serial port reading
        :return:
        """
        if not self.com.isOpen(): return

        data = self.com.readline()
        if data != b'':
            if self.checkBox_savenmea.isChecked():
                if self._fh is None:
                    if self._fn == '':
                        self._fn = self._dir + '/' + gettstr()
                    self._fh = open(self._fn+'.log', 'wb')
                else:
                    self._fh.write(data)
            else:
                if self._fh is not None:
                    self._flush_file()
                    self._fh.close()
                    self._fh = None

            self._curgga = data
            self._srxbs += len(data)
            data = data.decode("utf-8", "ignore")
            self.textEdit_recv.insertPlainText(data)
            self.lineEdit_srx.setText(str(self._srxbs))

            if data.startswith(('$GNGGA', '$GPGGA')):
                try:
                    self.disp_gga(data)
                except Exception as e:
                    print(f'{e}')
            elif data.startswith("$GPFMI"):
                try:
                    self.disp_fmi(data)
                except Exception as e:
                    print(f'{e}')
            elif data.startswith("Rtk Boot"):
                self._cold_reseted = False
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
            if len(seg) < 14: return

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
                        latdm, londm = "%.7f" % a, "%.7f" % o

                self.set_lebf_color(COLOR_TAB[solstat], 'white')
                self.lineEdit_rovlat.setText(latdm)
                self.lineEdit_rovlon.setText(londm)
                self.lineEdit_rovhgt.setText(hgt)
                self.lineEdit_solstat.setText(solstat)
                self.lineEdit_sats.setText(nsats)
                self.lineEdit_time.setText(now)
                self.lineEdit_dage.setText(dage)

                # test cold reset
                # if solstat == '4' and self._cold_reseted == False:
                #     cmd = "AT+COLD_RESET\r\n"
                #     try:
                #         self.com.write(cmd.encode("utf-8", "ignore"))
                #         self.com.write(cmd.encode("utf-8", "ignore"))
                #         self.com.write(cmd.encode("utf-8", "ignore"))
                #         self.com.write(cmd.encode("utf-8", "ignore"))
                #         self.com.write(cmd.encode("utf-8", "ignore"))
                #     except Exception as e:
                #         print(f'{e}')
                #     self._cold_reset_cnt += 1
                #     # dage show cold reset counts
                #     self.lineEdit_dage.setText(str(self._cold_reset_cnt))
                #     self._cold_reseted = True
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
            caster = self.comboBox_caster.currentText()
            port = int(self.comboBox_port.currentText())
            mount = self.comboBox_mount.currentText()

            if self.lineEdit_user.text() == '' or self.lineEdit_pwd.text() == '':
                user, passwd = 'feyman', '123456'
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
        if SERIAL_WRITE_MUTEX == False:
            if self.com.isOpen():
                cmd = self.cbatcmd.currentText() + "\r\n"
                if not cmd.startswith('AT+'):
                    QMessageBox.warning(self, "Warning", "AT command start with AT+ ")
                    return

                if cmd == "AT+GPFMI\r\n":
                    cmd = "AT+GPFPD\r\n"
                self.com.write(cmd.encode("utf-8", "ignore"))
                if cmd == "AT+UPDATE_MODE\r\n" or cmd == "AT+UPDATE_SHELL\r\n":
                    self._term_ntrip()
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
        if SERIAL_WRITE_MUTEX == False:
            try:
                rtcm = self.sock.readAll()

                # source cors host mount point
                if self._mnt_updated is False and b'SOURCETABLE 200 OK' in rtcm:
                    resp_list = bytes(rtcm).decode().split("\r\n")[6:]
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
                            self._fn = self._dir + '/' + gettstr()
                        self._fhcors = open(self._fn+'.cors', 'wb')
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
                    self._val += 5
                    self.progressBar.setValue(self._val%100)
                    self.lineEdit_stx.setText(str(self._stxbs))
                else:
                    pass
            except Exception as e:
                print(f'{e}')
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

    # ntirp reconnection
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

    # send file to serial
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
                kml_str = genKmlStr(coords, header)
            fo.write(kml_str)
            fo.close()

            QMessageBox.information(self, "Info", f"file {fn} done")

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
        pass
        # dialog = MultiSerial(self)
        # dialog.show()

if __name__ == '__main__':
    app = QApplication(argv)
    nst = NtripSerialTool()
    nst.show()
    exit(app.exec_())
