#!-*-coding:utf-8 -*-
"""
    this file is used to save user Settings
    such as :
        1. ntrip parameter
        2. cmd

"""
from PyQt5.QtCore import QSettings

KEY_NTRIP = "Ntrip"

VEH_MODE = ['AT+NAVI_RATE=5\r\n', 'AT+GPGGA=UART1,1\r\n', 'AT+GPRMC=UART1,1\r\n',
            'AT+GPREF=UART1,0.1\r\n', 'AT+WORK_MODE=13\r\n', 'AT+DR_TIME=600\r\n',
            'AT+ALIGN_VEL=3\r\n', 'AT+RTK_DIFF=5\r\n', 'AT+SAVE_ALL\r\n',
            'AT+READ_PARA\r\n', 'AT+WARM_RESET\r\n']
UAV_MODE = ['AT+NAVI_RATE=10\r\n', 'AT+GPGGA=UART1,10\r\n', 'AT+GPRMC=UART1,10\r\n',
            'AT+GPREF=UART1,0.1\r\n', 'AT+WORK_MODE=8\r\n', 'AT+DR_TIME=10\r\n',
            'AT+ALIGN_VEL=0.5\r\n', 'AT+RTK_DIFF=5\r\n', 'AT+SAVE_ALL\r\n',
            'AT+READ_PARA\r\n', 'AT+WARM_RESET\r\n']


class FMIConfig:

    def __init__(self):
        self.config = QSettings('FMI.ini', QSettings.IniFormat)
        pass

    def saveNtripValue(self, group, key, value):
        self.config.beginGroup(group)
        self.config.setValue(key, value)
        self.config.endGroup()

    def getValue(self, group, key):
        self.config.beginGroup(group)
        value = self.config.value(key, "")
        self.config.endGroup()
        return value

    def getValueArray(self, group, keyList):
        values = []
        self.config.beginGroup(group)
        for key in keyList:
            values.append(self.config.value(key, ""))
        self.config.endGroup()
        return values

    def getGroupKeys(self, group):
        try:
            self.config.beginGroup(group)
            keys = self.config.childKeys()
            self.config.endGroup()
            return keys
        except Exception as e:
            print(e)
        return None

    def clear(self):
        self.config.clear()

    def getCmdComb(self, CMD):
        if "VEH_MODE" in CMD:
            return VEH_MODE
        elif "UAV_MODE" in CMD:
            return UAV_MODE
        return CMD


if __name__ == '__main__':
    fmiConfig = FMIConfig()
    NTRIP = "NRTRIP"
    fmiConfig.saveNtripValue(NTRIP, "ntrip.py.feymani.cn2", "2102:Obs:feyman-user:123456")
    fmiConfig.saveNtripValue(NTRIP, "ntrip.py.feymani.cn1", "2102:Obs:feyman-user:123451")
    print(fmiConfig.getGroupKeys(NTRIP))
