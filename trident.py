# -*- coding: utf-8 -*-
""" 
 Created on 2/27/2020 2:26 PM
 
 @author : chey
 
"""
import PySimpleGUI as sg
from serial import Serial
from threading import Thread
import serial.tools.list_ports

baud_rate = (4800, 9600, 19200, 57600, 115200, 230400, 460800, 921600)
stop_bit = (1, 1.5, 2)
data_bit = (7, 8, 9, 10)
parity = ('N', 'O', 'E')

text_size = (5, 1)
comb_size = (15, 1)

caster_list = ['ntrips.feymani.cn', '219.142.87.107']
port_list = ['81', '2101', '2102']
mnt_list = ['Obs', 'Obs_fangshan', 'ATLAS', 'B990']

atcmd_list = ['COLD_RESET', 'WARM_RESET', 'SHUT_DONW', 'SAVE_ALL', '']
serial_layout = [[sg.Text('Port:', size=text_size), sg.Combo(serial.tools.list_ports.comports(), size=comb_size)],
                 [sg.Text('Baud:', size=text_size), sg.Combo(baud_rate, size=comb_size)],
                 [sg.Text('Stop:', size=text_size), sg.Combo(stop_bit, size=comb_size)],
                 [sg.Text('Data:', size=text_size), sg.Combo(data_bit, size=comb_size)],
                 [sg.Text('Parity:', size=text_size), sg.Combo(parity, size=comb_size)],
                 [sg.RButton('Connect', size=(20, 1), key='-SER_CONNECT-')]]

ntrip_layout = [[sg.Text('Caster:', size=text_size), sg.Combo(caster_list, key='-NTP_CASTER-', size=comb_size)],
                [sg.Text('Port:', size=text_size), sg.Combo(port_list, key='-NTP_PORT-', size=comb_size)],
                [sg.Text('Mount:', size=text_size), sg.Combo(mnt_list, key='-NTP_MONUT-', size=comb_size)],
                [sg.Text('User:', size=text_size), sg.Input(key='-NTP_USER-', size=(16, 1))],
                [sg.Text('Pwd:', size=text_size), sg.Input(key='-NTP_PASSWD-', size=(16, 1))],
                [sg.RButton('Source', size=(10, 1), key='-NTP_SOURCE-'),
                 sg.RButton('Connect', size=(10, 1), key='-NTP_CONNECT-')]]

at_layout = [ [sg.RButton('Send', size=(10, 1)), sg.Combo(atcmd_list, key='-AT_SEND-', size=comb_size)],
                [sg.RButton('File', size=(10, 1)), sg.Input(key='-AT_FILE-', size=comb_size)],
                [sg.RButton('Trans', size=(10, 1), key='-AT_TRANS-')]]

send_configure = [[sg.InputText('', key='input', size=(41, 1)), sg.Checkbox('自动换行', default=True), sg.RButton('发送')]]

layout = [[sg.Multiline('', key='message', size=(29, 5)), [sg.Frame('Serial', serial_layout), sg.Frame('Ntrip', ntrip_layout)]],
          [sg.Frame('发送区', send_configure)]
          ]

if __name__ == '__main__':
    window = sg.Window('FMI Trident').layout(layout)
    while True:
        event, values = window.Read()
        if event in (None, 'Cancel'):
            break
        elif event == 'Connect':
            print(f"Button Connect pressed!")
        else:
            print(f"event {event}, values {values}")

    window.close()
