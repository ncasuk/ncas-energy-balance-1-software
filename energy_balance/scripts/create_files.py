#!/usr/bin/env python

__author__ = 'Elle Smith'
__date__ = '09 Aug 2021'
__contact__ = 'eleanor.smith@stfc.ac.uk'

import argparse
import os
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from energy_balance.netcdf.soil_netcdf import SoilNetCDF
from energy_balance.netcdf.soil_quality_control import SoilQualityControl
from energy_balance.netcdf.radiation_netcdf import RadiationNetCDF
from energy_balance.netcdf.radiation_quality_control import RadiationQualityControl

def arg_parse():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--start-date',
                        type=str,
                        required=True,
                        help="The start date to create netCDF files for. e.g. '2021-07-30' when creating daily files, '2021-07' when creating monthly files.")

    parser.add_argument('-e', '--end-date',
                        type=str,
                        required=False,
                        help="The end date to create netCDF files for. e.g. '2021-07-30' when creating daily files, '2021-07' when creating monthly files. This is inclusive.")

    parser.add_argument('-f', '--frequency',
                        type=str,
                        required=False,
                        default='monthly',
                        choices=['daily', 'monthly'],
                        help="The frequency for creating the netCDF files, options are daily or monthly. The default is monthly.")

    parser.add_argument('-d', '--data-product',
                        type=str,
                        required=True,
                        choices=['soil', 'radiation'],
                        help="The data product to create files for.")

    return parser.parse_args()

def create_soil_files(date, frequency):
    """
    Create soil netcdf.
    
    :param date: (datetime.datetime) The date for which to create the file.
    :param frequency: (str) The frequency for files - daily or monthly.
    :returns: None
    """
    sqc = SoilQualityControl(date, frequency)
    SoilNetCDF(sqc.df, sqc.qc, date, frequency)

def create_radiation_files(date, frequency):
    """
    Create radiation netcdf.
    
    :param date: (datetime.datetime) The date for which to create the file.
    :param frequency: (str) The frequency for files - daily or monthly.
    :returns: None
    """
    rqc = RadiationQualityControl(date, frequency)
    RadiationNetCDF(rqc.df, rqc.qc, date, frequency)

def get_create_file(data_product):
    """Get the function for creating files for the specified data product."""
    if data_product == "radiation":
        return create_radiation_files
    elif data_product == "soil":
        return create_soil_files
    
def create_files(start_date, end_date, frequency, data_product=None):
    """
    Create netcdf files for the specified data product in the time range provided.
    If no data product is provided, netcdf files are created for soil and radiation.
    
    :param start_date: (datetime.datetime) The start date for which to create the files.
    :param end_date: (datetime.datetime) The end date for which to create the files.
    :param frequency: (str) The frequency for files - daily or monthly.
    :param data_product: (str) The data product to create the netcdf files for e.g. radiation or soil
    :returns: None
    """
    while start_date <= end_date:

        if frequency == 'daily':
            delta = relativedelta(days=1)
        else:
            delta = relativedelta(months=1)

        try:
            func = get_create_file(data_product)
            func(start_date, frequency)
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
    
    start_date = datetime.strptime(args.start_date, date_format)

    # if no end date, make it the same as the start date, then file will be created 
    if args.end_date:
        end_date = datetime.strptime(args.end_date, date_format)
    else:
        end_date = start_date

    data_product = args.data_product

    create_files(start_date, end_date, freq, data_product)

if __name__ == '__main__':
    main()
