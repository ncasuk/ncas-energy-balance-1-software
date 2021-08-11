#!/usr/bin/env python

__author__ = 'Elle Smith'
__date__ = '11 Aug 2021'
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