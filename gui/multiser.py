# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'multiser.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtWidgets


class MUi_widget(object):
    def setupUi(self, widget):
        widget.setObjectName("widget")
        widget.resize(575, 270)
        self.pushButton_close_all_5 = QtWidgets.QPushButton(widget)
        self.pushButton_close_all_5.setGeometry(QtCore.QRect(490, 240, 75, 23))
        self.pushButton_close_all_5.setObjectName("pushButton_close_all_5")
        self.widget = QtWidgets.QWidget(widget)
        self.widget.resize(551, 222)
        self.widget.setObjectName("widget")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.widget)
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.Serial_4 = QtWidgets.QGroupBox(self.widget)
        self.Serial_4.setObjectName("Serial_4")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.Serial_4)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.lsbaud_4 = QtWidgets.QLabel(self.Serial_4)
        self.lsbaud_4.setObjectName("lsbaud_4")
        self.gridLayout_4.addWidget(self.lsbaud_4, 0, 2, 1, 1)
        self.cbsdata_4 = QtWidgets.QComboBox(self.Serial_4)
        self.cbsdata_4.setEditable(True)
        self.cbsdata_4.setObjectName("cbsdata_4")
        self.cbsdata_4.addItem("")
        self.cbsdata_4.addItem("")
        self.cbsdata_4.addItem("")
        self.gridLayout_4.addWidget(self.cbsdata_4, 1, 1, 1, 1)
        self.pushButton_open_4 = QtWidgets.QPushButton(self.Serial_4)
        self.pushButton_open_4.setObjectName("pushButton_open_4")
        self.gridLayout_4.addWidget(self.pushButton_open_4, 4, 4, 1, 1)
        self.lsstop_4 = QtWidgets.QLabel(self.Serial_4)
        self.lsstop_4.setObjectName("lsstop_4")
        self.gridLayout_4.addWidget(self.lsstop_4, 4, 0, 1, 1)
        self.lsdata_4 = QtWidgets.QLabel(self.Serial_4)
        self.lsdata_4.setObjectName("lsdata_4")
        self.gridLayout_4.addWidget(self.lsdata_4, 1, 0, 1, 1)
        self.cbsport_4 = QtWidgets.QComboBox(self.Serial_4)
        self.cbsport_4.setEditable(True)
        self.cbsport_4.setObjectName("cbsport_4")
        self.cbsport_4.addItem("")
        self.gridLayout_4.addWidget(self.cbsport_4, 0, 1, 1, 1)
        self.cbsparity_4 = QtWidgets.QComboBox(self.Serial_4)
        self.cbsparity_4.setEditable(True)
        self.cbsparity_4.setObjectName("cbsparity_4")
        self.cbsparity_4.addItem("")
        self.cbsparity_4.addItem("")
        self.cbsparity_4.addItem("")
        self.gridLayout_4.addWidget(self.cbsparity_4, 1, 4, 1, 1)
        self.cbsstop_4 = QtWidgets.QComboBox(self.Serial_4)
        self.cbsstop_4.setEditable(True)
        self.cbsstop_4.setObjectName("cbsstop_4")
        self.cbsstop_4.addItem("")
        self.cbsstop_4.addItem("")
        self.gridLayout_4.addWidget(self.cbsstop_4, 4, 1, 1, 1)
        self.lsport_4 = QtWidgets.QLabel(self.Serial_4)
        self.lsport_4.setObjectName("lsport_4")
        self.gridLayout_4.addWidget(self.lsport_4, 0, 0, 1, 1)
        self.lsparity_4 = QtWidgets.QLabel(self.Serial_4)
        self.lsparity_4.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.lsparity_4.setObjectName("lsparity_4")
        self.gridLayout_4.addWidget(self.lsparity_4, 1, 2, 1, 1)
        self.cbsbaud_4 = QtWidgets.QComboBox(self.Serial_4)
        self.cbsbaud_4.setEditable(True)
        self.cbsbaud_4.setInsertPolicy(QtWidgets.QComboBox.InsertBeforeCurrent)
        self.cbsbaud_4.setObjectName("cbsbaud_4")
        self.cbsbaud_4.addItem("")
        self.cbsbaud_4.addItem("")
        self.cbsbaud_4.addItem("")
        self.cbsbaud_4.addItem("")
        self.cbsbaud_4.addItem("")
        self.cbsbaud_4.addItem("")
        self.cbsbaud_4.addItem("")
        self.cbsbaud_4.addItem("")
        self.gridLayout_4.addWidget(self.cbsbaud_4, 0, 4, 1, 1)
        self.gridLayout_5.addWidget(self.Serial_4, 1, 1, 1, 1)
        self.Serial_3 = QtWidgets.QGroupBox(self.widget)
        self.Serial_3.setObjectName("Serial_3")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.Serial_3)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.lsbaud_3 = QtWidgets.QLabel(self.Serial_3)
        self.lsbaud_3.setObjectName("lsbaud_3")
        self.gridLayout_3.addWidget(self.lsbaud_3, 0, 2, 1, 1)
        self.cbsdata_3 = QtWidgets.QComboBox(self.Serial_3)
        self.cbsdata_3.setEditable(True)
        self.cbsdata_3.setObjectName("cbsdata_3")
        self.cbsdata_3.addItem("")
        self.cbsdata_3.addItem("")
        self.cbsdata_3.addItem("")
        self.gridLayout_3.addWidget(self.cbsdata_3, 1, 1, 1, 1)
        self.pushButton_open_3 = QtWidgets.QPushButton(self.Serial_3)
        self.pushButton_open_3.setObjectName("pushButton_open_3")
        self.gridLayout_3.addWidget(self.pushButton_open_3, 4, 4, 1, 1)
        self.lsstop_3 = QtWidgets.QLabel(self.Serial_3)
        self.lsstop_3.setObjectName("lsstop_3")
        self.gridLayout_3.addWidget(self.lsstop_3, 4, 0, 1, 1)
        self.lsdata_3 = QtWidgets.QLabel(self.Serial_3)
        self.lsdata_3.setObjectName("lsdata_3")
        self.gridLayout_3.addWidget(self.lsdata_3, 1, 0, 1, 1)
        self.cbsport_3 = QtWidgets.QComboBox(self.Serial_3)
        self.cbsport_3.setEditable(True)
        self.cbsport_3.setObjectName("cbsport_3")
        self.cbsport_3.addItem("")
        self.gridLayout_3.addWidget(self.cbsport_3, 0, 1, 1, 1)
        self.cbsparity_3 = QtWidgets.QComboBox(self.Serial_3)
        self.cbsparity_3.setEditable(True)
        self.cbsparity_3.setObjectName("cbsparity_3")
        self.cbsparity_3.addItem("")
        self.cbsparity_3.addItem("")
        self.cbsparity_3.addItem("")
        self.gridLayout_3.addWidget(self.cbsparity_3, 1, 4, 1, 1)
        self.cbsstop_3 = QtWidgets.QComboBox(self.Serial_3)
        self.cbsstop_3.setEditable(True)
        self.cbsstop_3.setObjectName("cbsstop_3")
        self.cbsstop_3.addItem("")
        self.cbsstop_3.addItem("")
        self.gridLayout_3.addWidget(self.cbsstop_3, 4, 1, 1, 1)
        self.lsport_3 = QtWidgets.QLabel(self.Serial_3)
        self.lsport_3.setObjectName("lsport_3")
        self.gridLayout_3.addWidget(self.lsport_3, 0, 0, 1, 1)
        self.lsparity_3 = QtWidgets.QLabel(self.Serial_3)
        self.lsparity_3.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.lsparity_3.setObjectName("lsparity_3")
        self.gridLayout_3.addWidget(self.lsparity_3, 1, 2, 1, 1)
        self.cbsbaud_3 = QtWidgets.QComboBox(self.Serial_3)
        self.cbsbaud_3.setEditable(True)
        self.cbsbaud_3.setInsertPolicy(QtWidgets.QComboBox.InsertBeforeCurrent)
        self.cbsbaud_3.setObjectName("cbsbaud_3")
        self.cbsbaud_3.addItem("")
        self.cbsbaud_3.addItem("")
        self.cbsbaud_3.addItem("")
        self.cbsbaud_3.addItem("")
        self.cbsbaud_3.addItem("")
        self.cbsbaud_3.addItem("")
        self.cbsbaud_3.addItem("")
        self.cbsbaud_3.addItem("")
        self.gridLayout_3.addWidget(self.cbsbaud_3, 0, 4, 1, 1)
        self.gridLayout_5.addWidget(self.Serial_3, 1, 0, 1, 1)
        self.Serial = QtWidgets.QGroupBox(self.widget)
        self.Serial.setObjectName("Serial")
        self.gridLayout = QtWidgets.QGridLayout(self.Serial)
        self.gridLayout.setObjectName("gridLayout")
        self.lsbaud = QtWidgets.QLabel(self.Serial)
        self.lsbaud.setObjectName("lsbaud")
        self.gridLayout.addWidget(self.lsbaud, 0, 2, 1, 1)
        self.cbsdata = QtWidgets.QComboBox(self.Serial)
        self.cbsdata.setEditable(True)
        self.cbsdata.setObjectName("cbsdata")
        self.cbsdata.addItem("")
        self.cbsdata.addItem("")
        self.cbsdata.addItem("")
        self.gridLayout.addWidget(self.cbsdata, 1, 1, 1, 1)
        self.pushButton_open = QtWidgets.QPushButton(self.Serial)
        self.pushButton_open.setObjectName("pushButton_open")
        self.gridLayout.addWidget(self.pushButton_open, 4, 4, 1, 1)
        self.lsstop = QtWidgets.QLabel(self.Serial)
        self.lsstop.setObjectName("lsstop")
        self.gridLayout.addWidget(self.lsstop, 4, 0, 1, 1)
        self.lsdata = QtWidgets.QLabel(self.Serial)
        self.lsdata.setObjectName("lsdata")
        self.gridLayout.addWidget(self.lsdata, 1, 0, 1, 1)
        self.cbsport = QtWidgets.QComboBox(self.Serial)
        self.cbsport.setEditable(True)
        self.cbsport.setObjectName("cbsport")
        self.cbsport.addItem("")
        self.gridLayout.addWidget(self.cbsport, 0, 1, 1, 1)
        self.cbsparity = QtWidgets.QComboBox(self.Serial)
        self.cbsparity.setEditable(True)
        self.cbsparity.setObjectName("cbsparity")
        self.cbsparity.addItem("")
        self.cbsparity.addItem("")
        self.cbsparity.addItem("")
        self.gridLayout.addWidget(self.cbsparity, 1, 4, 1, 1)
        self.cbsstop = QtWidgets.QComboBox(self.Serial)
        self.cbsstop.setEditable(True)
        self.cbsstop.setObjectName("cbsstop")
        self.cbsstop.addItem("")
        self.cbsstop.addItem("")
        self.gridLayout.addWidget(self.cbsstop, 4, 1, 1, 1)
        self.lsport = QtWidgets.QLabel(self.Serial)
        self.lsport.setObjectName("lsport")
        self.gridLayout.addWidget(self.lsport, 0, 0, 1, 1)
        self.lsparity = QtWidgets.QLabel(self.Serial)
        self.lsparity.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.lsparity.setObjectName("lsparity")
        self.gridLayout.addWidget(self.lsparity, 1, 2, 1, 1)
        self.cbsbaud = QtWidgets.QComboBox(self.Serial)
        self.cbsbaud.setEditable(True)
        self.cbsbaud.setInsertPolicy(QtWidgets.QComboBox.InsertBeforeCurrent)
        self.cbsbaud.setObjectName("cbsbaud")
        self.cbsbaud.addItem("")
        self.cbsbaud.addItem("")
        self.cbsbaud.addItem("")
        self.cbsbaud.addItem("")
        self.cbsbaud.addItem("")
        self.cbsbaud.addItem("")
        self.cbsbaud.addItem("")
        self.cbsbaud.addItem("")
        self.gridLayout.addWidget(self.cbsbaud, 0, 4, 1, 1)
        self.gridLayout_5.addWidget(self.Serial, 0, 0, 1, 1)
        self.Serial_2 = QtWidgets.QGroupBox(self.widget)
        self.Serial_2.setObjectName("Serial_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.Serial_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.lsbaud_2 = QtWidgets.QLabel(self.Serial_2)
        self.lsbaud_2.setObjectName("lsbaud_2")
        self.gridLayout_2.addWidget(self.lsbaud_2, 0, 2, 1, 1)
        self.cbsdata_2 = QtWidgets.QComboBox(self.Serial_2)
        self.cbsdata_2.setEditable(True)
        self.cbsdata_2.setObjectName("cbsdata_2")
        self.cbsdata_2.addItem("")
        self.cbsdata_2.addItem("")
        self.cbsdata_2.addItem("")
        self.gridLayout_2.addWidget(self.cbsdata_2, 1, 1, 1, 1)
        self.pushButton_open_2 = QtWidgets.QPushButton(self.Serial_2)
        self.pushButton_open_2.setObjectName("pushButton_open_2")
        self.gridLayout_2.addWidget(self.pushButton_open_2, 4, 4, 1, 1)
        self.lsstop_2 = QtWidgets.QLabel(self.Serial_2)
        self.lsstop_2.setObjectName("lsstop_2")
        self.gridLayout_2.addWidget(self.lsstop_2, 4, 0, 1, 1)
        self.lsdata_2 = QtWidgets.QLabel(self.Serial_2)
        self.lsdata_2.setObjectName("lsdata_2")
        self.gridLayout_2.addWidget(self.lsdata_2, 1, 0, 1, 1)
        self.cbsport_2 = QtWidgets.QComboBox(self.Serial_2)
        self.cbsport_2.setEditable(True)
        self.cbsport_2.setObjectName("cbsport_2")
        self.cbsport_2.addItem("")
        self.gridLayout_2.addWidget(self.cbsport_2, 0, 1, 1, 1)
        self.cbsparity_2 = QtWidgets.QComboBox(self.Serial_2)
        self.cbsparity_2.setEditable(True)
        self.cbsparity_2.setObjectName("cbsparity_2")
        self.cbsparity_2.addItem("")
        self.cbsparity_2.addItem("")
        self.cbsparity_2.addItem("")
        self.gridLayout_2.addWidget(self.cbsparity_2, 1, 4, 1, 1)
        self.cbsstop_2 = QtWidgets.QComboBox(self.Serial_2)
        self.cbsstop_2.setEditable(True)
        self.cbsstop_2.setObjectName("cbsstop_2")
        self.cbsstop_2.addItem("")
        self.cbsstop_2.addItem("")
        self.gridLayout_2.addWidget(self.cbsstop_2, 4, 1, 1, 1)
        self.lsport_2 = QtWidgets.QLabel(self.Serial_2)
        self.lsport_2.setObjectName("lsport_2")
        self.gridLayout_2.addWidget(self.lsport_2, 0, 0, 1, 1)
        self.lsparity_2 = QtWidgets.QLabel(self.Serial_2)
        self.lsparity_2.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.lsparity_2.setObjectName("lsparity_2")
        self.gridLayout_2.addWidget(self.lsparity_2, 1, 2, 1, 1)
        self.cbsbaud_2 = QtWidgets.QComboBox(self.Serial_2)
        self.cbsbaud_2.setEditable(True)
        self.cbsbaud_2.setInsertPolicy(QtWidgets.QComboBox.InsertBeforeCurrent)
        self.cbsbaud_2.setObjectName("cbsbaud_2")
        self.cbsbaud_2.addItem("")
        self.cbsbaud_2.addItem("")
        self.cbsbaud_2.addItem("")
        self.cbsbaud_2.addItem("")
        self.cbsbaud_2.addItem("")
        self.cbsbaud_2.addItem("")
        self.cbsbaud_2.addItem("")
        self.cbsbaud_2.addItem("")
        self.gridLayout_2.addWidget(self.cbsbaud_2, 0, 4, 1, 1)
        self.gridLayout_5.addWidget(self.Serial_2, 0, 1, 1, 1)

        self.retranslateUi(widget)
        self.cbsdata_4.setCurrentIndex(1)
        self.cbsstop_4.setCurrentIndex(1)
        self.cbsbaud_4.setCurrentIndex(4)
        self.cbsdata_3.setCurrentIndex(1)
        self.cbsstop_3.setCurrentIndex(1)
        self.cbsbaud_3.setCurrentIndex(4)
        self.cbsdata.setCurrentIndex(1)
        self.cbsstop.setCurrentIndex(1)
        self.cbsbaud.setCurrentIndex(4)
        self.cbsdata_2.setCurrentIndex(1)
        self.cbsstop_2.setCurrentIndex(1)
        self.cbsbaud_2.setCurrentIndex(4)
        QtCore.QMetaObject.connectSlotsByName(widget)

    def retranslateUi(self, widget):
        _translate = QtCore.QCoreApplication.translate
        widget.setWindowTitle(_translate("widget", "Trident v1.4 (for any support contact fmi@feyman.cn)"))
        self.pushButton_close_all_5.setText(_translate("widget", "Close All"))
        self.Serial_4.setTitle(_translate("widget", "Serial"))
        self.lsbaud_4.setText(_translate("widget", "Baud"))
        self.cbsdata_4.setItemText(0, _translate("widget", "7"))
        self.cbsdata_4.setItemText(1, _translate("widget", "8"))
        self.cbsdata_4.setItemText(2, _translate("widget", "9"))
        self.pushButton_open_4.setText(_translate("widget", "Open"))
        self.lsstop_4.setText(_translate("widget", "Stopbit"))
        self.lsdata_4.setText(_translate("widget", "Databit"))
        self.cbsport_4.setCurrentText(_translate("widget", "COM1"))
        self.cbsport_4.setItemText(0, _translate("widget", "COM1"))
        self.cbsparity_4.setItemText(0, _translate("widget", "N"))
        self.cbsparity_4.setItemText(1, _translate("widget", "E"))
        self.cbsparity_4.setItemText(2, _translate("widget", "O"))
        self.cbsstop_4.setItemText(0, _translate("widget", "0"))
        self.cbsstop_4.setItemText(1, _translate("widget", "1"))
        self.lsport_4.setText(_translate("widget", "Port"))
        self.lsparity_4.setText(_translate("widget", "Parity"))
        self.cbsbaud_4.setCurrentText(_translate("widget", "115200"))
        self.cbsbaud_4.setItemText(0, _translate("widget", "4800"))
        self.cbsbaud_4.setItemText(1, _translate("widget", "9600"))
        self.cbsbaud_4.setItemText(2, _translate("widget", "19200"))
        self.cbsbaud_4.setItemText(3, _translate("widget", "57600"))
        self.cbsbaud_4.setItemText(4, _translate("widget", "115200"))
        self.cbsbaud_4.setItemText(5, _translate("widget", "230400"))
        self.cbsbaud_4.setItemText(6, _translate("widget", "460800"))
        self.cbsbaud_4.setItemText(7, _translate("widget", "921600"))
        self.Serial_3.setTitle(_translate("widget", "Serial"))
        self.lsbaud_3.setText(_translate("widget", "Baud"))
        self.cbsdata_3.setItemText(0, _translate("widget", "7"))
        self.cbsdata_3.setItemText(1, _translate("widget", "8"))
        self.cbsdata_3.setItemText(2, _translate("widget", "9"))
        self.pushButton_open_3.setText(_translate("widget", "Open"))
        self.lsstop_3.setText(_translate("widget", "Stopbit"))
        self.lsdata_3.setText(_translate("widget", "Databit"))
        self.cbsport_3.setCurrentText(_translate("widget", "COM1"))
        self.cbsport_3.setItemText(0, _translate("widget", "COM1"))
        self.cbsparity_3.setItemText(0, _translate("widget", "N"))
        self.cbsparity_3.setItemText(1, _translate("widget", "E"))
        self.cbsparity_3.setItemText(2, _translate("widget", "O"))
        self.cbsstop_3.setItemText(0, _translate("widget", "0"))
        self.cbsstop_3.setItemText(1, _translate("widget", "1"))
        self.lsport_3.setText(_translate("widget", "Port"))
        self.lsparity_3.setText(_translate("widget", "Parity"))
        self.cbsbaud_3.setCurrentText(_translate("widget", "115200"))
        self.cbsbaud_3.setItemText(0, _translate("widget", "4800"))
        self.cbsbaud_3.setItemText(1, _translate("widget", "9600"))
        self.cbsbaud_3.setItemText(2, _translate("widget", "19200"))
        self.cbsbaud_3.setItemText(3, _translate("widget", "57600"))
        self.cbsbaud_3.setItemText(4, _translate("widget", "115200"))
        self.cbsbaud_3.setItemText(5, _translate("widget", "230400"))
        self.cbsbaud_3.setItemText(6, _translate("widget", "460800"))
        self.cbsbaud_3.setItemText(7, _translate("widget", "921600"))
        self.Serial.setTitle(_translate("widget", "Serial"))
        self.lsbaud.setText(_translate("widget", "Baud"))
        self.cbsdata.setItemText(0, _translate("widget", "7"))
        self.cbsdata.setItemText(1, _translate("widget", "8"))
        self.cbsdata.setItemText(2, _translate("widget", "9"))
        self.pushButton_open.setText(_translate("widget", "Open"))
        self.lsstop.setText(_translate("widget", "Stopbit"))
        self.lsdata.setText(_translate("widget", "Databit"))
        self.cbsport.setCurrentText(_translate("widget", "COM1"))
        self.cbsport.setItemText(0, _translate("widget", "COM1"))
        self.cbsparity.setItemText(0, _translate("widget", "N"))
        self.cbsparity.setItemText(1, _translate("widget", "E"))
        self.cbsparity.setItemText(2, _translate("widget", "O"))
        self.cbsstop.setItemText(0, _translate("widget", "0"))
        self.cbsstop.setItemText(1, _translate("widget", "1"))
        self.lsport.setText(_translate("widget", "Port"))
        self.lsparity.setText(_translate("widget", "Parity"))
        self.cbsbaud.setCurrentText(_translate("widget", "115200"))
        self.cbsbaud.setItemText(0, _translate("widget", "4800"))
        self.cbsbaud.setItemText(1, _translate("widget", "9600"))
        self.cbsbaud.setItemText(2, _translate("widget", "19200"))
        self.cbsbaud.setItemText(3, _translate("widget", "57600"))
        self.cbsbaud.setItemText(4, _translate("widget", "115200"))
        self.cbsbaud.setItemText(5, _translate("widget", "230400"))
        self.cbsbaud.setItemText(6, _translate("widget", "460800"))
        self.cbsbaud.setItemText(7, _translate("widget", "921600"))
        self.Serial_2.setTitle(_translate("widget", "Serial"))
        self.lsbaud_2.setText(_translate("widget", "Baud"))
        self.cbsdata_2.setItemText(0, _translate("widget", "7"))
        self.cbsdata_2.setItemText(1, _translate("widget", "8"))
        self.cbsdata_2.setItemText(2, _translate("widget", "9"))
        self.pushButton_open_2.setText(_translate("widget", "Open"))
        self.lsstop_2.setText(_translate("widget", "Stopbit"))
        self.lsdata_2.setText(_translate("widget", "Databit"))
        self.cbsport_2.setCurrentText(_translate("widget", "COM1"))
        self.cbsport_2.setItemText(0, _translate("widget", "COM1"))
        self.cbsparity_2.setItemText(0, _translate("widget", "N"))
        self.cbsparity_2.setItemText(1, _translate("widget", "E"))
        self.cbsparity_2.setItemText(2, _translate("widget", "O"))
        self.cbsstop_2.setItemText(0, _translate("widget", "0"))
        self.cbsstop_2.setItemText(1, _translate("widget", "1"))
        self.lsport_2.setText(_translate("widget", "Port"))
        self.lsparity_2.setText(_translate("widget", "Parity"))
        self.cbsbaud_2.setCurrentText(_translate("widget", "115200"))
        self.cbsbaud_2.setItemText(0, _translate("widget", "4800"))
        self.cbsbaud_2.setItemText(1, _translate("widget", "9600"))
        self.cbsbaud_2.setItemText(2, _translate("widget", "19200"))
        self.cbsbaud_2.setItemText(3, _translate("widget", "57600"))
        self.cbsbaud_2.setItemText(4, _translate("widget", "115200"))
        self.cbsbaud_2.setItemText(5, _translate("widget", "230400"))
        self.cbsbaud_2.setItemText(6, _translate("widget", "460800"))
        self.cbsbaud_2.setItemText(7, _translate("widget", "921600"))