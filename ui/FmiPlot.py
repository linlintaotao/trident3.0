"""
 this class is use for draw realtime track and NEU position
"""
from gui.plotdialog import Ui_Dialog
from PyQt5.QtWidgets import QDialog, QGridLayout
import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import QtCore


class Fmiplot(QDialog, Ui_Dialog):

    def __init__(self, parent=None):
        super(Fmiplot, self).__init__(parent)
        self.setupUi(self)
        self.pgPlot = pg.PlotWidget()
        girdWidget = QGridLayout()
        girdWidget.addWidget(self.pgPlot)
        self.widget.setLayout(girdWidget)
        self.nmeaPos = self.pgPlot.plot(pen=(100, 100, 100), symbolBrush=(255, 0, 0), symbolPen='w')
        self.timer = QtCore.QTimer()  # 实例化一个计时器
        self.timer.timeout.connect(self.update)  # 计时器信号连接到update()函数
        self.timer.start(200)  # 计时器间隔200毫秒
        self.data = np.array()

    def plotData(self, data):
        self.nmeaPos.setData
        pass

    def update(self):
        print("update")
        self.nmeaPos.setData(np.random.normal(size=100))
        # self.pgPlot.plot(np.random.normal(size=100), pen=(200, 200, 200), symbolBrush=(255, 0, 0), symbolPen='w',
        #                  clear=True)

    def stop(self):
        pass
