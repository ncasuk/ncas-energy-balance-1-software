#!/usr/bin/env python

__author__ = 'Elle Smith'
__date__ = '12 Aug 2021'
__contact__ = 'eleanor.smith@stfc.ac.uk'

import pandas as pd
import argparse
import matplotlib.pyplot as plt
from datetime import datetime
from energy_balance import CONFIG

def arg_parse():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--start',
                        type=str,
                        required=False,
                        help="The start date/time for the plot in 'YYYY-MM-dd HH:MM:SS' format. e.g. '2021-07-10 04:00'.")

    parser.add_argument('-e', '--end',
                        type=str,
                        required=False,
                        help="The end date/time for the plot in 'YYYY-MM-dd HH:MM:SS' format. e.g. '2021-07-10 16:00'.")

    parser.add_argument('-f', '--file',
                        type=str,
                        required=True,
                        help="The path to the csv file to plot.")

    parser.add_argument('-c', '--columns',
                        type=str,
                        required=True,
                        help="The columns from the csv to plot against datetime, provide as comma separated list if more than one e.g. 'IR01Dn,IR01Up'.")

    return parser.parse_args()


def plot(start, end, columns, fpath):
    dt_header = CONFIG['common']['datetime_header']
    df = pd.read_csv(fpath)

    if not start:
        start = df[dt_header][0]
    
    if not end:
        end = df[dt_header].iloc[-1]
    
    df['TIMESTAMP'] = pd.to_datetime((df[dt_header]))
    df = df[(df['TIMESTAMP'] > start) & (df['TIMESTAMP'] < end)]
    
    df.plot(x="TIMESTAMP", y=columns)
    plt.show()


def validate_time(time):
    try:
        datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        return time
    except ValueError:
        raise ValueError(f"Time {time} not in correct format: %Y-%m-%d %H:%M:%S")

def main():
    args = arg_parse()

    start = args.start
    end = args.end

    if start:
        start = validate_time(start)
    
    if end:
        end = validate_time(end)

    fpath = args.file
    columns = args.columns.strip(' ').split(',')

    plot(start, end, columns, fpath)


if __name__ == '__main__':
    main()
