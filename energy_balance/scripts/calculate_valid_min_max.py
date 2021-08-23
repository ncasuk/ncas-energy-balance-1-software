#!/usr/bin/env python

__author__ = 'Elle Smith'
__date__ = '23 Aug 2021'
__contact__ = 'eleanor.smith@stfc.ac.uk'

import pandas as pd
from netCDF4 import Dataset
import argparse
import os
import numpy as np
from energy_balance import CONFIG

def arg_parse():
    parser = argparse.ArgumentParser()

    parser.add_argument('-v', '--var-name',
                        type=str,
                        required=True,
                        help="The name of the variable to update the min/max on. e.g. 'soil_temperature'")

    parser.add_argument('-qc', '--qc-var-name',
                        type=str,
                        required=True,
                        help="The name of the quality control variable to use as a mask for retrieving valid values. e.g. 'qc_flag_soil_temperature'")

    parser.add_argument('-fp', '--file-path',
                        type=str,
                        required=True,
                        help="The path to netCDF file on which to recalculate the min/max e.g. /path/to/my/file.nc")

    return parser.parse_args()


def calculate_valid_min_max(fpath, var_name, qc_var_name, qc_value):
    """
    Re calculate valid min and valid max for a variable, given the quality control variable and maximum desired quality control value.
    Useful after quality control variable has been changed manually. 

    :param fpath: (str) Path to netCDF file on which to calculate the min/max
    :param var_name: (str) The name of the variable to update the min/max on.
    :param qc_var_name: (str) The name of the quality control variable to use as a mask for retrieving valid values.
    :param qc_value: (int) Max value of qc to use i.e. 1 will calculate min/max on only 'good data', 2 will calculate it on good data and data marked with a flag of 2.
    """
    dataset = Dataset(fpath, 'r+')

    var = dataset[var_name]
    qc_var = dataset[qc_var_name]

    data = pd.DataFrame(var[:])
    qc = pd.DataFrame(qc_var[:])

    mask = (qc <= qc_value) 
    data_masked = data[mask]

    var.valid_min = np.nanmin(data_masked)
    var.valid_max = np.nanmax(data_masked)

    dataset.close()


def main():
    args = arg_parse()

    fpath = os.path.expanduser(args.file_path)
    var_name = args.var_name
    qc_var_name = args.qc_var_name

    qc_value = CONFIG['common']['qc_flag_level']

    calculate_valid_min_max(fpath, var_name, qc_var_name, qc_value)
    print(f"Recalculated valid min and valid max for {var_name}, using {qc_var_name} as a mask, with qc flag value of {qc_value}.")

if __name__ == '__main__':
    main()