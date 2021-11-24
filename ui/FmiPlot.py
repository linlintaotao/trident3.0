"""
 this class is use for draw realtime track and NEU position
"""
import time

from gui.plotdialog import Ui_Dialog
from PyQt5.QtWidgets import QDialog, QGridLayout
import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import QtCore
from extools import rtkcmn
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QThread, pyqtSignal
import queue
from collections import deque

COLOR_TUPLE = ['black', 'red', 'cyan', '', 'green', 'blue', 'yellow']
# COLOR_TUPLE = ['b', 'r', 'c', '', 'g', 'b', 'y']
TYPE = ['GndTrk', 'Position', 'State']


class Fmiplot(QDialog, Ui_Dialog):

    def __init__(self, parent=None):
        super(Fmiplot, self).__init__(parent)
        self._isRunning = True
        self.setupUi(self)
        self.initView()
        self.glw = pg.GraphicsLayoutWidget()
        pg.setConfigOption("useOpenGL", True)
        self.glw.setBackground(background='w')
        layout = QGridLayout()
        layout.addWidget(self.glw)
        self.widget.setLayout(layout)
        self.threadAnalysis = AnalysisThread()
        self.threadAnalysis.signal.connect(self.updatePic)
        self.threadAnalysis.start()

        self.currentType = 0
        # self.time = []
        # self.pointData = []
        # self.xList = []
        # self.yList = []
        # self.dataN = []
        # self.dataE = []
        # self.dataU = []
        # self.satNum = []
        # self.dAge = []
        # self.fixState = []
        # self.colorList = []
        #
        # self.x0 = 0
        # self.y0 = 0
        # self.N = 0
        # self.E = 0
        # self.U = 0
        # self.init = True

        self.itemTop = None
        self.itemMid = None
        self.itemBot = None
        self.initGndTrk()

    def initGndTrk(self):
        self.pgPlot = self.glw.addPlot()
        self.scatter = self.pgPlot.plot(symbolPen=None, symbolSize=4)
        self.pgPlot.showGrid(True, True)

    def initplotItems(self, supportNEU=True):

        top = self.glw.addPlot(row=0, col=0, title="E-W(m)" if supportNEU else 'FixState', connect='pairs')
        top.showGrid(True, True)
        top.showAxes((True, False, False, False), showValues=(True, None, None, None))
        mid = self.glw.addPlot(row=1, col=0, title="N-S(m)" if supportNEU else 'SatNum', connect='pairs')
        mid.setXLink(top)
        mid.showGrid(True, True)
        mid.showAxes((True, False, False, False), showValues=(True, None, None, None))
        bottom = self.glw.addPlot(row=2, col=0, title="U-D(m)" if supportNEU else 'DAge',
                                  axisItems={'bottom': pg.DateAxisItem()}, connect='pairs')
        bottom.setXLink(top)
        bottom.showGrid(True, True)
        self.itemTop = top.plot(symbolPen=None, symbolSize=4)
        self.itemMid = mid.plot(symbolPen=None, symbolSize=4)
        self.itemBot = bottom.plot(symbolPen=None, symbolSize=4)

    def initView(self):
        self.refresh.clicked.connect(self.clear)
        self.typeSelect.currentIndexChanged.connect(self.changeType)
        self.stateSelect.currentIndexChanged.connect(self.qualityChanged)

    def changeType(self):
        self.clearItem()
        self.glw.clear()
        if self.typeSelect.currentText() == TYPE[0]:
            self.currentType = 0
            self.initGndTrk()
        elif self.typeSelect.currentText() == TYPE[1]:
            self.currentType = 1
            self.initplotItems(supportNEU=True)
        elif self.typeSelect.currentText() == TYPE[2]:
            self.currentType = 2
            self.initplotItems(supportNEU=False)

    def qualityChanged(self):
        pass

    def clear(self):
        self.threadAnalysis.clear()
        # self.init = True
        # self.time.clear()
        # self.pointData.clear()
        # self.xList.clear()
        # self.yList.clear()
        # self.dataN.clear()
        # self.dataE.clear()
        # self.dataU.clear()
        # self.satNum.clear()
        # self.dAge.clear()
        # self.fixState.clear()
        # self.colorList.clear()
        # self.x0 = 0
        # self.y0 = 0
        # self.N = 0
        # self.E = 0
        # self.U = 0
        # self.clearItem()

    def clearItem(self):
        if self.scatter is not None:
            self.scatter.clear()
            self.scatter = None
        if self.itemTop is not None:
            self.itemTop.clear()
            self.itemTop = None
        if self.itemMid is not None:
            self.itemMid.clear()
            self.itemMid = None
        if self.itemBot is not None:
            self.itemBot.clear()
            self.itemBot = None

    # self.plotDialog.addPoint((latd, lond, int(solstat), int(nsats), float(hgt), float(dage), now))
    def addPoint(self, point):
        # self.initData(point)
        # self.parseData(point)
        # self.updatePic() /
        print(point)
        self.threadAnalysis.analysis(point)

    # def initData(self, point):
    #     if self.init:
    #         x, y = rtkcmn.LatLon2XY(point[0], point[1])
    #         self.x0 = x
    #         self.y0 = y
    #         self.N = point[0]
    #         self.E = point[1]
    #         self.U = point[4]
    #         self.init = False

    # def parseData(self, point):
    #     x, y = rtkcmn.LatLon2XY(point[0], point[1])
    #     x_ = x - self.x0
    #     y_ = y - self.y0
    #     self.xList.append(x_)
    #     self.yList.append(y_)
    #
    #     diffN = rtkcmn.diffN(point[0], self.N)
    #     diffE = rtkcmn.diffE(point[1], self.E)
    #     diffU = point[4] - self.U
    #     self.dataN.append(diffN)
    #     self.dataE.append(diffE)
    #     self.dataU.append(diffU)
    #
    #     self.time.append(point[-1])
    #     self.satNum.append(point[3])
    #     self.dAge.append(point[-2])
    #     self.fixState.append(point[2])
    #     self.colorList.append(COLOR_TUPLE[point[2]])

    def updatePic(self, data):
        print("updatePic")
        if self.currentType == 0:
            self.scatter.setData(x=data[1], y=data[0], symbolBrush=data[8], size=4)
            print(len(self.scatter.getData()[0]))
        elif self.currentType == 1:
            self.itemTop.setData(y=data[2], symbolBrush=data[8], size=4)
            self.itemMid.setData(y=data[3], symbolBrush=data[8], size=4)
            self.itemBot.setData(y=data[4], symbolBrush=data[8], size=4)
            print(len(self.itemTop.getData()[0]))

        elif self.currentType == 2:
            self.itemTop.setData(y=data[7], symbolBrush=data[8], size=4)
            self.itemMid.setData(y=data[5], symbolBrush=data[8], size=4)
            self.itemBot.setData(y=data[6], symbolBrush=data[8], size=4)

    def stop(self):
        pass

    def isRunning(self):
        return self._isRunning

    def closeEvent(self, QCloseEvent):
        self._isRunning = False
        self.threadAnalysis.stopSelf()


