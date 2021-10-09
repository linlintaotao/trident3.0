from gui.Server import Ui_NtripTool
from gui.ntrip import Ui_ntripDialog
from gui.serial import Ui_SerialDialog
from PyQt5.QtWidgets import QDialog, QFileDialog
from streams.QThreadSerial import SerialThread
from streams.ntripClient import NtripClient
from streams.ntripServer import NtripServer
from extools.FmiConfig import FMIConfig

"""

"""
STREAM_TYPE = ['Serial', 'NtripServer', 'File']
STREAM_KEY = ['INPUT1', 'OUPUT1', 'OUPUT2']
streamInfoList = [None, None, None]
streamEntity = [None, None, None]
NTRIP_CLIENT = 'NtripClient'
NTRIP_SERVER = 'NtripServer'
SERIAL = 'Serial'
RTCM = 'RTCM'


class NtripTool(QDialog, Ui_NtripTool):

    def __init__(self, parent=None):
        super(NtripTool, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("NtripTool")
        self.initView()
        self.loadData()
        self.progressValue = 0

    def loadData(self):
        self.fmiConfig = FMIConfig()
        inputValue = self.fmiConfig.getValue(RTCM, STREAM_KEY[0])
        if inputValue is not None:
            streamInfoList[0] = inputValue.split(':')
            valueList = inputValue.split(':')
            if len(valueList) >= 2:
                self.inputType.setCurrentText(valueList[0])

        output1Value = self.fmiConfig.getValue(RTCM, STREAM_KEY[1])
        streamInfoList[1] = output1Value.split(':')
        if output1Value is not None:
            valueList = output1Value.split(':')
            if len(valueList) >= 2:
                self.outputType1.setCurrentText(valueList[0])

        output2Value = self.fmiConfig.getValue(RTCM, STREAM_KEY[2])
        streamInfoList[2] = output2Value.split(':')
        if output2Value is not None:
            valueList = output2Value.split(':')
            if len(valueList) >= 2:
                self.outputType2.setCurrentText(valueList[0])

    def initView(self):
        self.inputOpt.clicked.connect(lambda: self.setupOption(0, self.inputType.currentText()))
        self.outputOpt1.clicked.connect(lambda: self.setupOption(1, self.outputType1.currentText()))
        self.outputOpt2.clicked.connect(lambda: self.setupOption(2, self.outputType2.currentText()))
        self.startBtn.clicked.connect(self.clickEvent)

    def setupOption(self, index, dialogType):
        print(dialogType)
        if dialogType == 'Serial':
            dialog = SerialDialog(self)
            dialog.show()
            if dialog.exec_():
                streamInfoList[index] = dialog.dialogInput()
            dialog.close()
        elif dialogType == 'NtripClient':
            dialog = NtripDialog(self, isClient=True, index=index)
            dialog.show()
            if dialog.exec_():
                streamInfoList[index] = dialog.dialogInput()
            dialog.close()
        elif dialogType == 'NtripServer':
            dialog = NtripDialog(self, index=index)
            dialog.show()
            if dialog.exec_():
                streamInfoList[index] = dialog.dialogInput()
            dialog.close()
        elif dialogType == 'File':
            filename, filetype = QFileDialog.getOpenFileName(self, "Select file", "./",
                                                             "All Files (*);;Text Files (*.txt)")
            print(filename)

    def clickEvent(self):
        print(self.startBtn.text())
        if self.startBtn.text() == "Start":
            self.start()
        else:
            self.stop()

    def start(self):
        self.startBtn.setText("Stop")
        self.inputType.setEnabled(False)
        self.outputType1.setEnabled(False)
        self.outputType2.setEnabled(False)
        self.inputOpt.setEnabled(False)
        self.outputOpt1.setEnabled(False)
        self.outputOpt2.setEnabled(False)

        index = 0
        for streamInfo in streamInfoList:
            if streamInfo is None and len(streamInfo) > 1:
                continue
            if streamInfo[0] == SERIAL:
                streamEntity[index] = SerialThread(streamInfo[1], streamInfo[2])
            elif streamInfo[0] == NTRIP_SERVER:
                streamEntity[index] = NtripServer(ip=streamInfo[1], port=int(streamInfo[2]), mountPoint=streamInfo[3],
                                                  pwd=streamInfo[5])
            elif streamInfo[0] == NTRIP_CLIENT:
                streamEntity[index] = NtripClient(ip=streamInfo[1], port=int(streamInfo[2]), mountPoint=streamInfo[3],
                                                  user=streamInfo[4],
                                                  password=streamInfo[5], useSignal=True)
            else:
                # nothing
                pass
            index += 1

        print(streamInfoList[0])

        '''
        ('NtripClient', 'ntrips.feymani.cn', '2102', 'Obs', 'feyman-user', '123456')
        ('Serial', 'COM2', '115200')
        '''
        strInfo1, strInfo2, strInfo3 = "", "", ""
        if streamEntity[0] is not None:
            if streamInfoList[0][0] == SERIAL:
                strInfo1 = streamInfoList[0][1]
            else:
                strInfo1 = streamInfoList[0][1] + "/" + streamInfoList[0][3]
            streamEntity[0].signal.connect(self.inputData)
            streamEntity[0].start()
        if streamEntity[1] is not None:
            if streamInfoList[0][0] == SERIAL:
                strInfo2 = streamInfoList[1][1]
            else:
                strInfo2 = streamInfoList[1][1] + "/" + streamInfoList[1][3]
            streamEntity[1].start()
        if streamEntity[2] is not None:
            streamEntity[2].start()
        self.stateLabel.setText(f"(1)%s (2)%s" % (strInfo1, strInfo2))

    def stop(self):
        self.startBtn.setText("Start")
        self.inputType.setEnabled(True)
        self.outputType1.setEnabled(True)
        self.outputType2.setEnabled(True)
        self.inputOpt.setEnabled(True)
        self.outputOpt1.setEnabled(True)
        self.outputOpt2.setEnabled(True)
        for stream in streamEntity:
            if stream is not None:
                stream.stop()

    def showLog(self):
        pass

    def inputData(self, byteData):
        self.progressValue = (self.progressValue + 5) % 100
        streamEntity[1].write(byteData)
        self.progressBar.setValue(self.progressValue)
        pass


class SerialDialog(QDialog, Ui_SerialDialog):

    def __init__(self, parent=None, index=0):
        super(SerialDialog, self).__init__(parent=parent)
        self.setupUi(self)
        self.key = STREAM_KEY[index]
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.fmiConfig = FMIConfig()

    def loadData(self):
        strParameters = self.fmiConfig.getValue(RTCM, self.key)
        if strParameters is not None:
            values = strParameters.split(':')
            self.serialport.setCurrentText(values[1])
            self.baudrate.setCurrentText(values[2])
            pass

    def dialogInput(self):
        self.fmiConfig.saveNtripValue(RTCM, self.key,
                                      f"%s:%s:%s" % (SERIAL, self.serialport.currentText(),
                                                     self.baudrate.currentText()))
        return SERIAL, self.serialport.currentText(), self.baudrate.currentText()


class NtripDialog(QDialog, Ui_ntripDialog):

    def __init__(self, parent=None, isClient=False, index=0):
        super(NtripDialog, self).__init__(parent=parent)
        self.key = STREAM_KEY[index]
        self.isClient = isClient
        self.ntripType = NTRIP_CLIENT if isClient else NTRIP_SERVER
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.loadData()

    def loadData(self):
        self.fmiConfig = FMIConfig()
        strParameters = self.fmiConfig.getValue(RTCM, self.key)
        if strParameters is not None:
            self.udpateUI(strParameters)

    def udpateUI(self, strParameters):
        values = strParameters.split(":")
        if len(values) < 5:
            return
        self.ip.setCurrentText(values[1])
        self.port.setCurrentText(values[2])
        self.mountPoint.setText(values[3])
        self.pwd.setText(values[5])
        if self.isClient:
            self.username.setText(values[4])
        else:
            self.username.setEnabled(False)

    def dialogInput(self):
        self.fmiConfig.saveNtripValue(RTCM, self.key,
                                      f"%s:%s:%s:%s:%s:%s" % (self.ntripType, self.ip.currentText(),
                                                              self.port.currentText(), self.mountPoint.text(),
                                                              self.username.text(), self.pwd.text()))
        return self.ntripType, self.ip.currentText(), self.port.currentText(), \
               self.mountPoint.text(), self.username.text(), \
               self.pwd.text()
