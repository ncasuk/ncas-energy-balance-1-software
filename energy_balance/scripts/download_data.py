#!/usr/bin/env python

__author__ = 'Elle Smith'
__date__ = '15 Jul 2021'
__contact__ = 'eleanor.smith@stfc.ac.uk'


import os
import subprocess
import pandas as pd
import ntplib
import argparse
from datetime import datetime, date
from pycampbellcr1000 import CR1000
from energy_balance import CONFIG


def arg_parse():
    
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-t",
        "--set-time",
        action="store_true",
        help=f"If set then the logger time will be updated when the script runs at midnight. If not specified, set_time=False."
    )
                        
    return parser.parse_args()


def log(url, dir_path, set_time=False):
    """
    Extract the data from the campbell data logger for each specified table and save to a daily csv file.
    This will backfill the file to get all data from the start of the day or update from the latest data entry if data already exists in the file.
    Default tables are: Housekeeping, GPS_datetime, SoilTemperature, SoilMoisture, SoilHeatFlux and Radiation
    If set_time=True the logger time will be updated when the script runs at midnight. Default is False.
    
    :param url: (str) URL for connection with logger in format 'tcp:iphost:port' or 'serial:/dev/ttyUSB0:19200:8N1'
    :param dir_path: (str) The path to the top level directory in which to create the csv files and folders.
    :param set_time: (boolean) If True, the logger time will be updated when the script runs at midnight. Default is False.
    :returns: None
    """
    device = CR1000.from_url(url)

    # first check if it's midnight (utc) & sync time, if set_time=True
    if set_time:
        try:
            c = ntplib.NTPClient()
            start_time = datetime.utcfromtimestamp(c.request('pool.ntp.org').tx_time)

            if start_time.hour == "0" and start_time.minute == "0":
                device.set_time(datetime.utcfromtimestamp(c.request('pool.ntp.org').tx_time))
                
        except:
            print("Could not sync with time server.")

    # device.list_tables():
    # ['Status', 'Housekeeping', 'GPS_datetime', 'SoilTemperature', 'SoilMoisture', 'SoilHeatFlux', 'Radiation', 'DataTableInfo', 'Public']
    tables = CONFIG['common']['logger_tables']
    date = datetime.utcnow().strftime("%Y-%m-%d")

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
    today = datetime.utcnow().date()
    midnight = datetime.combine(today, datetime.min.time())
    start_time = midnight.strftime("%Y-%m-%d %H:%M")

    cmd = f"pycr1000 getdata {url} {table} --start '{start_time}' {csv_path}"
    subprocess.call(cmd, shell=True)


def main():
    args = arg_parse()
    set_time = args.set_time

    url = CONFIG['common']['logger_url']
    dir_path = os.path.expanduser(CONFIG['common']['logger_csv_path'])

    log(url, dir_path, set_time)

if __name__ == '__main__':
    main()