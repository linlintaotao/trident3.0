#!-*-coding:utf-8 -*-
"""
@desp:
@file: SerialSettingLayout.py
@date: 11/12/2019
@author: Chey
"""
# !/user/bin/python3
# -*- coding:utf-8 -*-


import sys
import os
import serial
import serial.tools.list_ports
import configparser

from PyQt5.QtWidgets import (QWidget, QApplication, QComboBox, QLabel, QPushButton, QHBoxLayout,
                             QVBoxLayout, QToolTip, QMessageBox)
from PyQt5.QtGui import (QIcon, QFont)


class SerialSettingLayout(QWidget):
    def __init__(self, open_callback=None, close_callback=None):
        """
        init serial layout
        :param open_callback:
        :param close_callback:
        """
        super(SerialSettingLayout, self).__init__()

        self.serial = serial.Serial()

        # serial ui settings
        self.open_close_button = QPushButton(u'Open')
        self.refresh_button = QPushButton(u'Refresh')

        self.serial_setting_layout = QVBoxLayout()

        self.serial_COM_comboBox = QComboBox()
        self.serial_baudRate_comboBox = QComboBox()
        self.serial_data_comboBox = QComboBox()
        self.serial_stopBits_comboBox = QComboBox()
        self.serial_parity_comboBox = QComboBox()

        # save serial configurations
        self.cfg_serial_dic = {}
        self.current_path = os.path.dirname(os.path.realpath(__file__))
        self.cfg_path = ''
        self.cfg_dir = 'settings'
        self.conf_file_name = "serial.ini"
        self.confParse = configparser.ConfigParser()
        self.is_serial_open = False

        self.serial_open_callback = open_callback
        self.serial_close_callback = close_callback
        self.init_ui()

    def init_ui(self):
        """

        :return:
        """
        self.read_config()
        self.init_setting_layout()

    def read_config(self):
        """
        :return:
        """
        # load serial configuration file
        self.cfg_path = os.path.join(self.current_path, self.cfg_dir, self.conf_file_name)
        if self.confParse.read(self.cfg_path, encoding='utf-8'):
            try:
                items = self.confParse.items('serial_setting')
                self.cfg_serial_dic = dict(items)

            except configparser.NoSectionError:
                self.confParse.add_section('serial_setting')
                self.confParse.write(open(self.cfg_path, 'w'))
        else:
            if not os.path.exists(os.path.join(self.current_path, self.cfg_dir)):
                os.mkdir(os.path.join(self.current_path, self.cfg_dir))

            self.confParse.add_section('serial_setting')
            self.confParse.write(open(self.cfg_path, 'w'))

    def init_setting_layout(self):
        """
        init serial layout
        :return:
        """
        serial_com_label = QLabel(u'Com Port')
        self.serial_COM_comboBox.addItems(self.get_port_list())
        self.serial_COM_comboBox.setCurrentText(self.cfg_serial_dic.get('com', 'COM1'))

        serial_baud_rate_label = QLabel(u'Baud Rate')
        self.serial_baudRate_comboBox.addItems(['9600', '19200', '38400', '57600', '115200', '230400', '921600'])
        self.serial_baudRate_comboBox.setCurrentText(self.cfg_serial_dic.get('baudrate', '115200'))

        serial_data_label = QLabel(u'Data Bits')
        self.serial_data_comboBox.addItems(['5', '6', '7', '8'])
        self.serial_data_comboBox.setCurrentText(self.cfg_serial_dic.get('data', '8'))

        serial_stop_bits_label = QLabel(u'Stop Bits')
        self.serial_stopBits_comboBox.addItems(['1', '1.5', '2'])
        self.serial_stopBits_comboBox.setCurrentText(self.cfg_serial_dic.get('stopbits', '1'))

        serial_parity_label = QLabel(u'Parity Check')
        self.serial_parity_comboBox.addItems(['N', 'E', 'O', 'M', 'S'])
        self.serial_parity_comboBox.setCurrentText(self.cfg_serial_dic.get('parity', 'N'))

        # set buttons
        QToolTip.setFont(QFont('SansSerif', 10))
        self.open_close_button.setToolTip("open or close selected port")
        self.refresh_button.setToolTip("refresh current port")
        self.open_close_button.clicked.connect(self.open_close_button_handle)
        self.refresh_button.clicked.connect(self.refresh_button_handle)

        # set layouts
        serial_com_layout = QHBoxLayout()
        serial_com_layout.addWidget(serial_com_label)
        serial_com_layout.addWidget(self.serial_COM_comboBox)

        # set baud rate horizontal layout
        serial_baud_rate_layout = QHBoxLayout()
        serial_baud_rate_layout.addWidget(serial_baud_rate_label)
        serial_baud_rate_layout.addWidget(self.serial_baudRate_comboBox)

        # set data bit horizontal layout
        serial_data_layout = QHBoxLayout()
        serial_data_layout.addWidget(serial_data_label)
        serial_data_layout.addWidget(self.serial_data_comboBox)

        # set stop bit horizontal layout
        serial_stop_bits_layout = QHBoxLayout()
        serial_stop_bits_layout.addWidget(serial_stop_bits_label)
        serial_stop_bits_layout.addWidget(self.serial_stopBits_comboBox)

        # set parity check horizontal layout
        serial_parity_layout = QHBoxLayout()
        serial_parity_layout.addWidget(serial_parity_label)
        serial_parity_layout.addWidget(self.serial_parity_comboBox)

        # set button horizontal layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.open_close_button)
        button_layout.addWidget(self.refresh_button)

        # set widgets horizontal layout
        self.serial_setting_layout.addLayout(serial_com_layout)
        self.serial_setting_layout.addLayout(serial_baud_rate_layout)
        self.serial_setting_layout.addLayout(serial_data_layout)
        self.serial_setting_layout.addLayout(serial_stop_bits_layout)
        self.serial_setting_layout.addLayout(serial_parity_layout)
        self.serial_setting_layout.addLayout(button_layout)

    @staticmethod
    def get_port_list():
        """
        get current serial port list
        :return:
        """
        com_list = []
        port_list = serial.tools.list_ports.comports()
        for port in port_list:
            com_list.append(port[0])
        return com_list

    def save_config(self):
        """
        save configurations
        :return:
        """
        self.confParse.set('serial_setting', 'com', self.serial.port)
        self.confParse.set('serial_setting', 'baudrate', str(self.serial.baudrate))
        self.confParse.set('serial_setting', 'data', str(self.serial.bytesize))
        self.confParse.set('serial_setting', 'stopbit', str(self.serial.stopbits))
        self.confParse.set('serial_setting', 'parity', self.serial.parity)
        self.confParse.write(open(self.cfg_path, 'w'))

    def get_serial_setting(self):
        """
        :return:
        """
        self.serial.port = self.serial_COM_comboBox.currentText()
        self.serial.baudrate = int(self.serial_baudRate_comboBox.currentText())
        self.serial.bytesize = int(self.serial_data_comboBox.currentText())
        self.serial.stopbits = int(self.serial_stopBits_comboBox.currentText())
        self.serial.parity = self.serial_parity_comboBox.currentText()
        self.serial.timeout = 0

    def open_serial(self):
        """

        :return:
        """
        self.get_serial_setting()
        self.save_config()

        try:
            self.serial.open()
        except serial.SerialException:
            QMessageBox.critical(self, "Critical", f"Open {self.serial.port} failed!")  # 打开失败，弹窗提示
        else:
            self.is_serial_open = True
            self.open_close_button.setText(u'close')
            self.enable_serial_setting(False)
            self.serial_open_callback()

    def close_serial(self):
        """

        :return:
        """
        self.is_serial_open = False
        self.open_close_button.setText(u'open')
        self.enable_serial_setting(True)
        self.serial_close_callback()
        self.serial.close()

    def open_close_button_handle(self):
        """
        :return:
        """
        if self.is_serial_open:
            self.close_serial()
        else:
            self.open_serial()

    def refresh_button_handle(self):
        """

        :return:
        """
        self.serial_COM_comboBox.clear()
        self.serial_COM_comboBox.addItems(self.get_port_list())

    def enable_serial_setting(self, enable):
        """

        :param enable:
        :return:
        """
        self.refresh_button.setEnabled(enable)
        self.serial_parity_comboBox.setEnabled(enable)
        self.serial_stopBits_comboBox.setEnabled(enable)
        self.serial_data_comboBox.setEnabled(enable)
        self.serial_baudRate_comboBox.setEnabled(enable)
        self.serial_COM_comboBox.setEnabled(enable)

    def get_serial_setting_layout(self):
        """

        :return:
        """
        return self.serial_setting_layout

    def serial_readline(self):
        """

        :return:
        """
        if self.is_serial_open:
            try:
                text_line = self.serial.readline()
            except Exception as e:
                print(e)
                self.close_serial()
            else:
                return text_line.decode("utf-8", "ignore")
        else:
            return ""

    def serial_write(self, data):
        """

        :param data:
        :return:
        """
        if self.is_serial_open:
            try:
                self.serial.write(data.encode("utf-8", "ignore"))
            except Exception as e:
                print(e)

    def set_frame(self):
        """

        :return:
        """
        self.setLayout(self.serial_setting_layout)

        self.setWindowTitle('FST (FMI Serial Tool)')

        self.setWindowIcon(QIcon('settings/logo.png'))
        self.resize(800, 600)

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = SerialSettingLayout()
    w.set_frame()
    sys.exit(app.exec_())