class AnalysisThread(QThread):
    signal = pyqtSignal(list)

    def __init__(self):
        super(AnalysisThread, self).__init__()
        self.isStop = False

        self.maxLen = 2000
        self.time = deque(maxlen=self.maxLen)
        self.pointData = deque(maxlen=self.maxLen)
        self.xList = deque(maxlen=self.maxLen)
        self.yList = deque(maxlen=self.maxLen)
        self.dataN = deque(maxlen=self.maxLen)
        self.dataE = deque(maxlen=self.maxLen)
        self.dataU = deque(maxlen=self.maxLen)
        self.satNum = deque(maxlen=self.maxLen)
        self.dAge = deque(maxlen=self.maxLen)
        self.fixState = deque(maxlen=self.maxLen)
        self.colorList = deque(maxlen=self.maxLen)

        self.x0 = 0
        self.y0 = 0
        self.N = 0
        self.E = 0
        self.U = 0
        self.init = True

        self.cache = queue.Queue()

    def run(self):
        while not self.isStop:
            receiveData = False
            while self.cache.qsize() > 0:
                point = self.cache.get()
                self.initData(point)
                self.parseData(point)
                receiveData = True
            if receiveData:
                self.updateSignal()
            time.sleep(0.05)

    def analysis(self, point):
        self.cache.put(point)

    def initData(self, point):
        if self.init:
            x, y = rtkcmn.LatLon2XY(point[0], point[1])
            self.x0 = x
            self.y0 = y
            self.N = point[0]
            self.E = point[1]
            self.U = point[4]
            self.init = False

    def parseData(self, point):
        x, y = rtkcmn.LatLon2XY(point[0], point[1])
        x_ = x - self.x0
        y_ = y - self.y0
        self.xList.append(x_)
        self.yList.append(y_)

        diffN = rtkcmn.diffN(point[0], self.N)
        diffE = rtkcmn.diffE(point[1], self.E)
        diffU = point[4] - self.U
        self.dataN.append(diffN)
        self.dataE.append(diffE)
        self.dataU.append(diffU)

        self.time.append(point[-1])
        self.satNum.append(point[3])
        self.dAge.append(point[-2])
        self.fixState.append(point[2])
        self.colorList.append(COLOR_TUPLE[point[2]])

    def clear(self):
        self.init = True
        self.time.clear()
        self.pointData.clear()
        self.xList.clear()
        self.yList.clear()
        self.dataN.clear()
        self.dataE.clear()
        self.dataU.clear()
        self.satNum.clear()
        self.dAge.clear()
        self.fixState.clear()
        self.colorList.clear()
        self.x0 = 0
        self.y0 = 0
        self.N = 0
        self.E = 0
        self.U = 0

    def updateSignal(self):
        if not self.isStop:
            self.signal.emit(
                [self.xList, self.yList, self.dataN, self.dataE,
                 self.dataU, self.satNum, self.dAge, self.fixState,
                 list(self.colorList), self.time])

    def stopSelf(self):
        self.isStop = True
