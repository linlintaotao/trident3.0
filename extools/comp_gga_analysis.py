#!-*-coding:utf-8 -*-
"""
@desp: A simple python script to plot neu error, horizontal error and horizontal CDF figure of NMEA data
@file: comp_gga_analysis.py
@date: 8/26/2019
@author: Chey
"""

from numpy import sqrt, cos, nan
from pandas import merge, read_table, offsets
from datetime import datetime, timedelta

#######################################################
radius = 6371000
d2r = 0.017453292519943295

#######################################################


def format_time(date):
    ''' round off datetime microseconds '''
    t = datetime.strptime(date, "%H%M%S.%f")
    if t.microsecond % 1000 >= 500:  # check if there will be rounding up
        t = t + timedelta(milliseconds=1)  # manually round up
        t = t.replace(microsecond=0)
    else:
        t = t.replace(microsecond=0)
    return t


def nmeatime(date):
    ''' return NMEA time format '''
    micro = date.split('.')
    if int(micro[1]) >= 50:  # return round of .time
        date += '9999'
    return format_time(date)


def ratio_info(df, type=5):
    '''get float solution ratio'''
    total_cnt = df.size
    if total_cnt <= 0:
        print(f"data frame zero count")
        return None

    sd_cnt, float_cnt, fix_cnt = 0, 0, 0
    for index, element in df.iteritems():
        row = int(element)
        if row == 2 or row == 1 or row == 0:
            df.at[index] = nan
            sd_cnt += 1
        elif row == 5:
            float_cnt += 1
        elif row == 4:
            fix_cnt += 1
        else:
            pass
    return (float_cnt + fix_cnt) / total_cnt, sd_cnt / total_cnt, fix_cnt, float_cnt, sd_cnt, total_cnt


def genComp(gt_file, gga_file, ymd):
    # data list to hold [tgga.txt mgga.txt xgga.txt zgga.txt]
    # float ratio list to hold each measurements float ratio
    data_list = []
    float_ratio = tuple()

    for file in (gt_file, gga_file):
        data = read_table(file, sep=',', header=None, index_col=1, parse_dates=True, date_parser=nmeatime, comment='*',
                          usecols=[0, 1, 2, 3, 4, 5, 6, 9])

        # rename each column
        data.rename(columns={1: 'UTC Time', 2: 'Lat', 3: 'NorS', 4: 'Lon', 5: 'EorW', 6: 'Fix', 9: 'Alt'}, inplace=True)
        data['Fix'] = data['Fix'].astype(float)
        float_ratio = ratio_info(data['Fix'])

        # convert DDMM.MMMM to DD.dddd
        data['LatDD'] = (data.Lat / 100).fillna(0).astype(int)
        data['LatDD'] = data.LatDD + (data.Lat - 100.0 * data.LatDD) / 60.0
        data['LonDD'] = (data.Lon / 100).fillna(0).astype(int)
        data['LonDD'] = data.LonDD + (data.Lon - 100.0 * data.LonDD) / 60.0
        data_list.append(data)

    # merge drop re-calc index time
    dts_n_diff, dts_e_diff, dts_u_diff, hz_diff = [], [], [], []

    dt = merge(data_list[0], data_list[1], left_index=True, right_index=True, how='outer')
    dt = dt.dropna()
    dt.index.names = ['UTC Time']
    dt.index = dt.index.map(lambda t: t.replace(year=ymd[0], month=ymd[1], day=ymd[2])) + offsets.Hour(8)
    dt_n_diff = (dt['LatDD_y'] - dt['LatDD_x']) * d2r * radius
    dt_e_diff = (dt['LonDD_y'] - dt['LonDD_x']) * d2r * radius * cos(dt['LatDD_x'] * d2r)
    dt_u_diff = dt['Alt_y'] - dt['Alt_x']

    dts_n_diff.append(dt_n_diff)
    dts_e_diff.append(dt_e_diff)
    dts_u_diff.append(dt_u_diff)

    # calc horizontal differential
    hz_diff.append(sqrt(dt_n_diff[:] ** 2 + dt_e_diff[:] ** 2))

    # dts_total_diff list in [n, n, ..., n, e, e, ..., e, u, u, ..., u]
    dts_total_diff = dts_n_diff + dts_e_diff + dts_u_diff

    return dts_total_diff, hz_diff, float_ratio


if __name__ == '__main__':
    pass
