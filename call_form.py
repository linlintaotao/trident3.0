# -*- coding: utf-8 -*-
""" 
 Created on 11/13/2019 3:05 PM
 
 @author : chey
 
"""
import sys
from queue import Queue
from threading import Thread
from PyQt5.QtWidgets import *
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import QTimer
from gui.form import Ui_Form
from streams import NtripClient


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
        self.timer.timeout.connect(self.ShowInfo)
        self.timer.start(1000)

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

    # serial configuration parameters
    def SOpenBtClick(self):
        """

        :return:
        """
        self.com.setPortName(self.cbsport.currentText())
        self.com.setBaudRate(int(self.cbsbaud.currentText()))
        self.com.setDataBits(int(self.cbsdata.currentText()))
        self.com.setStopBits(int(self.cbsstop.currentText()))
        # self.com.setParity(self.cbsparity.currentText())
        try:
            if self.com.open(QSerialPort.ReadWrite) == False:
                QMessageBox.critical(self, 'Fatal', 'Open serial failed!')
                return
        except Exception as e:
            QMessageBox.critical(self, 'Fatal', f"{sys._getframe().f_code.co_name}, {e}")

        self.pushButton_open.setEnabled(False)

        self.cbsport.setEnabled(False)
        self.cbsbaud.setEnabled(False)
        self.cbsdata.setEnabled(False)
        self.cbsstop.setEnabled(False)
        self.cbsparity.setEnabled(False)

    # serial received data display
    def SerialRecvData(self):
        """

        :return:
        """
        try:
            data = bytes(self.com.readAll())
            self.textEdit_recv.insertPlainText(data.decode('utf-8'))
        except Exception as e:
            QMessageBox.critical(self, 'Fatal', f"{sys._getframe().f_code.co_name}, {e}")

    # get ntrip caster params, invoke NtripClient thread
    def NConnBtClick(self):
        """

        :return:
        """
        if self.lineEdit_caster.text() == '' or self.lineEdit_port.text() == '':
            caster, port, mount = 'ntrips.feymani.cn', 2102, 'Obs'
            user, passwd = 'feyman-user', '123456'
        else:
            caster = self.lineEdit_caster.text()
            port = int(self.lineEdit_port.text())
            mount = self.lineEdit_mount.text()
            user = self.lineEdit_user.text()
            passwd = self.lineEdit_pwd.text()
        if self.ntrip is None:
            self.ntrip = NtripClient.NtripClient(caster=caster, port=port, mountpoint=mount, user=user, passwd=passwd)
            self.CorsThread = Thread(target=self.ntrip.readData)
            self.CorsThread.start()

            if not self.pushButton_atcmd.isChecked():
                print(f"AT command not checked")
                try:
                    self.com.write(self.ntrip.data.get())
                except Exception as e:
                    QMessageBox.critical(self, 'Fatal', f"{sys._getframe().f_code.co_name}, {e}")
        self.pushButton_conn.setEnabled(False)

    # send AT command
    def AtCmdBtClick(self):
        """
        while AT command button clicked ntrip data must not imported into serial
        :return:
        """
        if self.pushButton_conn.isChecked():
            print(f"Ntrip already checked, kill ntrip...")
            self.ntrip.readData.terminate()
            self.CorsThread.join()
        cmd = self.cbatcmd.currentText()
        if not cmd.startswith('AT+'):
            QMessageBox.warning(self, "Warning", "AT command start with AT+ ")
            return
        self.com.write(cmd.encode('utf-8'))
        print(f"AT cmd {cmd}")

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

    # display some statistics
    def ShowInfo(self):
        """

        :return:
        """
        if self.ntrip is not None:
            print(f"Ntrip recv data size {self.ntrip.nbytes} bytes")
        else:
            print(f"Nothing to do here")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())
