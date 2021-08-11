__author__ = 'Elle Smith'
__date__ = '09 Aug 2021'
__contact__ = 'eleanor.smith@stfc.ac.uk'

import numpy as np
from .base_netcdf import BaseNetCDF

from energy_balance import CONFIG

class RadiationNetCDF(BaseNetCDF):

    lwdn_header = CONFIG['radiation']['lwdn_header']
    lwup_header = CONFIG['radiation']['lwup_header']
    swdn_header = CONFIG['radiation']['swdn_header']
    swup_header = CONFIG['radiation']['swup_header']
    body_temp_header = CONFIG['radiation']['body_temp_header']
    headers = [lwdn_header, lwup_header, swdn_header, swup_header, body_temp_header]

    data_product = 'radiation'

    def create_specific_dimensions(self):
        # no extra dimensions to create
        pass

    def apply_cleaning_and_temp_masks(self):
        # apply cleaning mask to all variables
        for col in self.headers:
            mask_column = self.mask['cleaning_qc']
            self.df_masked[col] = self.df[col][mask_column]

        # apply temp mask to all variables
        for col in self.headers:
            mask_column = self.mask[self.body_temp_header+'_qc']
            self.df_masked[col] = self.df[col][mask_column]

    def create_radiation_variables(self):
        # set common parameters
        dims = ('time',)
        data_type = np.float32
        attrs = {"cell_methods": "time:mean",
                 "coordinates": "latitude longitude",
                 "units": "W m-2"}
        
        # lwdn
        lwdn_attrs = {"standard_name": "downwelling_longwave_flux_in_air",
                      "long_name": "Downwelling Longwave Radiation in air"}
        self.create_variable("downwelling_longwave_flux_in_air", data_type, dims, self.lwdn_header, **{**attrs, **lwdn_attrs})

        # lwup
        lwup_attrs = {"standard_name": "upwelling_longwave_flux_in_air",
                      "long_name": "Upwelling Longwave Radiation in air"}
        self.create_variable("upwelling_longwave_flux_in_air", data_type, dims, self.lwup_header, **{**attrs, **lwup_attrs})

        # swdn
        swdn_attrs = {"standard_name": "downwelling_shortwave_flux_in_air",
                      "long_name": "Downwelling Shortwave Radiation in air"}
        self.create_variable("downwelling_shortwave_flux_in_air", data_type, dims, self.swdn_header, **{**attrs, **swdn_attrs})

        # swup
        swup_attrs = {"standard_name": "upwelling_shortwave_flux_in_air",
                      "long_name": "Upwelling Shortwave Radiation in air"}
        self.create_variable("upwelling_shortwave_flux_in_air", data_type, dims, self.swup_header, **{**attrs, **swup_attrs})


    def create_specific_variables(self):
        # create variables
        self.apply_cleaning_and_temp_masks()
        self.create_radiation_variables()

        # create body temperature variable
        temp_attrs = {"units": "K",
                      "long_name": "Radiometer Body Temperature",
                      "cell_methods": "time:mean",
                      "coordinates": "latitude longitude",}
        self.create_variable("radiometer_body_temperature", np.float32, ("time",), self.body_temp_header, **temp_attrs)

        # create qc variables
        # swdn
        attrs = {"long_name": "Data Quality flag: dwonwelling shortwave",
                 "flag_values": "0b,1b,2b,3b,4b,5b,6b",
                 "flag_meanings": "0: not_used \n1: good data \n2: no_data \n3: bad_data_sw_radiation_<_0 \n4: bad_data_sw_radiation_>_2000_W_m-2 \n5: suspect_data \n6: timestamp_error"}
        self.create_qc_variable("qc_flag_downwelling_shortwave", self.swdn_header, ('time',), **attrs)

        # swup
        attrs = {"long_name": "Data Quality flag: upwelling shortwave",
                 "flag_values": "0b,1b,2b,3b,4b,5b,6b",
                 "flag_meanings": "0: not_used \n1: good data \n2: no_data \n3: bad_data_sw_radiation_<_0 \n4: bad_data_sw_radiation_>_2000_W_m-2 \n5: suspect_data \n6: timestamp_error"}
        self.create_qc_variable("qc_flag_upwelling_shortwave", self.swup_header, ('time',), **attrs)
        
        # lwdn
        attrs = {"long_name": "Data Quality flag: downwelling longwave",
                 "flag_values": "0b,1b,2b,3b,4b,5b,6b",
                 "flag_meanings": "0: not_used \n1: good data \n2: no_data \n3: bad_data_lw_radiation_<_0 \n4: bad_data_lw_radiation_>_1000_W_m-2 \n5: suspect_data \n6: timestamp_error"}
        self.create_qc_variable("qc_flag_downwelling_longwave", self.lwdn_header, ('time',), **attrs)

        # lwup
        attrs = {"long_name": "Data Quality flag: upwelling longwave",
                 "flag_values": "0b,1b,2b,3b,4b,5b,6b",
                 "flag_meanings": "0: not_used \n1: good data \n2: no_data \n3: bad_data_lw_radiation_<_0 \n4: bad_data_lw_radiation_>_1000_W_m-2 \n5: suspect_data \n6: timestamp_error"}
        self.create_qc_variable("qc_flag_upwelling_longwave", self.lwup_header, ('time',), **attrs)

        # body temp
        attrs = {"long_name": "Data Quality flag: Body Temperature",
                 "flag_values": "0b,1b,2b,3b,4b",
                 "flag_meanings": "0: not_used \n1: good data \n2: bad_data_body_temperature_outside_operational_range_-40_to_80C \n3: suspect_data \n4: timestamp_error"}
        self.create_qc_variable("qc_flag_body_temperature", self.body_temp_header, ('time',), **attrs)

        # cleaning
        attrs = {"long_name": "Data Quality flag: sensor cleaning",
                 "flag_values": "0b,1b,2b,3b,4b",
                 "flag_meanings": "0: not_used \n1: good data \n2: bad_data_sensor_being_cleaned \n3: suspect_data \n4: timestamp_error"}
        self.create_qc_variable("qc_flag_cleaning", "cleaning", ('time',), **attrs)