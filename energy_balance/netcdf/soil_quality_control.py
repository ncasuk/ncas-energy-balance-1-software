__author__ = 'Elle Smith'
__date__ = '09 Aug 2021'
__contact__ = 'eleanor.smith@stfc.ac.uk'

import numpy as np
import pandas as pd
import os
import glob

from .quality_control import QualityControl

from energy_balance import CONFIG

class SoilQualityControl(QualityControl):

    soil_moisture_headers = CONFIG['soil']['soil_moisture_headers']
    soil_temperature_headers = CONFIG['soil']['soil_temperature_headers']
    soil_heat_flux_headers = CONFIG['soil']['soil_heat_flux_headers']
    headers = soil_moisture_headers + soil_temperature_headers + soil_heat_flux_headers

    def create_dataframes(self):
        date = self.prepare_date(CONFIG['soil']['input_date_format'])
        input_file_path = CONFIG['soil']['input_file_path']
        
        soil_moisture_file = CONFIG['soil']['soil_moisture_file']
        soil_temperature_file = CONFIG['soil']['soil_temperature_file']
        soil_heat_flux_file = CONFIG['soil']['soil_heat_flux_file']

        try:
            df_soilmoisture = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(input_file_path, soil_moisture_file.format(date=date)))],ignore_index=True)
            df_soiltemp= pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(input_file_path, soil_temperature_file.format(date=date)))],ignore_index=True)
            df_soilheatflux = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(input_file_path, soil_heat_flux_file.format(date=date)))],ignore_index=True)
        except ValueError:
            print(f"No files found for {date}, skipping")
            raise FileNotFoundError

        # all data needed is selected using column headers
        self._df = df_soilmoisture[[self.dt_header] + self.soil_moisture_headers].merge(df_soiltemp[[self.dt_header] + self.soil_temperature_headers], on=self.dt_header).merge(df_soilheatflux[[self.dt_header] + self.soil_heat_flux_headers], on=self.dt_header)

        # np.select(conditions, choices, default='1')
        self._qc = pd.DataFrame(columns = [h+ '_qc' for h in self.headers])

    def qc_variables(self):
        # soil temperature
        for col in self.soil_temperature_headers:
            temp_conditions = [np.isnan(self._df[col]), self._df[col] < -35, self._df[col] > 50, self._df[col] < 18, self._df[col] > 25]
            temp_choices = [2, 2, 2, 3, 3]
            self.apply_qc(temp_conditions, temp_choices, col)

        # soil heat flux
        for col in self.soil_heat_flux_headers:
            shf_conditions = [np.isnan(self._df[col]), self._df[col] < -30, self._df[col] > 70]
            shf_choices = [2, 2, 2]
            self.apply_qc(shf_conditions, shf_choices, col)

        # soil water potential
        for col in self.soil_moisture_headers:
            swp_conditions = [np.isnan(self._df[col]), self._df[col] > 80, self._df[col] > 200, self._df[col] < 0]
            swp_choices = [2, 2, 3, 3]
            self.apply_qc(swp_conditions, swp_choices, col)