"""
 this class is use for draw realtime track and NEU position
"""
import time

from gui.plotdialog import Ui_PlotView
from PyQt5.QtWidgets import QDialog, QGridLayout, QFileDialog
import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import QtCore
from extools import rtkcmn
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QThread, pyqtSignal, QTime, QTimer
import queue
from collections import deque
from extools import NmeaParser
import time
from datetime import datetime, timedelta

COLOR_TUPLE = ['black', 'red', 'cyan', '', 'green', 'blue', 'yellow']
TYPE = ['GndTrk', 'Position', 'State']


class Fmiplot(QDialog, Ui_PlotView):

    def __init__(self, parent=None):
        super(Fmiplot, self).__init__(parent)
        self.setAcceptDrops(True)
        self._isRunning = True
        self.setupUi(self)
        self.initView()
        self.glw = pg.GraphicsLayoutWidget()
        self.glw.setBackground(background='white')
        layout = QGridLayout()
        layout.addWidget(self.glw)
        self.widget.setLayout(layout)
        self.threadAnalysis = None

        self.currentType = 0
        self.itemTop = None
        self.itemMid = None
        self.itemBot = None
        self.initGndTrk()

        self.loading = False
        self.realTime = True
        self._data = []

        self.startRealTimeThread()
        self.lock = False
        self.top = None
        self.mid = None
        self.bottom = None
        self.pgPlot = None

    def startRealTimeThread(self):
        self.threadAnalysis = AnalysisThread()
        self.threadAnalysis.signal.connect(self.updatePic)
        self.threadAnalysis.start()

    def startReadFileThread(self, file):
        self.threadAnalysis = AnalysisThread(realTime=False, filePath=file)
        self.threadAnalysis.signal.connect(self.updatePic)
        self.threadAnalysis.progress.connect(self.parseProgress)
        self.threadAnalysis.start()

    def parseProgress(self, progress):
        if progress == 101:
            self.messagebox.setText(' done')
        elif progress == -1:
            self.messagebox.setText(' no solution data...')
        else:
            self.messagebox.setText(' reading file %d%%' % progress)

    def stopThread(self):
        if self.threadAnalysis is not None:
            self.threadAnalysis.stopSelf()

    def initGndTrk(self):
        self.pgPlot = self.glw.addPlot()
        self.scatter = pg.ScatterPlotItem()
        self.pgPlot.setMenuEnabled(False)  # 取消右键菜单

        self.pgPlot.addItem(self.scatter)
        self.pgPlot.showGrid(True, True)
        self.pgPlot.setXRange(-0.5, 0.5)
        self.pgPlot.setYRange(-0.5, 0.5)
        self.pgPlot.enableAutoRange(True)

    def initplotItems(self, supportNEU=True):

        self.top = self.glw.addPlot(row=0, col=0)
        self.top.showGrid(True, True)
        self.top.showAxes((True, False, False, False), showValues=(True, None, None, None))

        self.mid = self.glw.addPlot(row=1, col=0)
        self.mid.setXLink(self.top)
        self.mid.showGrid(True, True)
        self.mid.showAxes((True, False, False, False), showValues=(True, None, None, None))
        tai = TimeAxisItem(orientation='bottom')
        self.bottom = self.glw.addPlot(row=2, col=0,
                                       axisItems={'bottom': tai})
        self.bottom.setXLink(self.top)
        self.bottom.showGrid(True, True)
        self.top.setMenuEnabled(False)  # 取消右键菜单
        self.mid.setMenuEnabled(False)  # 取消右键菜单
        self.bottom.setMenuEnabled(False)  # 取消右键菜单

        if supportNEU:
            self.top.setLabel('left', 'N (m)')
            self.mid.setLabel('left', 'E (m)')
            self.bottom.setLabel('left', 'U (m)')

            self.itemTop = pg.ScatterPlotItem()
            self.itemMid = pg.ScatterPlotItem()
            self.itemBot = pg.ScatterPlotItem()
        else:
            self.top.setLabel('left', 'FixState')
            self.mid.setLabel('left', 'Sats')
            self.bottom.setLabel('left', 'DAge')
            self.itemTop = pg.ScatterPlotItem()
            self.itemMid = pg.ScatterPlotItem()
            self.itemBot = pg.ScatterPlotItem()
            self.top.setYRange(-1, 7)
            self.mid.setYRange(-1, 45)
            self.bottom.setYRange(-1, 5)

        self.top.addItem(self.itemTop)
        self.mid.addItem(self.itemMid)
        self.bottom.addItem(self.itemBot)

    def initView(self):
        self.refresh.clicked.connect(self.clear)
        self.typeSelect.currentIndexChanged.connect(self.changeType)
        self.stateSelect.currentIndexChanged.connect(self.qualityChanged)
        self.inputType.currentTextChanged.connect(self.changeInputType)
        self.toolButton.clicked.connect(self.selectFile)
        self.refreshView.clicked.connect(self.reDraw)

    def reDraw(self):
        if self.pgPlot is not None:
            self.pgPlot.enableAutoRange()
            self.pgPlot.setAutoVisible(True)
        if self.top is not None:
            self.top.enableAutoRange()
            self.top.setAutoVisible(True)
        if self.mid is not None:
            self.mid.enableAutoRange()
            self.mid.setAutoVisible(True)
        if self.bottom is not None:
            self.bottom.enableAutoRange()
            self.bottom.setAutoVisible(True)

    def selectFile(self):
        filename, filetype = QFileDialog.getOpenFileName(self, "Select file", "./", "All Files (*);;Text Files (*.txt)")
        if filename != '':
            self.dataPath.setText(filename)
            self.inputType.setCurrentText('File')
            self.startReadFileThread(filename)

    def changeInputType(self):
        if self.threadAnalysis is not None:
            self.threadAnalysis.stopSelf()
            self.threadAnalysis = None
        if self.inputType.currentText() == 'Serial':
            self.realTime = True
            self.startRealTimeThread()
            self.dataPath.setText('')
        elif self.inputType.currentText() == 'File':
            pass

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

        if len(self.threadAnalysis.getData()[0]) > 0:
            self.updatePic(self.threadAnalysis.getData())

    def qualityChanged(self):
        pass

    def clear(self):
        if self.threadAnalysis:
            self.threadAnalysis.clear()
        self.clearItem(destory=False)

    def clearItem(self, destory=True):
        if self.scatter is not None:
            self.scatter.clear()
            if destory:
                self.scatter = None
        if self.itemTop is not None:
            self.itemTop.clear()
            if destory:
                self.itemTop = None
        if self.itemMid is not None:
            self.itemMid.clear()
            if destory:
                self.itemMid = None
        if self.itemBot is not None:
            self.itemBot.clear()
            if destory:
                self.itemBot = None
        if destory:
            self.top = None
            self.mid = None
            self.bottom = None
            self.pgPlot = None

    # self.plotDialog.addPoint((latd, lond, int(solstat), int(nsats), float(hgt), float(dage), now))
    def addPoint(self, point):
        if self.threadAnalysis:
            self.threadAnalysis.addQueue(point)

    def updatePic(self, data):
        if not self.lock:
            self.lock = True
        else:
            print('========return========')
            return
        if not self.realTime:
            self.loading = False
        if self.currentType == 0:
            self.scatter.setData(x=data[1], y=data[0], brush=data[8], pen=None, size=4)
        elif self.currentType == 1:
            if not self.itemTop:
                return
            self.itemTop.setData(x=data[-1], y=data[2], brush=data[8], pen=None, size=4)
            self.itemMid.setData(x=data[-1], y=data[3], brush=data[8], pen=None, size=4)
            self.itemBot.setData(x=data[-1], y=data[4], brush=data[8], pen=None, size=4)
        elif self.currentType == 2:
            if not self.itemTop:
                return
            self.itemTop.setData(x=data[-1], y=data[7], brush=data[8], pen=None)
            self.itemMid.setData(x=data[-1], y=data[5], brush=data[8], pen=None)
            self.itemBot.setData(x=data[-1], y=data[6], brush=data[8], pen=None)
        self.lock = False

    def deleteSameData(self, dataX, dataY):
        time_X = dataX[:]
        data_Y = dataY[:]
        indexTodel = []
        for i in range(1, len(data_Y) - 2):
            if data_Y[i - 1] == data_Y[i] == data_Y[i + 1]:
                indexTodel.append(i)
        for index in range(len(indexTodel) - 1, -1, -1):
            time_X.pop(indexTodel[index])
            data_Y.pop(indexTodel[index])
        return time_X, data_Y

    def stop(self):
        pass

    def isRunning(self):
        return self._isRunning and self.threadAnalysis is not None

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, e):
        if self.loading:
            return
        filePathList = e.mimeData().urls()
        filePath = filePathList[0].toLocalFile()
        self.dataPath.setText(filePath)
        self.loading = True
        self.realTime = False
        if self.inputType.currentText() != 'File':
            self.inputType.setCurrentText('File')
        self.startReadFileThread(filePath)

    def closeEvent(self, QCloseEvent):
        self._isRunning = False
        if self.threadAnalysis:
            self.threadAnalysis.stopSelf()


