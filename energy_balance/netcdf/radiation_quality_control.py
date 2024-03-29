__author__ = 'Elle Smith'
__date__ = '09 Aug 2021'
__contact__ = 'eleanor.smith@stfc.ac.uk'

import numpy as np
import pandas as pd
import os
import glob

from .quality_control import QualityControl

from energy_balance import CONFIG

class RadiationQualityControl(QualityControl):

    lwdn_header = CONFIG['radiation']['lwdn_header']
    lwup_header = CONFIG['radiation']['lwup_header']
    swdn_header = CONFIG['radiation']['swdn_header']
    swup_header = CONFIG['radiation']['swup_header']
    body_temp_header = CONFIG['radiation']['body_temp_header']

    def __init__(self, date, frequency):
        self.headers = [self.lwdn_header, self.lwup_header, self.swdn_header, self.swup_header]
        if not self.body_temp_header == 'null':
            self.headers.append(self.body_temp_header)
        super().__init__(date, frequency)

    def create_dataframes(self):
        """
        RadiationQualityControl specific implementation to create pandas dataframe from input csvs and empty QC dataframe other than column names.
        Sets self._df and self._qc
        """
        date = self.prepare_date(CONFIG['radiation']['input_date_format'])
        input_file_path = CONFIG['radiation']['input_file_path']
        
        radiation_file = CONFIG['radiation']['radiation_file']

        full_input_glob = os.path.expanduser(os.path.join(input_file_path, radiation_file.format(date=date)))
        try:
            df_radiation = pd.concat([pd.read_csv(f) for f in glob.glob(full_input_glob)],ignore_index=True)
        except ValueError:
            print(f"No files found for {date} in {full_input_glob}, skipping")
            raise FileNotFoundError

        # all data needed is selected using column headers
        self._df = df_radiation[[self.dt_header] + self.headers]

        # np.select(conditions, choices, default='1')
        self._qc = pd.DataFrame(columns = [h+ '_qc' for h in self.headers])

    def qc_variables(self):
        """
        RadiationQualityControl specific implementation to set QC conditions and flags and record in QC dataframe.
        """
        # downwelling longwave
        lwdn_conditions = [np.isnan(self._df[self.lwdn_header]), self._df[self.lwdn_header] < 0, self._df[self.lwdn_header] > 1000]
        lwdn_choices = [2, 3, 4]
        self.apply_qc(lwdn_conditions, lwdn_choices, self.lwdn_header)

        # upwelling longwave
        lwup_conditions = [np.isnan(self._df[self.lwup_header]), self._df[self.lwup_header] < 0, self._df[self.lwup_header] > 1000]
        lwup_choices = [2, 3, 4]
        self.apply_qc(lwup_conditions, lwup_choices, self.lwup_header)

        # downwelling shortwave
        swdn_conditions = [np.isnan(self._df[self.swdn_header]), self._df[self.swdn_header] < 0, self._df[self.swdn_header] > 2000]
        swdn_choices = [2, 3, 4]
        self.apply_qc(swdn_conditions, swdn_choices, self.swdn_header)

        # upwelling shortwave
        swup_conditions = [np.isnan(self._df[self.swup_header]), self._df[self.swup_header] < 0, self._df[self.swup_header] > 2000]
        swup_choices = [2, 3, 4]
        self.apply_qc(swup_conditions, swup_choices, self.swup_header)

        # body temperature
        if not self.body_temp_header == 'null':
            body_temp_conditions = [np.isnan(self._df[self.body_temp_header]), self._df[self.body_temp_header] < -233.15, self._df[self.body_temp_header] > 353.15]
            body_temp_choices = [2, 2, 2]
            self.apply_qc(lwdn_conditions, lwdn_choices, self.body_temp_header)

        # sensor cleaning
        # create using datetime column
        self._df['timestamp'] = pd.to_datetime((self._df[self.dt_header]))

        cleaning_time_lower = CONFIG['radiation']['cleaning_time_lower']
        cleaning_time_upper = CONFIG['radiation']['cleaning_time_upper']

        cleaning_conditions = [self._df['timestamp'].dt.strftime('%H:%M:%S').between(cleaning_time_lower,cleaning_time_upper)]
        # cleaning_conditions = [self._df[self._df[self.dt_header].dt.time < cleaning_time_upper]]
        cleaning_choices = [2]
        self.apply_qc(cleaning_conditions, cleaning_choices, 'cleaning')

    def apply_cleaning_and_temp_masks(self):
        """
        Apply cleaning QC and body temperature QC to all columns in the dataframe.
        """
        # apply cleaning mask to all variables
        for col in self.headers:
            mask_column = self.mask['cleaning_qc']
            self._df_masked[col] = self._df_masked[col][mask_column]

        # apply temp mask to all variables
        if not self.body_temp_header == 'null':
            for col in self.headers:
                mask_column = self.mask[self.body_temp_header+'_qc']
                self._df_masked[col] = self._df_masked[col][mask_column]

    def create_masked_df(self, qc_flag):
        """
        RadiationQualityControl specific implementation to create the masked dataframe.
        """
        super().create_masked_df(qc_flag)
        self.apply_cleaning_and_temp_masks()
