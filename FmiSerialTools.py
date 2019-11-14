# -*- coding: utf-8 -*-
""" 
 Created on 11/13/2019 3:05 PM
 
 @author : chey
 
"""

import sys
from base64 import b64encode
from datetime import datetime
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import QTimer, QThread
from PyQt5.QtNetwork import QTcpSocket
from gui.form import Ui_Form
from streams import NtripClient

OPEN = 'Open'
CLOSE = 'Close'
CONNECT = 'Connect'
DISCONNECT = 'Disconnect'


def gettstr():
    return datetime.now().strftime("%Y%m%d%H%M%S")


class NtripThread(QThread):
    def __init__(self, ntrip):
        super(NtripThread, self).__init__()
        self.ntrip = ntrip

    def run(self):
        self.ntrip.readData()

    def __del__(self):
        self.wait()


# TODO: serial and ntrip status info display
class MyMainWindow(QMainWindow, Ui_Form):
    def __init__(self, parent=None):
        """

        :param parent:
        """
        super(MyMainWindow, self).__init__(parent)
        self.fh = None
        self.ntrip = None
        self.CorsThread = None

        self.found_header = False
        self.tmpggadata = ''
        self.tmprefdata = ''
        self.getmnt = b''
        self.curgga = ''
        self.srxbs = 0
        self.stxbs = 0
        self.nrxbs = 0
        self.ntxbs = 0
        self.setupUi(self)
        self.CreateItems()
        self.CreateSignalSlot()

    def CreateItems(self):
        """

        :return:
        """
        self.com = QSerialPort()
        self.sock = QTcpSocket()
        # self.NtripTimer = QTimer(self)
        # self.NtripTimer.timeout.connect(self.ImportCors)
        # self.NtripTimer.start(100)
        self.SendGGATimer = QTimer(self)
        self.SendGGATimer.timeout.connect(self.SendGGA)
        self.SendGGATimer.start(10000)

    def CreateSignalSlot(self):
        """

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
        self.sock.disconnected.connect(self.SockDisconnect)
        self.sock.readyRead.connect(self.SockRecv)

        self.textEdit_recv.textChanged.connect(self.TextRecvChanged)

    # refresh serial
    def SRefreshBtClick(self):
        """

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

    def SetSerialPara(self, enable):
        """

        :param enable:
        :return:
        """
        self.cbsport.setEnabled(enable)
        self.cbsbaud.setEnabled(enable)
        self.cbsdata.setEnabled(enable)
        self.cbsstop.setEnabled(enable)
        self.cbsparity.setEnabled(enable)

    def SetNtripPara(self, enable):
        """

        :param enable:
        :return:
        """
        self.comboBox_caster.setEnabled(enable)
        self.comboBox_port.setEnabled(enable)
        self.comboBox_mount.setEnabled(enable)
        self.lineEdit_user.setEnabled(enable)
        self.lineEdit_pwd.setEnabled(enable)

    # serial configuration parameters
    def SOpenBtClick(self):
        """

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
                QMessageBox.critical(self, 'Critical', f"{sys._getframe().f_code.co_name}, {e}")
            else:
                self.SetSerialPara(False)
                # revert push button text label
                self.pushButton_open.setText(CLOSE)
        elif self.pushButton_open.text() == CLOSE:
            self.com.close()
            self.SetSerialPara(True)
            self.pushButton_open.setText(OPEN)

    # serial received data display
    # TODO: gga info textEdit display
    def SerialRecvData(self):
        """

        :return:
        """
        try:
            data = bytes(self.com.readAll())
            self.curgga = data
            self.srxbs += len(data)
            data = data.decode("utf-8", "ignore")
            if self.checkBox_savenmea.isChecked():
                if self.fh is None:
                    self.fh = open(gettstr() + '.log', 'w')
                else:
                    self.fh.write(data)
            else:
                self.fh = None
        except Exception as e:
            print(f"{sys._getframe().f_code.co_name}, {e}")
            # self.com.close()
        else:
            self.textEdit_recv.insertPlainText(data)
            self.lineEdit_srx.setText(str(self.srxbs))
            self.lineEdit_stx.setText(str(self.stxbs))
            self.DisplayGGA(data)


    def DisplayGGA(self, data):
        if len(data.strip("\r\n").split(",")) <= 14:
            self.tmpggadata += data
        else:
            self.tmpggadata = data

        if self.tmpggadata.startswith('$GNGGA') and self.tmpggadata.endswith("\r\n"):
            seg = self.tmpggadata.strip("\r\n").split(",")
            now, latdm = seg[1:3]
            londm = seg[4]
            solstat, nsats, dop, hgt = seg[6:10]
            dire = seg[-2]

            if self.checkBox_ggafmt.isChecked():
                lat_deg = float(latdm)
                lon_deg = float(londm)
                a = int(lat_deg / 100) + (lat_deg % 100) / 60
                o = int(lon_deg / 100) + (lon_deg % 100) / 60
                latdm, londm = "%.7f" % a, "%.7f" % o
            self.lineEdit_timenow.setText(now)
            self.lineEdit_rovlat.setText(latdm)
            self.lineEdit_rovlon.setText(londm)
            self.lineEdit_rovhgt.setText(hgt)

            self.lineEdit_solstat.setText(solstat)
            self.lineEdit_nsat.setText(nsats)
            self.lineEdit_dop.setText(dop)
            self.lineEdit_dir.setText(dire)
            self.tmpggadata = ""

    def DisplayRef(self, data):
        if len(data.strip("\r\n").split(",")) <= 4:
            self.tmprefdata += data
        else:
            self.tmprefdata = data

        if self.tmprefdata.startswith('$GEREF') and self.tmprefdata.endswith("\r\n"):
            seg = self.tmprefdata.strip("\r\n").split(",")
            blat, blon, bhgt, bid = seg[1:5]
            self.lineEdit_baselat.setText(blat)
            self.lineEdit_baselon.setText(blon)
            self.lineEdit_basehgt.setText(bhgt)
            self.lineEdit_baseid.setText(bid)
            self.tmprefdata = ""

    # get ntrip caster params, invoke NtripClient thread
    def NConnBtClick(self):
        """

        :return:
        """
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
            # create & start ntrip client thread
            if self.ntrip is None:
                try:
                    user = b64encode((user+":"+passwd).encode('utf-8')).decode()
                    self.setMountPointString(mount, user)
                    self.NtripConnect(caster, port, mount, user, passwd)
                    self.sock.connectToHost(caster, port)
                    if not self.sock.waitForConnected(5000):
                        msg = self.sock.errorString()
                        print(f"{msg}")

                    # self.ntrip = NtripClient.NtripClient(caster=caster, port=port, mountpoint=mount, user=user,
                    #                                      passwd=passwd)
                    # self.CorsThread = NtripThread(self.ntrip)
                    # self.CorsThread.start()
                    # self.SetNtripPara(False)
                    self.pushButton_conn.setText(DISCONNECT)
                except Exception as e:
                    print(f"{e}")
        elif self.pushButton_conn.text() == DISCONNECT:
            # terminate ntrip client thread
            self._TerminateNtrip()

    # send AT command
    def AtCmdBtClick(self):
        """
        while AT command button clicked ntrip data must not imported into serial
        :return:
        """
        # if self.ntrip is not None and self.CorsThread is not None:
        if not self.sock.disconnected():
            self._TerminateNtrip()

        cmd = self.cbatcmd.currentText() + "\r\n"
        if not cmd.startswith('AT+'):
            QMessageBox.warning(self, "Warning", "AT command start with AT+ ")
        self.com.write(cmd.encode("utf-8", "ignore"))
        print(f"AT cmd {cmd}")

    # # import cors rtcm data into serial
    # def ImportCors(self):
    #     """
    #
    #     :return:
    #     """
    #     if self.ntrip is not None and self.CorsThread is not None:
    #         if self.com.isOpen():
    #             try:
    #                 data = self.ntrip.data.pop()
    #                 self.com.write(data)
    #                 self.stxbs += len(data)
    #                 self.progressBar.setValue(self.stxbs % 100)
    #             except IndexError as e:
    #                 pass
    #         else:
    #             print(f"Open serial first please")
    #     # else:
    #     #     print(f"No valid ntrip or cors thread instance")

    def setMountPointString(self, mnt, user):
        mountPointString = "GET /%s HTTP/1.1\r\nUser-Agent: %s\r\nAuthorization: Basic %s\r\n" % (
                             mnt, "NTRIP FMIPythonClient/1.0", user)
        mountPointString += "\r\n"
        self.getmnt = mountPointString.encode('utf-8')

    def NtripConnect(self, caster, port, mnt, user, passwd):
        self.sock.connectToHost(caster, port)
        if not self.sock.waitForConnected(5000):
            msg = self.sock.errorString()
            print(f"{msg}")
            QMessageBox.critical(self, "Error", msg)
            return

    # sock connect
    def SockConnect(self):
        try:
            self.sock.write(self.getmnt)
        except Exception as e:
            print(f"{e}")


    def SockDisconnect(self):
        self.sock.flush()
        self.sock.close()

    def SockRecv(self):
        rtcm = self.sock.readAll()
        if self.com.isOpen():
            try:
                self.com.write(rtcm)
                self.stxbs += len(rtcm)
                self.progressBar.setValue(self.stxbs % 100)
            except IndexError as e:
                pass
        else:
            print(f"Open serial first please")


    def SockTransit(self):
        pass

    # send gga to ntrip server
    def SendGGA(self):
        if self.ntrip is not None and self.CorsThread is not None:
            if self.checkBox_sendgga.isChecked():
                if self.curgga.decode("utf-8").startswith("$GNGGA"):
                    print(f"Transit {self.curgga} to ntrip")
                    self.ntrip.sendGGA2Ntrip(self.curgga)

    # clear serial received data
    def SRecvClearBtClick(self):
        """

        :return:
        """
        self.textEdit_recv.clear()

    # text cursor at end
    def TextRecvChanged(self):
        """

        :return:
        """
        self.textEdit_recv.moveCursor(QTextCursor.End)

    # close window
    def CloseAll(self):
        if self.com.isOpen():
            self.com.flush()
            self.com.close()

        if self.ntrip is not None:
            self._TerminateNtrip()

        if self.fh is not None:
            self.fh.flush()
            self.fh.close()
        exit(0)

    # stop all stream
    def StopAll(self):
        if self.com.isOpen():
            self.com.close()
            self.SetSerialPara(True)
            self.pushButton_open.setText(OPEN)

        if self.ntrip is not None:
            self._TerminateNtrip()

    # terminate ntrip connection
    def _TerminateNtrip(self):
        """"""
        # self.ntrip.terminate()
        # self.ntrip.data.clear()
        self.sock.disconnect()
        self.com.flush()
        # self.ntrip, self.CorsThread = None, None
        self.SetNtripPara(True)
        self.pushButton_conn.setText(CONNECT)
        print(f"Ntrip client terminating...")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())
