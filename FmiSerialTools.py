# -*- coding: utf-8 -*-
""" 
 Created on 11/13/2019 3:05 PM
 
 @author : chey
 
"""

import sys
from base64 import b64encode
from threading import Thread, Timer
from datetime import datetime
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import QTextCursor, QIcon
from PyQt5.QtCore import QTimer
from PyQt5.QtNetwork import QTcpSocket
from gui.form import Ui_Form

OPEN = 'Open'
CLOSE = 'Close'
CONNECT = 'Connect'
DISCONNECT = 'Disconnect'

COLOR_TAB = {'0':'black', '1': 'red', '2': 'red', '3':'black', '4':'green', '5':'blue', '6':'yellow'}

def gettstr():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

class NtirpConnCheck():
    def __init__(self, interval, hfunc):
        self.intv = interval
        self.func = hfunc
        self.thread = Timer(self.intv, self.cycfunc)

    def cycfunc(self):
        self.func()
        self.thread = Timer(self.intv, self.cycfunc)
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()

class NtripSerialTool(QMainWindow, Ui_Form):
    """
    Ntrip serial tool for testing FMI P20 comb board
    """

    def __init__(self, parent=None):
        super(NtripSerialTool, self).__init__(parent)
        self.setWindowIcon(QIcon("./gui/i.svg"))
        self._fh = None
        self._tmpggadata = ''
        self._tmprefdata = ''
        self._getmnt = b''
        self._curgga = ''
        self._caster = ''
        self._port = 0
        self._srxbs = 0
        self._stxbs = 0
        self._nrxbs = 0
        self._ntxbs = 0
        self._val = 0
        self.setupUi(self)
        self.CreateItems()
        self.CreateSignalSlot()

    def CreateItems(self):
        """
        create serial, socket, timer instance
        :return:
        """
        self.com = QSerialPort()
        self.sock = QTcpSocket()

        self.SendGGATimer = QTimer(self)
        self.SendGGATimer.timeout.connect(self.SendGGA)
        self.SendGGATimer.start(10000)

        self.NtripCheck = NtirpConnCheck(10, self.NtripRecon)
        self.NtripCheck.start()
        # self.NtripReconTimer = QTimer(self)
        # self.NtripReconTimer.timeout.connect(self.NtripRecon)
        # self.NtripReconTimer.start(10000)

    def CreateSignalSlot(self):
        """
        connect signal with slots
        :return:
        """
        self.pushButton_open.clicked.connect(self.SOpenBtClick)
        self.pushButton_conn.clicked.connect(self.NConnBtClick)
        self.pushButton_atcmd.clicked.connect(self.AtCmdBtClick)
        self.pushButton_refresh.clicked.connect(self.SRefreshBtClick)
        self.pushButton_clear.clicked.connect(self.SRecvClearBtClick)
        self.pushButton_close.clicked.connect(self.CloseAll)
        self.pushButton_stop.clicked.connect(self.StopAll)

        self.com.readyRead.connect(self.SerialRecvData)
        self.sock.connected.connect(self.SockConnect)
        self.sock.readyRead.connect(self.SockRecv)

        self.textEdit_recv.textChanged.connect(self.TextRecvChanged)

    def SRefreshBtClick(self):
        """
        refresh current serial port list
        :return:
        """
        self.cbsport.clear()
        com = QSerialPort()
        com_list = QSerialPortInfo.availablePorts()
        for info in com_list:
            com.setPort(info)
            if com.open(QSerialPort.ReadWrite):
                self.cbsport.addItem(info.portName())
                com.close()

    # serial configuration parameters
    def SOpenBtClick(self):
        """
        serial open button clicked handling
        :return:
        """
        if self.pushButton_open.text() == OPEN:
            self.com.setPortName(self.cbsport.currentText())
            self.com.setBaudRate(int(self.cbsbaud.currentText()))
            self.com.setDataBits(int(self.cbsdata.currentText()))
            self.com.setStopBits(int(self.cbsstop.currentText()))
            # self.com.setParity(self.cbsparity.currentText())
            try:
                self.com.open(QSerialPort.ReadWrite)
            except Exception as e:
                print(f"{sys._getframe().f_code.co_name}, {e}")
            else:
                self.SetSerialPara(False)
                self.pushButton_open.setText(CLOSE)
                self.pushButton_refresh.setEnabled(False)
        elif self.pushButton_open.text() == CLOSE:
            self.com.close()
            self.SetSerialPara(True)
            self.pushButton_open.setText(OPEN)
            self.pushButton_refresh.setEnabled(True)

    def SerialRecvData(self):
        """
        serial port reading
        :return:
        """
        try:
            data = bytes(self.com.readAll())
        except Exception as e:
            QMessageBox.critical(self, "Critial", "Serial read error")
            print(f"{sys._getframe().f_code.co_name}, {e}")
            # self.com.close()
        else:
            self._curgga = data
            self._srxbs += len(data)
            data = data.decode("utf-8", "ignore")
            try:
                if self.checkBox_savenmea.isChecked():
                    if self._fh is None:
                        self._fh = open(gettstr() + '.log', 'w')
                    else:
                        self._fh.write(data)
                else:
                    self._fh = None
            except Exception as e:
                print(f"{e}")
            self.textEdit_recv.insertPlainText(data)
            self.lineEdit_srx.setText(str(self._srxbs))
            self.DisplayGGA(data)

    def SetBFColor(self, bg, fg):
        self.lineEdit_rovlat.setStyleSheet('background-color:'+bg+'; color:'+fg)
        self.lineEdit_rovlon.setStyleSheet('background-color:'+bg+'; color:'+fg)
        self.lineEdit_rovhgt.setStyleSheet('background-color:'+bg+'; color:'+fg)
        self.lineEdit_solstat.setStyleSheet('background-color:'+bg+'; color:'+fg)

    def DisplayGGA(self, data):
        """
        display gga string
        :param data: gga string
        :return:
        """
        if len(data.strip("\r\n").split(",")) <= 14:
            self._tmpggadata += data
        else:
            self._tmpggadata = data

        if self._tmpggadata.startswith('$GNGGA') and self._tmpggadata.endswith("\r\n"):
            seg = self._tmpggadata.strip("\r\n").split(",")
            now, latdm = seg[1:3]
            londm = seg[4]
            solstat, nsats, dop, hgt = seg[6:10]
            dire = seg[-2]

            if latdm != '' and londm != '':
                if self.checkBox_ggafmt.isChecked():
                    lat_deg = float(latdm)
                    lon_deg = float(londm)
                    a = int(lat_deg / 100) + (lat_deg % 100) / 60
                    o = int(lon_deg / 100) + (lon_deg % 100) / 60
                    latdm, londm = "%.7f" % a, "%.7f" % o

                self.SetBFColor(COLOR_TAB[solstat], 'white')
                self.lineEdit_timenow.setText(now)
                self.lineEdit_rovlat.setText(latdm)
                self.lineEdit_rovlon.setText(londm)
                self.lineEdit_rovhgt.setText(hgt)

                self.lineEdit_solstat.setText(solstat)
                self.lineEdit_nsat.setText(nsats)
                self.lineEdit_dop.setText(dop)
                self.lineEdit_dir.setText(dire)
            else:
                pass
            self._tmpggadata = ""

    def DisplayRef(self, data):
        """
        display geref string
        :param data: ref string
        :return:
        """
        if len(data.strip("\r\n").split(",")) <= 4:
            self._tmprefdata += data
        else:
            self._tmprefdata = data

        if self._tmprefdata.startswith('$GEREF') and self._tmprefdata.endswith("\r\n"):
            seg = self._tmprefdata.strip("\r\n").split(",")
            blat, blon, bhgt, bid = seg[1:5]
            self.lineEdit_baselat.setText(blat)
            self.lineEdit_baselon.setText(blon)
            self.lineEdit_basehgt.setText(bhgt)
            self.lineEdit_baseid.setText(bid)
            self._tmprefdata = ""

    def SetSerialPara(self, enable):
        self.cbsport.setEnabled(enable)
        self.cbsbaud.setEnabled(enable)
        self.cbsdata.setEnabled(enable)
        self.cbsstop.setEnabled(enable)
        self.cbsparity.setEnabled(enable)

    def SetNtripPara(self, enable):
        self.comboBox_caster.setEnabled(enable)
        self.comboBox_port.setEnabled(enable)
        self.comboBox_mount.setEnabled(enable)
        self.lineEdit_user.setEnabled(enable)
        self.lineEdit_pwd.setEnabled(enable)

    # get ntrip caster params, invoke NtripClient thread
    def NConnBtClick(self):
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

            self._caster = caster
            self._port = port
            if not self.sock.isOpen():
                self.sock.open(QTcpSocket.ReadWrite)

            # get mount point and try to connect caster
            user = b64encode((user + ":" + passwd).encode('utf-8')).decode()
            self.setMountPointString(mount, user)
            self.NtripConnect(caster, port)
            self.SetNtripPara(False)
            self.pushButton_conn.setText(DISCONNECT)

        elif self.pushButton_conn.text() == DISCONNECT:
            self._TerminateNtrip()


    def AtCmdBtClick(self):
        cmd = self.cbatcmd.currentText() + "\r\n"
        if not cmd.startswith('AT+'):
            QMessageBox.warning(self, "Warning", "AT command start with AT+ ")
        self.com.write(cmd.encode("utf-8", "ignore"))

    def setMountPointString(self, mnt, user):
        mountPointString = "GET /%s HTTP/1.1\r\nUser-Agent: %s\r\nAuthorization: Basic %s\r\n" % (
            mnt, "NTRIP FMIPythonClient/1.0", user)
        mountPointString += "\r\n"
        self._getmnt = mountPointString.encode('utf-8')

    def NtripConnect(self, caster, port):
        self.sock.connectToHost(caster, port)
        if not self.sock.waitForConnected(5000):
            msg = self.sock.errorString()
            QMessageBox.critical(self, "Error", msg)



    # sock connect, write get mount point request
    def SockConnect(self):
        try:
            self.sock.write(self._getmnt)
        except Exception as e:
            QMessageBox.warning(self, "Warning", "Socket connect failed")

    # socket receive data
    def SockRecv(self):
        rtcm = self.sock.readAll()
        if self.com.isOpen():
            try:
                self.com.write(rtcm)
            except Exception as e:
                print(f"{e}")
            else:
                self._stxbs += len(rtcm)
                self._val += 5
                self._val = 0 if self._val > 100 else self._val
                self.progressBar.setValue(self._val)
                self.lineEdit_stx.setText(str(self._stxbs))
        else:
            print(f"Open serial first please")

    # send gga to ntrip server
    def SendGGA(self):
        if self._fh is not None:
            self._fh.flush()

        if self.sock.isOpen():
            if self.checkBox_sendgga.isChecked():
                if self._curgga.decode("utf-8").startswith("$GNGGA"):
                    self.sock.write(bytes(self._curgga))

    def NtripRecon(self):
        if self.sock.isOpen():
            print(f"Ntrip connection check {datetime.now()}")
            if not self.sock.waitForReadyRead(5000):
                self.sock.flush()
                self.sock.close()
                self.NtripConnect(self._caster, self._port)
        else:
            pass # socket not open yet!

    # clear serial received data
    def SRecvClearBtClick(self):
        self.textEdit_recv.clear()

    # text cursor at end
    def TextRecvChanged(self):
        self.textEdit_recv.moveCursor(QTextCursor.End)

    # close window
    def CloseAll(self):
        self.NtripCheck.cancel()
        if self.com.isOpen():
            self.com.flush()
            self.com.close()

        if self.sock.isOpen():
            self._TerminateNtrip()

        if self._fh is not None:
            self._fh.flush()
            self._fh.close()
        exit(0)

    # stop all stream
    def StopAll(self):
        if self.com.isOpen():
            self.com.close()
            self.SetSerialPara(True)
            self.pushButton_open.setText(OPEN)

        if self.sock.isOpen():
            self._TerminateNtrip()

    # terminate ntrip connection
    def _TerminateNtrip(self):
        self.sock.flush()
        self.sock.close()
        self.SetNtripPara(True)
        self.pushButton_conn.setText(CONNECT)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    nst = NtripSerialTool()
    nst.show()
    sys.exit(app.exec_())
