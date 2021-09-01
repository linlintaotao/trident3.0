import random
import sys
from PyQt5.QtCore import (QSize, QTimer, QVariant, Qt, pyqtSignal)
from PyQt5.QtWidgets import (QApplication, QDialog, QHBoxLayout, QDesktopWidget, QWidget)
from PyQt5.QtGui import QColor, QPainter, QPixmap, QFont, QPen
from extools.RtcmParse import RtcmParse


class BarGraphModel(QWidget):
    dataChanged = pyqtSignal()

    def __init__(self):
        super(BarGraphModel, self).__init__()
        self.__data = []
        self.name = ""

    def len(self):
        return len(self.__data)

    def clear(self):
        self.__data.clear()

    def setData(self, data):
        self.__data.append(data)

    def update(self):
        self.dataChanged.emit()

    def data(self):
        return self.__data


class BarGraphView(QWidget):
    WIDTH = 12

    def __init__(self, parent=None):

        super(BarGraphView, self).__init__(parent)
        self.model = None
        self.painter = QPainter(self)
        self.colorL5 = QColor(Qt.blue)
        self.colorL1 = QColor(Qt.green)
        self.colorInvalid = QColor(Qt.gray)
        self.colorInvalid = QColor(Qt.gray)

    def setModel(self, model):
        self.model = model
        self.model.dataChanged.connect(self.update)
        self.pen = QPen(Qt.black, 0.1, Qt.SolidLine)

    def sizeHint(self):
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        if self.model is None:
            return QSize(BarGraphView.WIDTH * 10, 100)

        return QSize(BarGraphView.WIDTH * self.model.len(), 100)

    def paintEvent(self, event):
        if self.model is None:
            return
        self.painter.begin(self)
        self.painter.setPen(self.pen)
        self.painter.setFont(QFont('KaiTi', 2))
        self.painter.setRenderHint(QPainter.Antialiasing)

        span = 60
        length = self.model.len() if self.model.len() >= 10 else 10
        self.painter.setWindow(0, 0, BarGraphView.WIDTH * length + 12, span + 6)
        start = 16
        self.painter.fillRect(start + 4, 1, 4, 2, self.colorL1)
        self.painter.drawText(start, 3, "L1")
        self.painter.fillRect(start + 14, 1, 4, 2, self.colorL5)
        self.painter.drawText(start + 10, 3, "L5")
        self.painter.fillRect(start + 34, 1, 4, 2, self.colorInvalid)
        self.painter.drawText(start + 20, 3, "Invalid")
        self.painter.drawText(1, 5, "dBHz")
        for i in range(0, 6):
            if i != 0:
                self.painter.drawText(2, i * 10 + 1.5, str(60 - i * 10))
            self.painter.drawLine(6, i * 10, BarGraphView.WIDTH * length + 6, i * 10)

        row = 0

        for value in self.model.data():
            x = row * BarGraphView.WIDTH + 8
            if len(value) <= 0: continue
            color1 = self.colorL1
            color2 = self.colorL5
            y1 = self.getIndexValue(value, 0, 4)
            y2 = self.getIndexValue(value, 1, 4, -1)
            if y1 > 0:
                phase = self.getIndexValue(value, 0, 2)
                if phase == 0:
                    color1 = color2 = self.colorInvalid
            self.painter.fillRect(x, span - y1, BarGraphView.WIDTH - 4, y1, color1)
            if y2 != -1:
                self.painter.fillRect(x + 2, span - y2, BarGraphView.WIDTH - 8, y2, color2)
            self.painter.drawText(x + 2, span + 4, value[0])
            row += 1

        self.painter.end()

    @staticmethod
    def getIndexValue(valuseList, index, num, defaultValue=0):
        v = defaultValue
        try:
            if len(valuseList[index]) > 1:
                v = valuseList[1][index][num]
        except Exception as e:
            pass
        return v


class MainForm(QDialog):

    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)
        self.model = BarGraphModel()
        self.barGraphView = BarGraphView()
        self.barGraphView.setModel(self.model)
        layout = QHBoxLayout()
        layout.addWidget(self.barGraphView, 1)
        self.setLayout(layout)
        self.setWindowTitle("Obs CN0")
        self.isStart = True
        self.rtcmParse = RtcmParse()
        self.rtcmParse.msmSingnal.connect(self.updateMsg)

    def loadData(self, data):
        if self.isStart:
            self.rtcmParse.decode(data)

    def updateMsg(self, data):
        if self.isStart:
            self.model.clear()
            for key, value in data.getSatList().items():
                self.model.setData([key, value])
            self.model.update()

    def closeEvent(self, QCloseEvent):
        self.isStart = False

    def isWorking(self):
        return self.isStart


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MainForm()
    form.resize(600, 400)
    form.show()
    app.exec_()
