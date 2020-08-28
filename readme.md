# Trident v1.5 

A FMI ntrip serial tool for miscellaneous board testing

## Serial

- "Port" combo box will list current com port connected to the host, select or input proper 
serial parameters then "Open" the serial port.
- all messages serial port received will show up in the left blank text display area.

- 串口连接
    1. "Refresh"刷新按钮将列举当前主机所有串口号，串口配置参数设置完成后点击"Connect"
    按钮连接串口
        > 暂不支持VSPD虚拟串口识别，用户需手动输入虚拟串口配置信息
    2. 串口接收到的数据在左侧显示栏显示
        > 显示栏数据默认自动向下滚动，暂不支持在串口连接状态下数据选择操作
    3. 

## Ntrip Caster

- fill ntrip parameters press "Connect" button, all valid mount point will list in "Mount" combo box
- input user id and password press "Connect" button again to get cors data  

## AT command

- danger zone !

## Extools

- currently only support convert NMEA to KML 

## States

- board info display

pyuic5 -o mainwindow.py mainwindow.ui 
