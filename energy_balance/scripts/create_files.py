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
                        help="The end date to create netCDF files for. e.g. '2021-07-30' when creating daily files, '2021-07' when creating monthly files.")

    parser.add_argument('-f', '--frequency',
                        type=str,
                        required=False,
                        default='monthly',
                        choices=['daily', 'monthly'],
                        help="The frequency for creating the netCDF files, options are daily or monthly. The default is monthly.")

    parser.add_argument('-d', '--data-product',
                        type=str,
                        required=False,
                        choices=['soil', 'radiation'],
                        help="The data prodcut to create files for. If not provided files will be created for soil and radiation.")

    return parser.parse_args()

def create_soil_files(start_date, frequency):
    sqc = SoilQualityControl(start_date, frequency)
    SoilNetCDF(sqc.df, sqc.qc, start_date)

def create_radiation_files(start_date, frequency):
    rqc = RadiationQualityControl(start_date, frequency)
    RadiationNetCDF(rqc.df, rqc.qc, start_date)

def get_create_file(data_product):
    if data_product == "radiation":
        return create_radiation_files
    elif data_product == "soil":
        return create_soil_files
    
def create_files(start_date, end_date, frequency, data_product=None):
    # this creates a file per day
    while start_date <= end_date:

        if frequency == 'daily':
            delta = relativedelta(days=1)
        else:
            delta = relativedelta(months=1)

        if data_product:
            try:
                func = get_create_file(data_product)
                func(start_date, frequency)
            except FileNotFoundError:
                start_date += delta
                continue

        else:
            # soil
            try:
                create_soil_files(start_date, frequency)
            except FileNotFoundError:
                pass
            
            # radiation
            try:
                create_radiation_files(start_date, frequency)
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
