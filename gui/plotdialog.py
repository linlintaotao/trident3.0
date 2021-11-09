# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plotdialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(596, 444)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.style = QtWidgets.QComboBox(Dialog)
        self.style.setEditable(False)
        self.style.setFrame(True)
        self.style.setObjectName("style")
        self.gridLayout.addWidget(self.style, 0, 0, 1, 1)
        self.state = QtWidgets.QComboBox(Dialog)
        self.state.setEditable(False)
        self.state.setObjectName("state")
        self.gridLayout.addWidget(self.state, 0, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.refresh = QtWidgets.QPushButton(Dialog)
        self.refresh.setObjectName("refresh")
        self.gridLayout.addWidget(self.refresh, 0, 3, 1, 1)
        self.widget = QtWidgets.QWidget(Dialog)
        self.widget.setObjectName("widget")
        self.gridLayout.addWidget(self.widget, 1, 0, 1, 4)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.refresh.setText(_translate("Dialog", "refresh"))