class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super(TimeAxisItem, self).__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        return [int2dt(value) for value in values]


def int2dt(ts):
    return datetime.fromtimestamp(ts).strftime("%H:%M:%S")


class AnalysisThread(QThread):
    signal = pyqtSignal(list)
    progress = pyqtSignal(int)

    def __init__(self, realTime=True, filePath=None):
        super(AnalysisThread, self).__init__()
        self.isStop = False

        self.maxLen = 2000
        self.time = []
        self.pointData = []
        self.xList = []
        self.yList = []
        self.dataN = []
        self.dataE = []
        self.dataU = []
        self.satNum = []
        self.dAge = []
        self.fixState = []
        self.colorList = []

        self.x0 = 0
        self.y0 = 0
        self.N = 0
        self.E = 0
        self.U = 0
        self.init = True

        self.realTime = realTime
        self.filePath = filePath

        self.cache = queue.Queue()
        self._time = datetime.now().date()
        self.hour = 0

    def run(self):
        if self.realTime:
            while not self.isStop:
                receiveData = False
                while self.cache.qsize() > 0:
                    point = self.cache.get()
                    self.initData(point)
                    self.parseData(point)
                    receiveData = True
                if receiveData:
                    self.updateSignal()
                time.sleep(1)
        else:
            self.readFile(self.filePath)

    def addQueue(self, point):
        if not self.isStop:
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
        # print(point)
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

        self.time.append(self.nmeatime(point[-1]))
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

    def updateSignal(self, realTime=True):
        if not self.isStop:
            startIndex = 0
            if realTime:
                length = len(self.xList)
                startIndex = 0 if length < self.maxLen else length - self.maxLen
                if length > 4000:
                    self.xList = self.xList[startIndex:]
                    self.yList = self.yList[startIndex:]
                    self.dataN = self.dataN[startIndex:]
                    self.dataE = self.dataE[startIndex:]
                    self.dataU = self.dataU[startIndex:]
                    self.satNum = self.satNum[startIndex:]
                    self.dAge = self.dAge[startIndex:]
                    self.fixState = self.fixState[startIndex:]
                    self.colorList = self.colorList[startIndex:]
                    self.time = self.time[startIndex:]
                    startIndex = 0
            self.signal.emit(
                [self.xList[startIndex:], self.yList[startIndex:], self.dataN[startIndex:], self.dataE[startIndex:],
                 self.dataU[startIndex:], self.satNum[startIndex:], self.dAge[startIndex:], self.fixState[startIndex:],
                 self.colorList[startIndex:], self.time[startIndex:]])

    def getData(self):
        return [self.xList, self.yList, self.dataN, self.dataE,
                self.dataU, self.satNum, self.dAge, self.fixState,
                self.colorList, self.time]

    def readFile(self, path):
        self.clear()
        if self.filePath is None:
            return
        parseProgress = 0
        totalProgress = 1
        percentProgress = 0
        with open(path, 'rb') as rf:
            lines = rf.readlines()
            totalProgress = len(lines)
            for data in lines:
                parseProgress += 1
                try:
                    if b'$GNGGA' in data or b'$GPGGA' in data:
                        index = data.index(b'$G')
                        data = data[index:]
                        if NmeaParser.checkSum(data):
                            seg = data.strip(b"\r\n").split(b",")
                            now = seg[1]
                            solstat, nsats, dop, hgt = seg[6:10]
                            dage = seg[-2]
                            latd = NmeaParser.dformate(float(seg[2]))
                            lond = NmeaParser.dformate(float(seg[4]))
                            dage = dage if dage != b'' else b'0'
                            nsats = nsats if nsats != b'' else b'0'
                            point = (latd, lond, int(solstat), int(nsats), float(hgt), float(dage), now)
                            self.initData(point)
                            self.parseData(point)
                    intProgress = int(parseProgress / totalProgress * 100)
                    if percentProgress != intProgress:
                        self.progress.emit(percentProgress)
                        percentProgress = intProgress
                except Exception as e:
                    print(e)
                    continue
            self.updateSignal(realTime=False)
            self.progress.emit(-1 if len(self.xList) == 0 else 101)

    def stopSelf(self):
        self.isStop = True

    def nmeatime(self, dataTime):
        if isinstance(dataTime, bytes):
            dataTime = dataTime.decode()
        time = datetime.strptime(dataTime, '%H%M%S.%f')
        if time.hour == 0 and time.minute == 0 and time.second == 0 and time.microsecond == 0:
            self._time += timedelta(days=1)
        elif self.hour > time.hour:
            self._time += timedelta(days=1)
        self.hour = time.hour
        result = time.replace(year=self._time.year, month=self._time.month, day=self._time.day)
        return result.timestamp()


if __name__ == '__main__':
    dataX = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 1]
    dataY = [1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5]
    time_X = dataX[:]
    data_Y = dataY[:]
    indexTodel = []
    for i in range(1, len(data_Y) - 2):
        if data_Y[i - 1] == data_Y[i] == data_Y[i + 1]:
            indexTodel.append(i)
    print(indexTodel)
    for index in range(len(indexTodel) - 1, -1, -1):
        time_X.pop(indexTodel[index])
        data_Y.pop(indexTodel[index])
    # return time_X, data_Y
    print(time_X, data_Y)
