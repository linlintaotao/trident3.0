#!-*-coding:utf-8 -*-
"""
    this file is used to save user Settings
    such as :
        1. ntrip parameter
        2. cmd

"""
from PyQt5.QtCore import QSettings

ip = 0
port = 0
mount = 0
userName
password


class FMIConfig:

    def __init__(self):
        self.config = QSettings('FMI.ini', QSettings.IniFormat)
        pass

    def saveValue(self, key, value):
        pass

    def getValue(self, key):
        pass

    def freshHistory(self):
        pass
