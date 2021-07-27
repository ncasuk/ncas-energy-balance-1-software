#!/usr/bin/env python

__author__ = 'Elle Smith'
__date__ = '15 Jul 2021'
__contact__ = 'eleanor.smith@stfc.ac.uk'


import argparse
import os
import subprocess
import pandas as pd
from datetime import datetime, date
from pycampbellcr1000 import CR1000


def arg_parse():
    parser = argparse.ArgumentParser()

    parser.add_argument('url', action="store",
                        help="Specify URL for connection link. "
                        "E.g. tcp:iphost:port or serial:/dev/ttyUSB0:19200:8N1"
                        " or serial:/COM1:19200:8N1")

    parser.add_argument("-f",
                        "--file-path",
                        type=str,
                        required=True,
                        help="Path to directory in which to write the csv files.")

    return parser.parse_args()


def log(url, dir_path):
    """
    Extract the data from the campbell data logger for each specified table and save to a daily csv file.
    This will backfill the file to get all data from the start of the day or update from the latest data entry if data already exists in the file.
    Default tables are: Housekeeping, GPS_datetime, SoilTemperature, SoilMoisture, SoilHeatFlux and Radiation
    
    :param url: (str) URL for connection with logger in format 'tcp:iphost:port' or 'serial:/dev/ttyUSB0:19200:8N1'
    :param dir_path: (str) The path to the top level directory in which to create the csv files and folders.
    :returns: None
    """
    device = CR1000.from_url(url)

    # device.list_tables():
    # ['Status', 'Housekeeping', 'GPS_datetime', 'SoilTemperature', 'SoilMoisture', 'SoilHeatFlux', 'Radiation', 'DataTableInfo', 'Public']
    tables = ['Housekeeping', 'GPS_datetime', 'SoilTemperature', 'SoilMoisture', 'SoilHeatFlux', 'Radiation']
    date = datetime.now().strftime("%Y-%m-%d")

    for table in tables:

        csv_dirs = os.path.join(dir_path, table)
        csv_name = f"{table}_{date}.csv"
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
            get_todays_data(url, table, csv_path)
            continue

        if df.empty:
            get_todays_data(url, table, csv_path)

        else:
            cmd = f"pycr1000 update {url} {table} {csv_path}"
            subprocess.call(cmd, shell=True)


def get_todays_data(url, table, csv_path):
    """
    Gets all the data for the specified table from the start of the day i.e. 00:00

    :param url: (str) URL for connection with logger in format 'tcp:iphost:port' or 'serial:/dev/ttyUSB0:19200:8N1'
    :param table: (str) The name of the table on the logger from which the data is being extracted.
    :param csv_path: (str) The path to the csv file to back fill with todays data.
    :returns: None
    """
    # check if there is any data - if not, get since start of day (get data command is inclusive)
    # otherwise update command would just get all data
    # create a start time of midnight of todays date so update doesn't back-fill all data
    today = date.today()
    midnight = datetime.combine(today, datetime.min.time())
    start_time = midnight.strftime("%Y-%m-%d %H:%M")

    cmd = f"pycr1000 getdata {url} {table} --start '{start_time}' {csv_path}"
    subprocess.call(cmd, shell=True)


def main():
    args = arg_parse()
    url = args.url
    dir_path = args.file_path

    log(url, dir_path)

if __name__ == '__main__':
    main()