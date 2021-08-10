__author__ = 'Elle Smith'
__date__ = '09 Aug 2021'
__contact__ = 'eleanor.smith@stfc.ac.uk'

import numpy as np
from energy_balance import CONFIG
from .base_netcdf import BaseNetCDF


class SoilNetCDF(BaseNetCDF):

    soil_moisture_headers = CONFIG['soil']['soil_moisture_headers']
    soil_temperature_headers = CONFIG['soil']['soil_temperature_headers']
    soil_heat_flux_headers = CONFIG['soil']['soil_heat_flux_headers']
    headers = soil_moisture_headers + soil_temperature_headers + soil_heat_flux_headers
    data_product = 'soil'

    @staticmethod
    def convert_temps_to_kelvin(temps):
        temp_values = []
        for temp in temps:
            temp_values.append(temp + 273.15)
        return temp_values

    def create_specific_dimensions(self):
        # create index dimension of length 3
        self.dataset.createDimension("index", CONFIG['soil']['index_length'])

    def create_variable(self, var_name, data_type, dims, values, headers, **kwargs):
        # Create variable
        var = self.dataset.createVariable(var_name, data_type, dims, fill_value=-1e+20)
        var[:] = values

        # mask the data according to the qc
        var_masked = np.transpose(np.array([self.df_masked[headers[0]], self.df_masked[headers[1]], self.df_masked[headers[2]]]))
        
        # Set variable attributes
        var.valid_min = np.nanmin(var_masked) # get from valid values
        var.valid_max = np.nanmax(var_masked)

        for k, v in kwargs.items():
            setattr(var, k, v)

    def create_soil_temp_variable(self):
        # Create the soil temp variable - convert to kelvin
        temps_1 = self.convert_temps_to_kelvin(self.df[self.soil_temperature_headers[0]])
        temps_2 = self.convert_temps_to_kelvin(self.df[self.soil_temperature_headers[1]])
        temps_3 = self.convert_temps_to_kelvin(self.df[self.soil_temperature_headers[2]])
        values = np.transpose(np.array([temps_1, temps_2, temps_3]))

        attrs = {"cell_methods": "time:mean",
                 "long_name": "Soil Temperature",
                 "units": "K",
                 "standard_name": "soil_temperature",
                 "coordinates": "latitude longitude"}

        self.create_variable("soil_temperature", np.float32, ("time","index"), values, self.soil_temperature_headers, **attrs)

    def create_soil_moisture_variable(self):
        # Create the soil water potential variable
        values = np.transpose(np.array([self.df[self.soil_moisture_headers[0]], self.df[self.soil_moisture_headers[1]], self.df[self.soil_moisture_headers[2]]]))

        # Set water potential variable attributes
        attrs = {"cell_methods": "time:mean",
                 "long_name": "Soil Water Potential",
                 "units": "kPa",
                 "coordinates": "latitude longitude"}

        self.create_variable("soil_water_potential", np.float32, ("time","index"), values, self.soil_moisture_headers, **attrs)

    def create_soil_heat_flux_variable(self):
        # Create the soil heat flux variable
        values = np.transpose(np.array([self.df[self.soil_heat_flux_headers[0]], self.df[self.soil_heat_flux_headers[1]], self.df[self.soil_heat_flux_headers[2]]]))
 
        # Set soil heat flux variable attributes
        attrs = {"cell_methods": "time:mean",
                 "long_name": "Downward Heat Flux in Soil",
                 "standard_name": "downward_heat_flux_soil",
                 "units": "W m-2",
                 "coordinates": "latitude longitude"}

        self.create_variable("downward_heat_flux_in_soil", np.float32, ("time","index"), values, self.soil_heat_flux_headers, **attrs)

    def create_qc_variable(self, name, headers, **kwargs):
        var = self.dataset.createVariable(name, np.byte, ("time","index"))
        qc_headers = [h + '_qc' for h in headers]
        var[:] = np.transpose(np.array([self.qc[qc_headers[0]], self.qc[qc_headers[1]], self.qc[qc_headers[2]]]))
        var.units = "1"
        for k, v in kwargs.items():
            setattr(var, k, v)

    def create_specific_variables(self):
        # create variables
        self.create_soil_temp_variable()
        self.create_soil_moisture_variable()
        self.create_soil_heat_flux_variable()

        # create qc variables
        # qc soil heat flux
        attrs = {"long_name": "Data Quality flag: Soil Heat Flux",
                 "flag_values": "0b, 1b, 2b, 3b, 4b",
                 "flag_meanings": "0: not_used \n1: good data \n2: bad_data_value_outside_operational_range_-30C_to_70C \n3: suspect_data \n4: timestamp_error"}
        self.create_qc_variable("qc_flag_soil_heat_flux", self.soil_heat_flux_headers, **attrs)
        
        # qc soil temp
        attrs = {"long_name": "Data Quality flag: Soil Temperature",
                 "flag_values": "0b, 1b, 2b, 3b, 4b",
                 "flag_meanings": "0: not_used \n1: good data \n2: bad_data_outside_operational_range_-35C_to_50C \n3: suspect_data \n4: timestamp_error"}
        self.create_qc_variable("qc_flag_soil_temperature", self.soil_temperature_headers, **attrs)
        
        # qc soil water potential 
        attrs = {"long_name": "Data Quality flag: Soil Water Potential",
                 "flag_values": "0b, 1b, 2b, 3b, 4b, 5b",
                 "flag_meanings": "0: not_used \n1: good data \n2: bad_data_soil_water_potential_>_80kPa_contact_between_soil_and_sensor_usually_lost \n3: bad_data_value_outside_operational_range_0_to_200_kPa \n4: suspect_data \n5: timestamp_error"}
        self.create_qc_variable("qc_flag_soil_water_potential", self.soil_moisture_headers, **attrs)
