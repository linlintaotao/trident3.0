# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'form.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_widget(object):
    def setupUi(self, widget):
        widget.setObjectName("widget")
        widget.resize(1002, 653)
        self.textEdit_recv = QtWidgets.QTextEdit(widget)
        self.textEdit_recv.setGeometry(QtCore.QRect(10, 10, 711, 391))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(10)
        self.textEdit_recv.setFont(font)
        self.textEdit_recv.setFrameShadow(QtWidgets.QFrame.Plain)
        self.textEdit_recv.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.textEdit_recv.setReadOnly(True)
        self.textEdit_recv.setObjectName("textEdit_recv")
        self.Serial = QtWidgets.QGroupBox(widget)
        self.Serial.setGeometry(QtCore.QRect(730, 10, 261, 221))
        self.Serial.setObjectName("Serial")
        self.gridLayout = QtWidgets.QGridLayout(self.Serial)
        self.gridLayout.setObjectName("gridLayout")
        self.cbsbaud = QtWidgets.QComboBox(self.Serial)
        self.cbsbaud.setEditable(True)
        self.cbsbaud.setObjectName("cbsbaud")
        self.cbsbaud.addItem("")
        self.cbsbaud.addItem("")
        self.cbsbaud.addItem("")
        self.cbsbaud.addItem("")
        self.cbsbaud.addItem("")
        self.gridLayout.addWidget(self.cbsbaud, 1, 1, 1, 2)
        self.lsdata = QtWidgets.QLabel(self.Serial)
        self.lsdata.setObjectName("lsdata")
        self.gridLayout.addWidget(self.lsdata, 2, 0, 1, 1)
        self.cbsstop = QtWidgets.QComboBox(self.Serial)
        self.cbsstop.setEditable(True)
        self.cbsstop.setObjectName("cbsstop")
        self.cbsstop.addItem("")
        self.cbsstop.addItem("")
        self.gridLayout.addWidget(self.cbsstop, 4, 1, 1, 2)
        self.lsparity = QtWidgets.QLabel(self.Serial)
        self.lsparity.setObjectName("lsparity")
        self.gridLayout.addWidget(self.lsparity, 3, 0, 1, 1)
        self.cbsparity = QtWidgets.QComboBox(self.Serial)
        self.cbsparity.setEditable(True)
        self.cbsparity.setObjectName("cbsparity")
        self.cbsparity.addItem("")
        self.cbsparity.addItem("")
        self.cbsparity.addItem("")
        self.gridLayout.addWidget(self.cbsparity, 3, 1, 1, 2)
        self.lsbaud = QtWidgets.QLabel(self.Serial)
        self.lsbaud.setObjectName("lsbaud")
        self.gridLayout.addWidget(self.lsbaud, 1, 0, 1, 1)
        self.lsstop = QtWidgets.QLabel(self.Serial)
        self.lsstop.setObjectName("lsstop")
        self.gridLayout.addWidget(self.lsstop, 4, 0, 1, 1)
        self.lsport = QtWidgets.QLabel(self.Serial)
        self.lsport.setObjectName("lsport")
        self.gridLayout.addWidget(self.lsport, 0, 0, 1, 1)
        self.cbsdata = QtWidgets.QComboBox(self.Serial)
        self.cbsdata.setEditable(True)
        self.cbsdata.setObjectName("cbsdata")
        self.cbsdata.addItem("")
        self.cbsdata.addItem("")
        self.cbsdata.addItem("")
        self.gridLayout.addWidget(self.cbsdata, 2, 1, 1, 2)
        self.cbsport = QtWidgets.QComboBox(self.Serial)
        self.cbsport.setEditable(True)
        self.cbsport.setObjectName("cbsport")
        self.cbsport.addItem("")
        self.gridLayout.addWidget(self.cbsport, 0, 1, 1, 2)
        self.pushButton_refresh = QtWidgets.QPushButton(self.Serial)
        self.pushButton_refresh.setObjectName("pushButton_refresh")
        self.gridLayout.addWidget(self.pushButton_refresh, 6, 2, 1, 1)
        self.pushButton_open = QtWidgets.QPushButton(self.Serial)
        self.pushButton_open.setObjectName("pushButton_open")
        self.gridLayout.addWidget(self.pushButton_open, 6, 1, 1, 1)
        self.Ntrip = QtWidgets.QGroupBox(widget)
        self.Ntrip.setGeometry(QtCore.QRect(730, 240, 261, 211))
        self.Ntrip.setObjectName("Ntrip")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.Ntrip)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.lnuser = QtWidgets.QLabel(self.Ntrip)
        self.lnuser.setObjectName("lnuser")
        self.gridLayout_2.addWidget(self.lnuser, 3, 0, 1, 1)
        self.lncaster = QtWidgets.QLabel(self.Ntrip)
        self.lncaster.setObjectName("lncaster")
        self.gridLayout_2.addWidget(self.lncaster, 0, 0, 1, 1)
        self.pushButton_conn = QtWidgets.QPushButton(self.Ntrip)
        self.pushButton_conn.setObjectName("pushButton_conn")
        self.gridLayout_2.addWidget(self.pushButton_conn, 5, 0, 1, 1)
        self.progressBar = QtWidgets.QProgressBar(self.Ntrip)
        self.progressBar.setMaximum(100)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(False)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout_2.addWidget(self.progressBar, 5, 1, 1, 1)
        self.lnpwd = QtWidgets.QLabel(self.Ntrip)
        self.lnpwd.setObjectName("lnpwd")
        self.gridLayout_2.addWidget(self.lnpwd, 4, 0, 1, 1)
        self.lineEdit_pwd = QtWidgets.QLineEdit(self.Ntrip)
        self.lineEdit_pwd.setInputMask("")
        self.lineEdit_pwd.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_pwd.setObjectName("lineEdit_pwd")
        self.gridLayout_2.addWidget(self.lineEdit_pwd, 4, 1, 1, 1)
        self.lnport = QtWidgets.QLabel(self.Ntrip)
        self.lnport.setObjectName("lnport")
        self.gridLayout_2.addWidget(self.lnport, 1, 0, 1, 1)
        self.comboBox_mount = QtWidgets.QComboBox(self.Ntrip)
        self.comboBox_mount.setEditable(True)
        self.comboBox_mount.setObjectName("comboBox_mount")
        self.comboBox_mount.addItem("")
        self.comboBox_mount.addItem("")
        self.comboBox_mount.addItem("")
        self.comboBox_mount.addItem("")
        self.gridLayout_2.addWidget(self.comboBox_mount, 2, 1, 1, 1)
        self.comboBox_caster = QtWidgets.QComboBox(self.Ntrip)
        self.comboBox_caster.setEditable(True)
        self.comboBox_caster.setMaxVisibleItems(15)
        self.comboBox_caster.setObjectName("comboBox_caster")
        self.comboBox_caster.addItem("")
        self.comboBox_caster.addItem("")
        self.comboBox_caster.addItem("")
        self.gridLayout_2.addWidget(self.comboBox_caster, 0, 1, 1, 1)
        self.lnmount = QtWidgets.QLabel(self.Ntrip)
        self.lnmount.setObjectName("lnmount")
        self.gridLayout_2.addWidget(self.lnmount, 2, 0, 1, 1)
        self.comboBox_port = QtWidgets.QComboBox(self.Ntrip)
        self.comboBox_port.setEditable(True)
        self.comboBox_port.setObjectName("comboBox_port")
        self.comboBox_port.addItem("")
        self.comboBox_port.addItem("")
        self.comboBox_port.addItem("")
        self.gridLayout_2.addWidget(self.comboBox_port, 1, 1, 1, 1)
        self.lineEdit_user = QtWidgets.QLineEdit(self.Ntrip)
        self.lineEdit_user.setObjectName("lineEdit_user")
        self.gridLayout_2.addWidget(self.lineEdit_user, 3, 1, 1, 1)
        self.ATCmd = QtWidgets.QGroupBox(widget)
        self.ATCmd.setGeometry(QtCore.QRect(730, 460, 261, 121))
        self.ATCmd.setObjectName("ATCmd")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.ATCmd)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.cbatcmd = QtWidgets.QComboBox(self.ATCmd)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(9)
        self.cbatcmd.setFont(font)
        self.cbatcmd.setEditable(True)
        self.cbatcmd.setObjectName("cbatcmd")
        self.cbatcmd.addItem("")
        self.cbatcmd.addItem("")
        self.cbatcmd.addItem("")
        self.cbatcmd.addItem("")
        self.cbatcmd.addItem("")
        self.cbatcmd.addItem("")
        self.cbatcmd.addItem("")
        self.cbatcmd.addItem("")
        self.cbatcmd.addItem("")
        self.cbatcmd.addItem("")
        self.cbatcmd.addItem("")
        self.cbatcmd.addItem("")
        self.cbatcmd.addItem("")
        self.cbatcmd.addItem("")
        self.cbatcmd.addItem("")
        self.cbatcmd.addItem("")
        self.cbatcmd.addItem("")
        self.cbatcmd.addItem("")
        self.cbatcmd.addItem("")
        self.gridLayout_3.addWidget(self.cbatcmd, 0, 1, 1, 1)
        self.file_transbar = QtWidgets.QProgressBar(self.ATCmd)
        self.file_transbar.setProperty("value", 0)
        self.file_transbar.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.file_transbar.setTextVisible(True)
        self.file_transbar.setOrientation(QtCore.Qt.Horizontal)
        self.file_transbar.setInvertedAppearance(False)
        self.file_transbar.setObjectName("file_transbar")
        self.gridLayout_3.addWidget(self.file_transbar, 3, 1, 1, 1)
        self.open_file = QtWidgets.QPushButton(self.ATCmd)
        self.open_file.setObjectName("open_file")
        self.gridLayout_3.addWidget(self.open_file, 1, 0, 1, 1)
        self.trans_file = QtWidgets.QPushButton(self.ATCmd)
        self.trans_file.setObjectName("trans_file")
        self.gridLayout_3.addWidget(self.trans_file, 3, 0, 1, 1)
        self.pushButton_atcmd = QtWidgets.QPushButton(self.ATCmd)
        self.pushButton_atcmd.setObjectName("pushButton_atcmd")
        self.gridLayout_3.addWidget(self.pushButton_atcmd, 0, 0, 1, 1)
        self.lineEdit_filename = QtWidgets.QLineEdit(self.ATCmd)
        self.lineEdit_filename.setObjectName("lineEdit_filename")
        self.gridLayout_3.addWidget(self.lineEdit_filename, 1, 1, 1, 1)
        self.checkBox_savenmea = QtWidgets.QCheckBox(widget)
        self.checkBox_savenmea.setGeometry(QtCore.QRect(299, 591, 77, 16))
        self.checkBox_savenmea.setMouseTracking(False)
        self.checkBox_savenmea.setChecked(True)
        self.checkBox_savenmea.setObjectName("checkBox_savenmea")
        self.checkBox_ggafmt = QtWidgets.QCheckBox(widget)
        self.checkBox_ggafmt.setGeometry(QtCore.QRect(228, 591, 65, 16))
        self.checkBox_ggafmt.setMouseTracking(False)
        self.checkBox_ggafmt.setChecked(True)
        self.checkBox_ggafmt.setObjectName("checkBox_ggafmt")
        self.Infos = QtWidgets.QGroupBox(widget)
        self.Infos.setGeometry(QtCore.QRect(10, 410, 541, 161))
        self.Infos.setObjectName("Infos")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.Infos)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.lineEdit_basehgt = QtWidgets.QLineEdit(self.Infos)
        self.lineEdit_basehgt.setReadOnly(True)
        self.lineEdit_basehgt.setObjectName("lineEdit_basehgt")
        self.gridLayout_4.addWidget(self.lineEdit_basehgt, 2, 4, 1, 2)
        self.lineEdit_dop = QtWidgets.QLineEdit(self.Infos)
        self.lineEdit_dop.setReadOnly(True)
        self.lineEdit_dop.setObjectName("lineEdit_dop")
        self.gridLayout_4.addWidget(self.lineEdit_dop, 3, 7, 1, 2)
        self.lineEdit_rovhgt = QtWidgets.QLineEdit(self.Infos)
        self.lineEdit_rovhgt.setReadOnly(True)
        self.lineEdit_rovhgt.setObjectName("lineEdit_rovhgt")
        self.gridLayout_4.addWidget(self.lineEdit_rovhgt, 2, 1, 1, 1)
        self.lineEdit_baselon = QtWidgets.QLineEdit(self.Infos)
        self.lineEdit_baselon.setReadOnly(True)
        self.lineEdit_baselon.setObjectName("lineEdit_baselon")
        self.gridLayout_4.addWidget(self.lineEdit_baselon, 1, 4, 1, 2)
        self.label_9 = QtWidgets.QLabel(self.Infos)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.gridLayout_4.addWidget(self.label_9, 2, 6, 1, 1)
        self.lineEdit_dir = QtWidgets.QLineEdit(self.Infos)
        self.lineEdit_dir.setReadOnly(True)
        self.lineEdit_dir.setObjectName("lineEdit_dir")
        self.gridLayout_4.addWidget(self.lineEdit_dir, 2, 7, 1, 2)
        self.lineEdit_nsat = QtWidgets.QLineEdit(self.Infos)
        self.lineEdit_nsat.setReadOnly(True)
        self.lineEdit_nsat.setObjectName("lineEdit_nsat")
        self.gridLayout_4.addWidget(self.lineEdit_nsat, 1, 7, 1, 2)
        self.label_11 = QtWidgets.QLabel(self.Infos)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.gridLayout_4.addWidget(self.label_11, 1, 2, 1, 2)
        self.lineEdit_solstat = QtWidgets.QLineEdit(self.Infos)
        self.lineEdit_solstat.setReadOnly(True)
        self.lineEdit_solstat.setObjectName("lineEdit_solstat")
        self.gridLayout_4.addWidget(self.lineEdit_solstat, 3, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.Infos)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.gridLayout_4.addWidget(self.label_8, 2, 2, 1, 1)
        self.lineEdit_baseid = QtWidgets.QLineEdit(self.Infos)
        self.lineEdit_baseid.setReadOnly(True)
        self.lineEdit_baseid.setObjectName("lineEdit_baseid")
        self.gridLayout_4.addWidget(self.lineEdit_baseid, 3, 4, 1, 2)
        self.label_10 = QtWidgets.QLabel(self.Infos)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.gridLayout_4.addWidget(self.label_10, 1, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.Infos)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.gridLayout_4.addWidget(self.label_7, 2, 0, 1, 1)
        self.label_18 = QtWidgets.QLabel(self.Infos)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_18.setFont(font)
        self.label_18.setObjectName("label_18")
        self.gridLayout_4.addWidget(self.label_18, 3, 6, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.Infos)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        self.gridLayout_4.addWidget(self.label_12, 1, 6, 1, 1)
        self.label_17 = QtWidgets.QLabel(self.Infos)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_17.setFont(font)
        self.label_17.setObjectName("label_17")
        self.gridLayout_4.addWidget(self.label_17, 3, 2, 1, 1)
        self.label_16 = QtWidgets.QLabel(self.Infos)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_16.setFont(font)
        self.label_16.setObjectName("label_16")
        self.gridLayout_4.addWidget(self.label_16, 3, 0, 1, 1)
        self.lineEdit_rovlon = QtWidgets.QLineEdit(self.Infos)
        self.lineEdit_rovlon.setReadOnly(True)
        self.lineEdit_rovlon.setObjectName("lineEdit_rovlon")
        self.gridLayout_4.addWidget(self.lineEdit_rovlon, 1, 1, 1, 1)
        self.lineEdit_rovlat = QtWidgets.QLineEdit(self.Infos)
        self.lineEdit_rovlat.setReadOnly(True)
        self.lineEdit_rovlat.setObjectName("lineEdit_rovlat")
        self.gridLayout_4.addWidget(self.lineEdit_rovlat, 0, 1, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.Infos)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_13.setFont(font)
        self.label_13.setObjectName("label_13")
        self.gridLayout_4.addWidget(self.label_13, 0, 0, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.Infos)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_14.setFont(font)
        self.label_14.setObjectName("label_14")
        self.gridLayout_4.addWidget(self.label_14, 0, 2, 1, 1)
        self.label_15 = QtWidgets.QLabel(self.Infos)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_15.setFont(font)
        self.label_15.setObjectName("label_15")
        self.gridLayout_4.addWidget(self.label_15, 0, 6, 1, 1)
        self.lineEdit_timenow = QtWidgets.QLineEdit(self.Infos)
        self.lineEdit_timenow.setReadOnly(True)
        self.lineEdit_timenow.setObjectName("lineEdit_timenow")
        self.gridLayout_4.addWidget(self.lineEdit_timenow, 0, 7, 1, 2)
        self.lineEdit_baselat = QtWidgets.QLineEdit(self.Infos)
        self.lineEdit_baselat.setReadOnly(True)
        self.lineEdit_baselat.setObjectName("lineEdit_baselat")
        self.gridLayout_4.addWidget(self.lineEdit_baselat, 0, 4, 1, 2)
        self.lineEdit = QtWidgets.QLineEdit(widget)
        self.lineEdit.setGeometry(QtCore.QRect(160, 620, 391, 20))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        self.lineEdit.setFont(font)
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setObjectName("lineEdit")
        self.layoutWidget = QtWidgets.QWidget(widget)
        self.layoutWidget.setGeometry(QtCore.QRect(730, 610, 261, 31))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.pushButton_close = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_close.setObjectName("pushButton_close")
        self.gridLayout_5.addWidget(self.pushButton_close, 0, 3, 1, 1)
        self.pushButton_stop = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_stop.setObjectName("pushButton_stop")
        self.gridLayout_5.addWidget(self.pushButton_stop, 0, 2, 1, 1)
        self.pushButton_clear = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_clear.setObjectName("pushButton_clear")
        self.gridLayout_5.addWidget(self.pushButton_clear, 0, 1, 1, 1)
        self.lineEdit_srx = QtWidgets.QLineEdit(widget)
        self.lineEdit_srx.setGeometry(QtCore.QRect(40, 590, 91, 20))
        self.lineEdit_srx.setAutoFillBackground(False)
        self.lineEdit_srx.setReadOnly(True)
        self.lineEdit_srx.setObjectName("lineEdit_srx")
        self.label_srx = QtWidgets.QLabel(widget)
        self.label_srx.setGeometry(QtCore.QRect(10, 590, 16, 16))
        self.label_srx.setObjectName("label_srx")
        self.lineEdit_stx = QtWidgets.QLineEdit(widget)
        self.lineEdit_stx.setGeometry(QtCore.QRect(40, 620, 91, 20))
        self.lineEdit_stx.setReadOnly(True)
        self.lineEdit_stx.setObjectName("lineEdit_stx")
        self.label_stx = QtWidgets.QLabel(widget)
        self.label_stx.setGeometry(QtCore.QRect(10, 620, 16, 16))
        self.label_stx.setObjectName("label_stx")
        self.checkBox_sendgga = QtWidgets.QCheckBox(widget)
        self.checkBox_sendgga.setGeometry(QtCore.QRect(163, 591, 59, 16))
        self.checkBox_sendgga.setMouseTracking(False)
        self.checkBox_sendgga.setObjectName("checkBox_sendgga")
        self.checkBox_autoScoll = QtWidgets.QCheckBox(widget)
        self.checkBox_autoScoll.setGeometry(QtCore.QRect(382, 591, 89, 16))
        self.checkBox_autoScoll.setMouseTracking(False)
        self.checkBox_autoScoll.setCheckable(True)
        self.checkBox_autoScoll.setChecked(True)
        self.checkBox_autoScoll.setObjectName("checkBox_autoScoll")
        self.checkBox_kml = QtWidgets.QCheckBox(widget)
        self.checkBox_kml.setGeometry(QtCore.QRect(477, 591, 71, 16))
        self.checkBox_kml.setMouseTracking(False)
        self.checkBox_kml.setCheckable(True)
        self.checkBox_kml.setChecked(True)
        self.checkBox_kml.setObjectName("checkBox_kml")

        self.retranslateUi(widget)
        self.cbsbaud.setCurrentIndex(2)
        self.cbsstop.setCurrentIndex(1)
        self.cbsdata.setCurrentIndex(1)
        self.comboBox_port.setCurrentIndex(0)
        self.cbatcmd.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(widget)

    def retranslateUi(self, widget):
        _translate = QtCore.QCoreApplication.translate
        widget.setWindowTitle(_translate("widget", "FMI Ntrip Serial Tool v1.2 fmi@feyman.cn"))
        self.Serial.setTitle(_translate("widget", "Serial"))
        self.cbsbaud.setItemText(0, _translate("widget", "4800"))
        self.cbsbaud.setItemText(1, _translate("widget", "9600"))
        self.cbsbaud.setItemText(2, _translate("widget", "115200"))
        self.cbsbaud.setItemText(3, _translate("widget", "230400"))
        self.cbsbaud.setItemText(4, _translate("widget", "460800"))
        self.lsdata.setText(_translate("widget", "Databit"))
        self.cbsstop.setItemText(0, _translate("widget", "0"))
        self.cbsstop.setItemText(1, _translate("widget", "1"))
        self.lsparity.setText(_translate("widget", "Parity"))
        self.cbsparity.setItemText(0, _translate("widget", "N"))
        self.cbsparity.setItemText(1, _translate("widget", "E"))
        self.cbsparity.setItemText(2, _translate("widget", "O"))
        self.lsbaud.setText(_translate("widget", "Baud"))
        self.lsstop.setText(_translate("widget", "Stopbit"))
        self.lsport.setText(_translate("widget", "Port"))
        self.cbsdata.setItemText(0, _translate("widget", "7"))
        self.cbsdata.setItemText(1, _translate("widget", "8"))
        self.cbsdata.setItemText(2, _translate("widget", "9"))
        self.cbsport.setItemText(0, _translate("widget", "COM20"))
        self.pushButton_refresh.setText(_translate("widget", "Refresh"))
        self.pushButton_open.setText(_translate("widget", "Open"))
        self.Ntrip.setTitle(_translate("widget", "Ntrip"))
        self.lnuser.setText(_translate("widget", "User"))
        self.lncaster.setText(_translate("widget", "Caster"))
        self.pushButton_conn.setText(_translate("widget", "Connect"))
        self.lnpwd.setText(_translate("widget", "Passwd"))
        self.lnport.setText(_translate("widget", "Port"))
        self.comboBox_mount.setItemText(0, _translate("widget", "Obs"))
        self.comboBox_mount.setItemText(1, _translate("widget", "Eph"))
        self.comboBox_mount.setItemText(2, _translate("widget", "P628"))
        self.comboBox_mount.setItemText(3, _translate("widget", "P328_ATLAS"))
        self.comboBox_caster.setItemText(0, _translate("widget", "ntrips.feymani.cn"))
        self.comboBox_caster.setItemText(1, _translate("widget", "219.142.87.107"))
        self.comboBox_caster.setItemText(2, _translate("widget", "219.142.87.73"))
        self.lnmount.setText(_translate("widget", "Mount"))
        self.comboBox_port.setItemText(0, _translate("widget", "2102"))
        self.comboBox_port.setItemText(1, _translate("widget", "2101"))
        self.comboBox_port.setItemText(2, _translate("widget", "81"))
        self.ATCmd.setTitle(_translate("widget", "AT Cmd"))
        self.cbatcmd.setItemText(0, _translate("widget", "AT+COLD_RESET"))
        self.cbatcmd.setItemText(1, _translate("widget", "AT+WARM_RESET"))
        self.cbatcmd.setItemText(2, _translate("widget", "AT+SHUTDOWN"))
        self.cbatcmd.setItemText(3, _translate("widget", "AT+SAVE_ALL"))
        self.cbatcmd.setItemText(4, _translate("widget", "AT+THIS_PORT"))
        self.cbatcmd.setItemText(5, _translate("widget", "AT+READ_PARA"))
        self.cbatcmd.setItemText(6, _translate("widget", "AT+UPDATE_MODE"))
        self.cbatcmd.setItemText(7, _translate("widget", "AT+SELF_TEST="))
        self.cbatcmd.setItemText(8, _translate("widget", "AT+GPGGA=UART1,"))
        self.cbatcmd.setItemText(9, _translate("widget", "AT+GPRMC=UART1,"))
        self.cbatcmd.setItemText(10, _translate("widget", "AT+GPVTG=UART1,"))
        self.cbatcmd.setItemText(11, _translate("widget", "AT+GPSAT=UART1,"))
        self.cbatcmd.setItemText(12, _translate("widget", "AT+GPGST=UART1,"))
        self.cbatcmd.setItemText(13, _translate("widget", "AT+GPZDA=UART1,"))
        self.cbatcmd.setItemText(14, _translate("widget", "AT+GPREF=UART1,"))
        self.cbatcmd.setItemText(15, _translate("widget", "AT+VEHICLE_MODE="))
        self.cbatcmd.setItemText(16, _translate("widget", "AT+ALT_PARA=-9.1,37,1"))
        self.cbatcmd.setItemText(17, _translate("widget", "AT+LEVER_ARM=0.01,-0.027,-0.1"))
        self.cbatcmd.setItemText(18, _translate("widget", "AT+ACTIVATE_KEY="))
        self.open_file.setText(_translate("widget", "File"))
        self.trans_file.setText(_translate("widget", "Trans"))
        self.pushButton_atcmd.setText(_translate("widget", "Send"))
        self.checkBox_savenmea.setText(_translate("widget", "Save NMEA"))
        self.checkBox_ggafmt.setText(_translate("widget", "GGA Deg"))
        self.Infos.setTitle(_translate("widget", "States"))
        self.label_9.setText(_translate("widget", "Direction"))
        self.label_11.setText(_translate("widget", "Base Lon"))
        self.label_8.setText(_translate("widget", "Base Hgt"))
        self.label_10.setText(_translate("widget", "Rov Lon"))
        self.label_7.setText(_translate("widget", "Rov Hgt"))
        self.label_18.setText(_translate("widget", "DOP"))
        self.label_12.setText(_translate("widget", "Num Sats"))
        self.label_17.setText(_translate("widget", "Base ID  "))
        self.label_16.setText(_translate("widget", "Sol Stat"))
        self.label_13.setText(_translate("widget", "Rov Lat"))
        self.label_14.setText(_translate("widget", "Base Lat"))
        self.label_15.setText(_translate("widget", "Time Now"))
        self.lineEdit.setText(_translate("widget", "Feyman Innovation Ntrip Serial Tool, feel free to use! "))
        self.pushButton_close.setText(_translate("widget", "Close"))
        self.pushButton_stop.setText(_translate("widget", "Stop"))
        self.pushButton_clear.setText(_translate("widget", "Clear"))
        self.label_srx.setText(_translate("widget", "Rx"))
        self.label_stx.setText(_translate("widget", "Tx"))
        self.checkBox_sendgga.setText(_translate("widget", "Tx GGA"))
        self.checkBox_autoScoll.setText(_translate("widget", "Auto Scroll"))
        self.checkBox_kml.setText(_translate("widget", "Auto kml"))
