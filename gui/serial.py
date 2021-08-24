# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'serial.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SerialDialog(object):
    def setupUi(self, SerialDialog):
        SerialDialog.setObjectName("SerialDialog")
        SerialDialog.resize(229, 138)
        self.gridLayout = QtWidgets.QGridLayout(SerialDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(SerialDialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.serialport = QtWidgets.QComboBox(SerialDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.serialport.sizePolicy().hasHeightForWidth())
        self.serialport.setSizePolicy(sizePolicy)
        self.serialport.setMaximumSize(QtCore.QSize(120, 16777215))
        self.serialport.setEditable(True)
        self.serialport.setObjectName("serialport")
        self.serialport.addItem("")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.serialport)
        self.label_2 = QtWidgets.QLabel(SerialDialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.baudrate = QtWidgets.QComboBox(SerialDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.baudrate.sizePolicy().hasHeightForWidth())
        self.baudrate.setSizePolicy(sizePolicy)
        self.baudrate.setMaximumSize(QtCore.QSize(120, 16777215))
        self.baudrate.setEditable(True)
        self.baudrate.setObjectName("baudrate")
        self.baudrate.addItem("")
        self.baudrate.addItem("")
        self.baudrate.addItem("")
        self.baudrate.addItem("")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.baudrate)
        self.gridLayout.addLayout(self.formLayout, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(SerialDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(SerialDialog)
        QtCore.QMetaObject.connectSlotsByName(SerialDialog)

    def retranslateUi(self, SerialDialog):
        _translate = QtCore.QCoreApplication.translate
        SerialDialog.setWindowTitle(_translate("SerialDialog", "Dialog"))
        self.label.setText(_translate("SerialDialog", "SerialPort"))
        self.serialport.setCurrentText(_translate("SerialDialog", "COM"))
        self.serialport.setItemText(0, _translate("SerialDialog", "COM"))
        self.label_2.setText(_translate("SerialDialog", "Baudrate"))
        self.baudrate.setCurrentText(_translate("SerialDialog", "115200"))
        self.baudrate.setItemText(0, _translate("SerialDialog", "115200"))
        self.baudrate.setItemText(1, _translate("SerialDialog", "9600"))
        self.baudrate.setItemText(2, _translate("SerialDialog", "460800"))
        self.baudrate.setItemText(3, _translate("SerialDialog", "921600"))
