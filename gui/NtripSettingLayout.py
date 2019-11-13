# -*- coding: utf-8 -*-
""" 
 Created on 11/13/2019 9:26 AM
 
 @author : chey
 
"""
import sys
import os
import socket
import configparser

from PyQt5.QtWidgets import (QWidget, QApplication, QComboBox, QLabel, QPushButton, QHBoxLayout,
                             QVBoxLayout, QToolTip, QMessageBox, QLineEdit)
from PyQt5.QtGui import (QIcon, QFont)


class NtripSettingLayout(QWidget):
    def __init__(self, open_callback=None, close_callback=None):
        """
        init ntrip layout
        :param open_callback:
        :param close_callback:
        """
        super(NtripSettingLayout, self).__init__()


        # ntrip ui settings
        self.open_close_button = QPushButton(u'Open')
        self.refresh_button = QPushButton(u'Refresh')

        self.ntrip_setting_layout = QVBoxLayout()

        self.ntrip_caster_comboBox = QComboBox()
        self.ntrip_port_ledit = QLineEdit()
        self.ntrip_mount_comboBox = QComboBox()
        self.ntrip_user_ledit = QLineEdit()
        self.ntrip_passwd_ledit = QLineEdit()

        # save ntrip configurations
        self.cfg_ntrip_dic = {}
        self.current_path = os.path.dirname(os.path.realpath(__file__))
        self.cfg_path = ''
        self.cfg_dir = 'settings'
        self.conf_file_name = "ntrip.ini"
        self.confParse = configparser.ConfigParser()
        self.is_ntrip_open = False

        self.ntrip_open_callback = open_callback
        self.ntrip_close_callback = close_callback
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
        # load ntrip configuration file
        self.cfg_path = os.path.join(self.current_path, self.cfg_dir, self.conf_file_name)
        if self.confParse.read(self.cfg_path, encoding='utf-8'):
            try:
                items = self.confParse.items('ntrip_setting')
                self.cfg_ntrip_dic = dict(items)

            except configparser.NoSectionError:
                self.confParse.add_section('ntrip_setting')
                self.confParse.write(open(self.cfg_path, 'w'))
        else:
            if not os.path.exists(os.path.join(self.current_path, self.cfg_dir)):
                os.mkdir(os.path.join(self.current_path, self.cfg_dir))

            self.confParse.add_section('ntrip_setting')
            self.confParse.write(open(self.cfg_path, 'w'))

    def init_setting_layout(self):
        """
        init ntrip layout
        :return:
        """
        ntrip_caster_comboBox = QLabel(u'Caster')
        self.ntrip_caster_comboBox.addItems(self.get_port_list())
        self.ntrip_caster_comboBox.setCurrentText(self.cfg_ntrip_dic.get('caster', 'ntrips.feymani.cn'))

        ntrip_port_ledit = QLabel(u'Port')
        self.ntrip_port_ledit.addItems(['83', '87', '2101', '2102'])

        ntrip_mount_comboBox = QLabel(u'Mount')
        self.ntrip_mount_comboBox.addItems(['Obs'])
        self.ntrip_mount_comboBox.setCurrentText(self.cfg_ntrip_dic.get('mnt', 'Obs'))

        ntrip_user_ledit = QLabel(u'User')

        self.ntrip_user_ledit.addItems(['feyman-user'])

        ntrip_passwd_ledit = QLabel(u'Passwd')
        self.ntrip_passwd_ledit.addItems(['123456'])


        # set buttons
        QToolTip.setFont(QFont('SansSerif', 10))
        self.open_close_button.setToolTip("open or close selected port")
        self.refresh_button.setToolTip("refresh current port")
        self.open_close_button.clicked.connect(self.open_close_button_handle)
        self.refresh_button.clicked.connect(self.refresh_button_handle)

        # set layouts
        ntrip_com_layout = QHBoxLayout()
        ntrip_com_layout.addWidget(ntrip_com_label)
        ntrip_com_layout.addWidget(self.ntrip_COM_comboBox)

        # set baud rate horizontal layout
        ntrip_baud_rate_layout = QHBoxLayout()
        ntrip_baud_rate_layout.addWidget(ntrip_baud_rate_label)
        ntrip_baud_rate_layout.addWidget(self.ntrip_baudRate_comboBox)

        # set data bit horizontal layout
        ntrip_data_layout = QHBoxLayout()
        ntrip_data_layout.addWidget(ntrip_data_label)
        ntrip_data_layout.addWidget(self.ntrip_data_comboBox)

        # set stop bit horizontal layout
        ntrip_stop_bits_layout = QHBoxLayout()
        ntrip_stop_bits_layout.addWidget(ntrip_stop_bits_label)
        ntrip_stop_bits_layout.addWidget(self.ntrip_stopBits_comboBox)

        # set parity check horizontal layout
        ntrip_parity_layout = QHBoxLayout()
        ntrip_parity_layout.addWidget(ntrip_parity_label)
        ntrip_parity_layout.addWidget(self.ntrip_parity_comboBox)

        # set button horizontal layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.open_close_button)
        button_layout.addWidget(self.refresh_button)

        # set widgets horizontal layout
        self.ntrip_setting_layout.addLayout(ntrip_com_layout)
        self.ntrip_setting_layout.addLayout(ntrip_baud_rate_layout)
        self.ntrip_setting_layout.addLayout(ntrip_data_layout)
        self.ntrip_setting_layout.addLayout(ntrip_stop_bits_layout)
        self.ntrip_setting_layout.addLayout(ntrip_parity_layout)
        self.ntrip_setting_layout.addLayout(button_layout)

    @staticmethod
    def get_port_list():
        """
        get current ntrip port list
        :return:
        """
        com_list = []
        port_list = ntrip.tools.list_ports.comports()
        for port in port_list:
            com_list.append(port[0])
        return com_list

    def save_config(self):
        """
        save configurations
        :return:
        """
        self.confParse.set('ntrip_setting', 'com', self.ntrip.port)
        self.confParse.set('ntrip_setting', 'baudrate', str(self.ntrip.baudrate))
        self.confParse.set('ntrip_setting', 'data', str(self.ntrip.bytesize))
        self.confParse.set('ntrip_setting', 'stopbit', str(self.ntrip.stopbits))
        self.confParse.set('ntrip_setting', 'parity', self.ntrip.parity)
        self.confParse.write(open(self.cfg_path, 'w'))

    def get_ntrip_setting(self):
        """
        :return:
        """
        self.ntrip.port = self.ntrip_COM_comboBox.currentText()
        self.ntrip.baudrate = int(self.ntrip_baudRate_comboBox.currentText())
        self.ntrip.bytesize = int(self.ntrip_data_comboBox.currentText())
        self.ntrip.stopbits = int(self.ntrip_stopBits_comboBox.currentText())
        self.ntrip.parity = self.ntrip_parity_comboBox.currentText()
        self.ntrip.timeout = 0

    def open_ntrip(self):
        """

        :return:
        """
        self.get_ntrip_setting()
        self.save_config()

        try:
            self.ntrip.open()
        except ntrip.SerialException:
            QMessageBox.critical(self, "Critical", f"Open {self.ntrip.port} failed!")  # 打开失败，弹窗提示
        else:
            self.is_ntrip_open = True
            self.open_close_button.setText(u'close')
            self.enable_ntrip_setting(False)
            self.ntrip_open_callback()

    def close_ntrip(self):
        """

        :return:
        """
        self.is_ntrip_open = False
        self.open_close_button.setText(u'open')
        self.enable_ntrip_setting(True)
        self.ntrip_close_callback()
        self.ntrip.close()

    def open_close_button_handle(self):
        """
        :return:
        """
        if self.is_ntrip_open:
            self.close_ntrip()
        else:
            self.open_ntrip()

    def refresh_button_handle(self):
        """

        :return:
        """
        self.ntrip_COM_comboBox.clear()
        self.ntrip_COM_comboBox.addItems(self.get_port_list())

    def enable_ntrip_setting(self, enable):
        """

        :param enable:
        :return:
        """
        self.refresh_button.setEnabled(enable)
        self.ntrip_parity_comboBox.setEnabled(enable)
        self.ntrip_stopBits_comboBox.setEnabled(enable)
        self.ntrip_data_comboBox.setEnabled(enable)
        self.ntrip_baudRate_comboBox.setEnabled(enable)
        self.ntrip_COM_comboBox.setEnabled(enable)

    def get_ntrip_setting_layout(self):
        """

        :return:
        """
        return self.ntrip_setting_layout

    def ntrip_readline(self):
        """

        :return:
        """
        if self.is_ntrip_open:
            try:
                text_line = self.ntrip.readline()
            except Exception as e:
                print(e)
                self.close_ntrip()
            else:
                return text_line.decode("utf-8", "ignore")
        else:
            return ""

    def ntrip_write(self, data):
        """

        :param data:
        :return:
        """
        if self.is_ntrip_open:
            try:
                self.ntrip.write(data.encode("utf-8", "ignore"))
            except Exception as e:
                print(e)

    def set_frame(self):
        """

        :return:
        """
        self.setLayout(self.ntrip_setting_layout)

        self.setWindowTitle('FST (FMI Serial Tool)')

        self.setWindowIcon(QIcon('settings/logo.png'))
        self.resize(800, 600)

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = SerialSettingLayout()
    w.set_frame()
    sys.exit(app.exec_())