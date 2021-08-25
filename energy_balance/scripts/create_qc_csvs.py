#!/usr/bin/env python

__author__ = 'Elle Smith'
__date__ = '11 Aug 2021'
__contact__ = 'eleanor.smith@stfc.ac.uk'

import argparse
import os
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from energy_balance import CONFIG
from energy_balance.netcdf.soil_netcdf import SoilNetCDF
from energy_balance.netcdf.soil_quality_control import SoilQualityControl
from energy_balance.netcdf.radiation_netcdf import RadiationNetCDF
from energy_balance.netcdf.radiation_quality_control import RadiationQualityControl

def arg_parse():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--start-date',
                        type=str,
                        required=True,
                        help="The start date to create files for. e.g. '2021-07-30' when creating daily files, '2021-07' when creating monthly files.")

    parser.add_argument('-e', '--end-date',
                        type=str,
                        required=False,
                        help="The end date to create files for. e.g. '2021-07-30' when creating daily files, '2021-07' when creating monthly files. This is incllusive.")
    
    parser.add_argument('-f', '--frequency',
                        type=str,
                        required=True,
                        default='monthly',
                        choices=['daily', 'monthly'],
                        help="The frequency for creating the csv files, options are daily or monthly.")

    parser.add_argument('-d', '--data-product',
                        type=str,
                        required=True,
                        choices=['soil', 'radiation'],
                        help="The data product to create files for.")
    
    return parser.parse_args()

def create_soil_files(date, frequency, path):
    """
    Create soil masked csv.
    
    :param date: (datetime.datetime) The date for which to create the file. 
    :param frequency: (str) The frequency for files - daily or monthly.
    :returns: None
    """
    sqc = SoilQualityControl(date, frequency)
    sqc.create_masked_csv(path)

def create_radiation_files(date, frequency, path):
    """
    Create radiation masked csv.
    
    :param date: (datetime.datetime) The date for which to create the file.
    :param frequency: (str) The frequency for files - daily or monthly.
    :returns: None
    """
    rqc = RadiationQualityControl(date, frequency)
    rqc.create_masked_csv(path)

def get_create_file(data_product):
    """Get the function for creating files for the specified data product."""
    if data_product == "radiation":
        return create_radiation_files
    elif data_product == "soil":
        return create_soil_files

def prepare_date(date, frequency):
    """
    Convert datetimes to strings, dependening on frequency.
    If monthly: format returned will be %Y%m
    If daily: format returned will be %Y%m%d

    :param date: (datetime.datetime) The date for which the file is being created.
    :param frequency: (str) The frequency for files - daily or monthly.
    :returns: (str) The date converted to string format.
    """
    if frequency == "monthly":
        date = date.strftime("%Y%m")
    else:
        date = date.strftime("%Y%m%d")

    return date
    
def create_files(start_date, end_date, frequency, data_product, fpath):
    """
    Create masked csvs for the specified data product in the time range provided.
    
    :param start_date: (datetime.datetime) The start date for which to create the files.
    :param end_date: (datetime.datetime) The end date for which to create the files.
    :param frequency: (str) The frequency for files - daily or monthly.
    :param data_product: (str) The data product to create the csvs for e.g. radiation or soil
    :param fpath: (str) The directory path at which to create the output file.
    :returns: None
    """
    while start_date <= end_date:

        date = prepare_date(start_date, frequency)
        fname = f"{data_product}_qc_{date}.csv"
        path = os.path.join(fpath, fname)

        if frequency == 'daily':
            delta = relativedelta(days=1)
        else:
            delta = relativedelta(months=1)

        try:
            func = get_create_file(data_product)
            func(start_date, frequency, path)
        except FileNotFoundError:
            start_date += delta
            continue
    
        start_date += delta


def main():
    args = arg_parse()

    freq = args.frequency

    if freq == 'daily':
        date_format = "%Y-%m-%d"
    else:
        date_format = "%Y-%m"
    
    try:
        start_date = datetime.strptime(args.start_date, date_format)
    except ValueError:
        raise ValueError("Dates must be in a format matching the frequency: Y-m-d for daily, Y-m for monthly.")

    # if no end date, make it the same as the start date, then file will be created 
    if args.end_date:
        end_date = datetime.strptime(args.end_date, date_format)
        complete_stmnt = f'Files created for {args.start_date} {args.end_date}'
    else:
        end_date = start_date
        complete_stmnt = f'File created for {args.start_date}'

    data_product = args.data_product
    fpath = os.path.expanduser(CONFIG['common']['qc_csv_path'])

    create_files(start_date, end_date, freq, data_product, fpath)
    print(complete_stmnt)

if __name__ == '__main__':
    main()
