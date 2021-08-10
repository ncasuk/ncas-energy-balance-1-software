__author__ = 'Elle Smith'
__date__ = '09 Aug 2021'
__contact__ = 'eleanor.smith@stfc.ac.uk'

import pandas as pd
import numpy as np
import xarray as xr
import os
from datetime import datetime
from energy_balance import CONFIG

# make this more general

class QualityControl:

    dt_header = CONFIG['common']['datetime_header']
    headers = 'UNDEFINED'
    qc_flag_level = CONFIG['common']['qc_flag_level']

    def __init__(self, date, frequency):
        self.date = date
        self.frequency = frequency
        self.execute_qc()

    def validate_date(self, input_date_format):
        
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
        # set self._df and self._qc
        raise NotImplementedError

    def apply_qc(self, conditions, choices, col):
        col_qc = col + '_qc'
        self._qc[col_qc] = np.select(conditions, choices, default=1)

    def qc_variables(self):
        # make use of apply_qc
        raise NotImplementedError

    def create_masked_df(self, qc_flag):
        mask = (self._qc <= qc_flag)

        self._df_masked = pd.DataFrame(columns = self.headers)
        self._df_masked[self.dt_header] = self._df[self.dt_header]

        for col in self.headers:
            mask_column = mask[col+'_qc']
            self._df_masked[col] = self._df[col][mask_column]

    def execute_qc(self):
        self.create_dataframes()
        self.qc_variables()
        self.create_masked_df(self.qc_flag_level)

    def create_masked_csv(self, file_path):
        self._df_masked.to_csv(file_path, index=False)
        self._masked_csv = file_path

    @property
    def df(self):
        return self._df

    @property
    def df_masked(self):
        return self._df_masked

    @property
    def qc(self):
        return self._qc

