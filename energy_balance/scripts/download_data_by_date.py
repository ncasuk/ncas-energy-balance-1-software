#!/usr/bin/env python

__author__ = 'Elle Smith'
__date__ = '23 Jul 2021'
__contact__ = 'eleanor.smith@stfc.ac.uk'


import argparse
import os
import pandas as pd
from datetime import datetime, timedelta
from pycampbellcr1000 import CR1000


def arg_parse():
    parser = argparse.ArgumentParser()

    parser.add_argument('url', action="store",
                        help="Specify URL for connection link. "
                        "E.g. tcp:iphost:port or serial:/dev/ttyUSB0:19200:8N1"
                        " or serial:/COM1:19200:8N1")

    parser.add_argument('-s', '--start-date',
                        type=str,
                        required=True,
                        help="The start date to extract data for")

    parser.add_argument('-e', '--end-date',
                        type=str,
                        required=False,
                        help="The end date to extract data for")

    parser.add_argument("-f",
                        "--file-path",
                        type=str,
                        required=True,
                        help="Path to directory in which to write the csv files.")

    return parser.parse_args()


def get_data(url, start_date, end_date, dir_path):
    """
    Extract data from the campbell data logger for each specified table and save to a daily csv file between the date ranges specified.
    Default tables are: Housekeeping, GPS_datetime, SoilTemperature, SoilMoisture, SoilHeatFlux and Radiation
    
    :param url: (str) URL for connection with logger in format 'tcp:iphost:port' or 'serial:/dev/ttyUSB0:19200:8N1'
    :param start_date: (datetime.datetime) The start date from which to collect data
    :param end_date: (datetime.datetime) The end date after which to stop collecting data. (the end date will be included in the data.) 
    :param dir_path: (str) The path to the top level directory in which to create the csv files and folders.
    :returns: None
    """
    device = CR1000.from_url(url)

    # device.list_tables():
    # ['Status', 'Housekeeping', 'GPS_datetime', 'SoilTemperature', 'SoilMoisture', 'SoilHeatFlux', 'Radiation', 'DataTableInfo', 'Public']
    tables = ['Housekeeping', 'GPS_datetime', 'SoilTemperature', 'SoilMoisture', 'SoilHeatFlux', 'Radiation']

    for table in tables:

        while start_date <= end_date:
            end_of_day = start_date + timedelta(hours=23, minutes=59, seconds=59, microseconds=59)

            csv_dirs = os.path.join(dir_path, table)
            csv_name = f"{table}_{start_date.strftime('%Y-%m-%d')}.csv"
            csv_path = os.path.join(csv_dirs, csv_name)

            # create csv path
            if not os.path.exists(csv_dirs):
                os.makedirs(csv_dirs)

            # if file doesn't exist - make it
            if not os.path.isfile(csv_path):
                open(csv_path, 'w').close()

            # open the csv file
            try:
                df = pd.read_csv(csv_path)
            except pd.errors.EmptyDataError:
                get_data_from_range(device, table, csv_path, start_date, end_of_day, header=True)
                continue

            if df.empty:
                get_data_from_range(device, table, csv_path, start_date, end_of_day, header=False)

            else:
                # if the file already has data in it, it will just update the existing data from latest entry onwards
                # get lastest date before updating - add a microsecond on, so no issues with duplication of record
                latest = datetime.strptime(df['Datetime'].iloc[-1], "%Y-%m-%d %H:%M:%S") + timedelta(microseconds=1)
                get_data_from_range(device, table, csv_path, latest, end_of_day, header=False)

            start_date = start_date + timedelta(1)


def get_data_from_range(device, table, csv_path, start, end, header):
    """ 
    Gets range of data specified by start and end dates and saves to csv at the path specified.

    :param device: (pycampbellcr1000.CR1000 object) URL for connection with logger in format 'tcp:iphost:port' or 'serial:/dev/ttyUSB0:19200:8N1'
    :param table: (str) The name of the table on the logger from which the data is being extracted.
    :param csv_path: (str) The path to the csv file to back fill with todays data.
    :param start: (datetime.datetime) The start datetime from which to collect data
    :param end: (datetime.datetime) The end datetime after which to stop collecting data. (end will be included in the data.) 
    :returns: None
    """
    data = device.get_data(table, start, end)
    content = data.to_csv(header=header)

    with open(csv_path, "a") as f:
        f.write(content)


def main():
    args = arg_parse()
    url = args.url
    dir_path = args.file_path
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d")

    # if no end date, make it the same as the start date, then data will be downloaded for one day only
    if args.end_date:
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
    else:
        end_date = start_date

    get_data(url, start_date, end_date, dir_path)

if __name__ == '__main__':
    main()
