__author__ = 'Elle Smith'
__date__ = '09 Aug 2021'
__contact__ = 'eleanor.smith@stfc.ac.uk'

import pandas as pd
import numpy as np
import os
from datetime import datetime
from energy_balance import CONFIG

# make this more general

class QualityControl:

    """
    Base class used for apply quality control to data in pandas data frames.
    Creates a quality control dataframe and a masked dataframe (the initial data with a quality control mask applied) from input csv files.
    The input files and various options are taken from a config file.

    Constant values are taken from the config file, excluding 'headers' which must be set in each specific implementation.

    :param date: (datetime.datetime) The date to do the QC for. If frequency is monthly, only the year and month will be taken into account.
    :param frequency: (str) 'daily' or 'monthly'. Determines whether one days worth of data, or one months worth is taken from the csv files to create the dataframes.
    """

    dt_header = CONFIG['common']['datetime_header']
    headers = 'UNDEFINED'
    qc_flag_level = CONFIG['common']['qc_flag_level']

    def __init__(self, date, frequency):
        self.date = date
        self.frequency = frequency
        self.execute_qc()

    def prepare_date(self, input_date_format):
        """
        Prepares the input date format so it matches with the frequency requested.

        :param input_date_format: (str) The format in which the date is provided in the input csv files.
        :returns: (str) The date now converted to string format.
        """
        
        if self.frequency == 'monthly' and 'd' in input_date_format:
            # remove day part from input date format
            input_date_format = input_date_format.replace('%d', '').rstrip('-/').lstrip('-/').replace('//', '/').replace('--', '-') + '*'

        elif self.frequency == 'daily':
            if 'd' not in input_date_format:
                raise ValueError(f'Input date format does not specify a day, so daily files can not be created.')

        else:
            raise ValueError(f'Frequency {self.frequency} is not supported. Options are daily or monthly.')

        date = self.date.strftime(input_date_format)
        return date

    def create_dataframes(self):
        """
        Class specific implementation to create pandas dataframe from input csv and empty QC dataframe other than column names.
        Sets self._df and self._qc
        """
        # set self._df and self._qc
        raise NotImplementedError

    def apply_qc(self, conditions, choices, col):
        """
        Generic method to apply QC to a column in a dataframe, new column is created in QC dataframe.

        :param conditions: (list) The conditions at which a QC flag should be applied. e.g. [np.isnan(self._df[col]), self._df[col] < -35, self._df[col] > 50]
        :param choices: (list) The QC flag to be applied, corresponds to conditions. e.g. [2, 2, 2]
        :param col: (str) The name of the column to apply QC to e.g. 'WP_kPa_1'
        """
        col_qc = col + '_qc'
        self._qc[col_qc] = np.select(conditions, choices, default=1)

    def qc_variables(self):
        """
        Class specific implementation to apply QC to all columns.
        """
        # make use of apply_qc
        raise NotImplementedError

    def create_masked_df(self, qc_flag):
        """
        Create masked pandas dataframe based on self._qc and the qc flag requested.
        Sets self._df_masked.

        :param qc_flag: (int) Max value of qc to show i.e. 1 will show only 'good data', 2 will show good data and data marked with a flag of 2.
        """
        self.mask = (self._qc <= qc_flag)

        self._df_masked = pd.DataFrame(columns = [self.dt_header] + self.headers)
        self._df_masked[self.dt_header] = self._df[self.dt_header]

        for col in self.headers:
            mask_column = self.mask[col+'_qc']
            self._df_masked[col] = self._df[col][mask_column]

    def execute_qc(self):
        """
        Create the dataframes, apply the QC and create the masked dataframe.
        """
        self.create_dataframes()
        self.qc_variables()
        self.create_masked_df(self.qc_flag_level)

    def create_masked_csv(self, file_path):
        """
        Create a csv file from the masked dataframe.

        :param file_path: (str) The path at which to create the csv file e.g. /path/to/my/file.csv
        """
        self._df_masked.to_csv(file_path, index=False)
        self._masked_csv = file_path

    @property
    def df(self):
        """ Returns the original dataframe created from the input csv files. All headers set in each class implementaiton of self.headers are included. """
        return self._df

    @property
    def df_masked(self):
        """ Returns the original dataframe masked following QC. """
        return self._df_masked

    @property
    def qc(self):
        """ Returns the QC dataframe created based on conditions and choices set in the qc_variables method. """
        return self._qc

