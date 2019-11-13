# -*- coding: utf-8 -*-
""" 
 Created on 11/13/2019 3:05 PM
 
 @author : chey
 
"""

import sys
from threading import Thread
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import QTimer
from gui.form import Ui_Form
from streams import NtripClient

OPEN = 'Open'
CLOSE = 'Close'
CONNECT = 'Connect'
DISCONNECT = 'Disconnect'


# TODO: serial and ntrip status info display
class MyMainWindow(QMainWindow, Ui_Form):
    def __init__(self, parent=None):
        """

        :param parent:
        """
        super(MyMainWindow, self).__init__(parent)
        self.ntrip = None
        self.CorsThread = None

        self.setupUi(self)
        self.CreateItems()
        self.CreateSignalSlot()

    def CreateItems(self):
        """

        :return:
        """
        self.com = QSerialPort()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.ImportCors)
        self.timer.start(100)

    def CreateSignalSlot(self):
        """

        :return:
        """
        self.pushButton_open.clicked.connect(self.SOpenBtClick)
        self.pushButton_conn.clicked.connect(self.NConnBtClick)
        self.pushButton_atcmd.clicked.connect(self.AtCmdBtClick)
        self.pushButton_refresh.clicked.connect(self.SRefreshBtClick)
        self.pushButton_clear.clicked.connect(self.SRecvClearBtClick)

        self.com.readyRead.connect(self.SerialRecvData)
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
        self.lineEdit_caster.setEnabled(enable)
        self.lineEdit_port.setEnabled(enable)
        self.lineEdit_mount.setEnabled(enable)
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
        if self.com.isOpen():
            try:
                data = bytes(self.com.readAll())
            except Exception as e:
                QMessageBox.critical(self, 'Critical', f"{sys._getframe().f_code.co_name}, {e}")
                self.com.close()
            else:
                self.textEdit_recv.insertPlainText(data.decode("utf-8", "ignore"))
        else:
            return


    # get ntrip caster params, invoke NtripClient thread
    def NConnBtClick(self):
        """

        :return:
        """
        if self.pushButton_conn.text() == CONNECT:
            if self.lineEdit_caster.text() == '' or self.lineEdit_port.text() == '':
                caster, port, mount = 'ntrips.feymani.cn', 2102, 'Obs'
                user, passwd = 'feyman-user', '123456'
            else:
                caster = self.lineEdit_caster.text()
                port = int(self.lineEdit_port.text())
                mount = self.lineEdit_mount.text()
                user = self.lineEdit_user.text()
                passwd = self.lineEdit_pwd.text()
            # create & start ntrip client thread
            if self.ntrip is None:
                self.ntrip = NtripClient.NtripClient(caster=caster, port=port, mountpoint=mount, user=user,
                                                     passwd=passwd)
                self.CorsThread = Thread(target=self.ntrip.readData)
                self.CorsThread.start()
                self.SetNtripPara(False)
                self.pushButton_conn.setText(DISCONNECT)
        elif self.pushButton_conn.text() == DISCONNECT:
            # terminate ntrip client thread
            self._TerminateNtrip()

    # send AT command
    def AtCmdBtClick(self):
        """
        while AT command button clicked ntrip data must not imported into serial
        :return:
        """
        if self.ntrip is not None and self.CorsThread is not None:
            self._TerminateNtrip()

        cmd = self.cbatcmd.currentText() + "\r\n"
        if not cmd.startswith('AT+'):
            QMessageBox.warning(self, "Warning", "AT command start with AT+ ")
        self.com.write(cmd.encode("utf-8", "ignore"))
        print(f"AT cmd {cmd}")

    # import cors data into serial
    # TODO: send gga to ntrip server
    def ImportCors(self):
        """

        :return:
        """
        if self.ntrip is not None and self.CorsThread is not None:
            try:
                self.com.write(self.ntrip.data.get())
            except Exception as e:
                QMessageBox.critical(self, 'Critical', f"{sys._getframe().f_code.co_name}, {e}")
            print(f"Ntrip recv data size {self.ntrip.nbytes} bytes")

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

    def _TerminateNtrip(self):
        """"""
        self.ntrip.terminate()
        self.CorsThread.join()
        self.com.flush()
        self.ntrip, self.CorsThread = None, None
        self.SetNtripPara(True)
        self.pushButton_conn.setText(CONNECT)
        print(f"Ntrip client terminating...")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())
