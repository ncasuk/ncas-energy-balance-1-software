__author__ = 'Elle Smith'
__date__ = '09 Aug 2021'
__contact__ = 'eleanor.smith@stfc.ac.uk'

import numpy as np
from energy_balance import CONFIG
from .base_netcdf import BaseNetCDF


class SoilNetCDF(BaseNetCDF):

    """
    Class for creating soil netcdf files.
    Creates soil specific dimensions and variables 

    """

    soil_moisture_headers = CONFIG['soil']['soil_moisture_headers']
    soil_temperature_headers = CONFIG['soil']['soil_temperature_headers']
    soil_heat_flux_headers = CONFIG['soil']['soil_heat_flux_headers']
    headers = soil_moisture_headers + soil_temperature_headers + soil_heat_flux_headers
    data_product = 'soil'
    index_length = CONFIG['soil']['index_length']

    @staticmethod
    def convert_temps_to_kelvin(temps):
        """
        Convert temperatures from degrees celsius to Kelvin.
        
        :param temps: (sequence) Temperatures to convert (in degrees C).
        :returns: (list) The temperatures converted to Kelvin.
        """
        temp_values = []
        for temp in temps:
            temp_values.append(temp + 273.15)
        return temp_values

    def create_specific_dimensions(self):
        """
        SoilNetCDF specific implementation to create index dimension.
        """
        # create index dimension of length specified in config file.
        self.dataset.createDimension("index", self.index_length)

    def create_variable(self, name, data_type, headers, **kwargs):
        """
        SoilNetCDF specific implementation to account for index dimension.

        :param name: (str) The name of the variable to be created.
        :param data_type: The data type of the variable to be created e.g. numpy.float32 
        :param headers: (list) The name of the columns in the pandas dataframe to use to populate the data of this variable.
        :param kwargs: (dict) Dictionary of attributes {'attr_name': 'attr_value'} to set on the variable e.g. {'standard_name': 'soil_temperature'}

        """
        var = self.dataset.createVariable(name, data_type, ("time","index"), fill_value=-1e+20)

        # get the values
        values = np.transpose(np.array([self.df[headers[n]] for n in range(self.index_length)]))

        # convert any nan values to fill values
        values[np.isnan(values)] = self.fill_value
        var[:] = values

        # mask the data according to the qc
        var_masked = np.transpose(np.array([self.df_masked[headers[n]].astype(data_type) for n in range(self.index_length)]))
        
        # Set variable attributes
        var.valid_min = np.nanmin(var_masked) # get from valid values
        var.valid_max = np.nanmax(var_masked)

        for k, v in kwargs.items():
            setattr(var, k, v)

    def create_soil_temp_variable(self):
        """
        Create soil temperature variable on the netCDF dataset.
        """
        # Create the soil temp variable - convert to kelvin
        for col in self.soil_temperature_headers:
            self.df[col] = self.convert_temps_to_kelvin(self.df[col])

        # convert the masked values to kelvin    
        for col in self.soil_temperature_headers:
            self.df_masked[col] = self.convert_temps_to_kelvin(self.df_masked[col])

        attrs = {"cell_methods": "time:mean",
                 "long_name": "Soil Temperature",
                 "units": "K",
                 "standard_name": "soil_temperature",
                 "coordinates": "latitude longitude"}

        self.create_variable("soil_temperature", np.float32, self.soil_temperature_headers, **attrs)

    def create_soil_moisture_variable(self):
        """
        Create soil water potential variable on the netCDF dataset.
        """
        # Set water potential variable attributes
        attrs = {"cell_methods": "time:mean",
                 "long_name": "Soil Water Potential",
                 "units": "kPa",
                 "coordinates": "latitude longitude"}

        self.create_variable("soil_water_potential", np.float32, self.soil_moisture_headers, **attrs)

    def create_soil_heat_flux_variable(self):
        """
        Create soil heat flux variable on the netCDF dataset.
        """
        # Set soil heat flux variable attributes
        attrs = {"cell_methods": "time:mean",
                 "long_name": "Downward Heat Flux in Soil",
                 "standard_name": "downward_heat_flux_soil",
                 "units": "W m-2",
                 "coordinates": "latitude longitude"}

        self.create_variable("downward_heat_flux_in_soil", np.float32, self.soil_heat_flux_headers, **attrs)

    def create_qc_variable(self, name, headers, **kwargs):
        """
        SoilNetCDF specific implementation to account for index dimension. 

        :param name: (str) The name of the variable to be created.
        :param header: (list) The names of the columns in the df pandas dataframe to use to populate the data of this variable.
        :param kwargs: (dict) Dictionary of attributes {'attr_name': 'attr_value'} to set on the variable e.g. {'standard_name': 'soil_temperature'}

        """
        var = self.dataset.createVariable(name, np.byte, ("time","index"))
        qc_headers = [h + '_qc' for h in headers]
        var[:] = np.transpose(np.array([self.qc[qc_headers[n]] for n in range(self.index_length)]))
        var.units = "1"
        for k, v in kwargs.items():
            setattr(var, k, v)

    def create_specific_variables(self):
        """
        SoilNetCDF specific implementation to create all soil specific variables.
        """
        # create variables
        self.create_soil_temp_variable()
        self.create_soil_moisture_variable()
        self.create_soil_heat_flux_variable()

        # create qc variables
        # qc soil heat flux
        attrs = {"long_name": "Data Quality flag: Soil Heat Flux",
                 "flag_values": "0b,1b,2b,3b,4b",
                 "flag_meanings": "0: not_used \n1: good data \n2: bad_data_value_outside_operational_range_-30C_to_70C \n3: suspect_data \n4: timestamp_error"}
        self.create_qc_variable("qc_flag_soil_heat_flux", self.soil_heat_flux_headers, **attrs)
        
        # qc soil temp
        attrs = {"long_name": "Data Quality flag: Soil Temperature",
                 "flag_values": "0b,1b,2b,3b,4b",
                 "flag_meanings": "0: not_used \n1: good data \n2: bad_data_outside_operational_range_-35C_to_50C \n3: suspect_data \n4: timestamp_error"}
        self.create_qc_variable("qc_flag_soil_temperature", self.soil_temperature_headers, **attrs)
        
        # qc soil water potential 
        attrs = {"long_name": "Data Quality flag: Soil Water Potential",
                 "flag_values": "0b,1b,2b,3b,4b,5b",
                 "flag_meanings": "0: not_used \n1: good data \n2: bad_data_soil_water_potential_>_80kPa_contact_between_soil_and_sensor_usually_lost \n3: bad_data_value_outside_operational_range_0_to_200_kPa \n4: suspect_data \n5: timestamp_error"}
        self.create_qc_variable("qc_flag_soil_water_potential", self.soil_moisture_headers, **attrs)
