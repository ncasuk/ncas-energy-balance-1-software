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

    def create_specific_dimensions(self, dataset):
        # create index dimension of length 3
        dataset.createDimension("index", CONFIG['soil']['index_length'])


    def create_soil_temp_variable(self, dataset):
        # Create the soil temp variable - convert to kelvin
        soil_temp = dataset.createVariable("soil_temperature", np.float32, ("time","index"), fill_value=-1e+20)
        temps_1 = self.convert_temps_to_kelvin(self.df[self.soil_temperature_headers[0]])
        temps_2 = self.convert_temps_to_kelvin(self.df[self.soil_temperature_headers[1]])
        temps_3 = self.convert_temps_to_kelvin(self.df[self.soil_temperature_headers[2]])
        soil_temp[:] = np.transpose(np.array([temps_1, temps_2, temps_3]))

        # mask the data according to the qc
        soil_temp_masked = np.transpose(np.array([self.df_masked[self.soil_temperature_headers[0]], self.df_masked[self.soil_temperature_headers[1]], self.df_masked[self.soil_temperature_headers[2]]]))
        # Set temp variable attributes
        soil_temp.cell_methods = "time:mean"
        soil_temp.valid_min = np.nanmin(soil_temp_masked) # get from valid values
        soil_temp.valid_max = np.nanmax(soil_temp_masked)
        soil_temp.long_name =  "Soil Temperature"  
        soil_temp.units = "K"   
        soil_temp.standard_name = "soil_temperature" 
        soil_temp.coordinates = "latitude longitude"

    def create_soil_moisture_variable(self, dataset):
        # Create the soil water potential variable
        soil_water_potential = dataset.createVariable("soil_water_potential", np.float32, ("time","index"), fill_value=-1e+20)
        soil_water_potential[:] = np.transpose(np.array([self.df[self.soil_moisture_headers[0]], self.df[self.soil_moisture_headers[1]], self.df[self.soil_moisture_headers[2]]]))

        # mask the data according to the qc
        soil_water_potential_masked = np.transpose(np.array([self.df_masked[self.soil_moisture_headers[0]], self.df_masked[self.soil_moisture_headers[1]], self.df_masked[self.soil_moisture_headers[2]]]))

        # Set water potential variable attributes
        soil_water_potential.cell_methods = "time:mean"
        soil_water_potential.valid_min = np.nanmin(soil_water_potential_masked) # get from valid values
        soil_water_potential.valid_max = np.nanmax(soil_water_potential_masked)
        soil_water_potential.long_name =  "Soil Water Potential"  
        soil_water_potential.units =  "kPa"   
        soil_water_potential.coordinates = "latitude longitude"

    def create_soil_heat_flux_variable(self, dataset):
        # Create the soil heat flux variable
        soil_heat_flux = dataset.createVariable("downward_heat_flux_in_soil", np.float32, ("time","index"), fill_value=-1e+20)
        soil_heat_flux[:] = np.transpose(np.array([self.df[self.soil_heat_flux_headers[0]], self.df[self.soil_heat_flux_headers[1]], self.df[self.soil_heat_flux_headers[2]]]))
        
        # mask the data according to the qc
        soil_heat_flux_masked = np.transpose(np.array([self.df_masked[self.soil_heat_flux_headers[0]], self.df_masked[self.soil_heat_flux_headers[1]], self.df_masked[self.soil_heat_flux_headers[2]]]))

        # Set soil heat flux variable attributes
        soil_heat_flux.cell_methods = "time:mean"
        soil_heat_flux.valid_min = np.nanmin(soil_heat_flux_masked) # get from valid values
        soil_heat_flux.valid_max = np.nanmax(soil_heat_flux_masked)
        soil_heat_flux.long_name =  "Downward Heat Flux in Soil"  
        soil_heat_flux.units =  "W m-2"   
        soil_heat_flux.standard_name =  "downward_heat_flux_soil"
        soil_heat_flux.coordinates = "latitude longitude"

    def create_qc_variable(self, dataset, name, headers, **kwargs):
        var = dataset.createVariable(name, np.byte, ("time","index"))
        qc_headers = [h + '_qc' for h in headers]
        var[:] = np.transpose(np.array([self.qc[qc_headers[0]], self.qc[qc_headers[1]], self.qc[qc_headers[2]]]))
        var.units = "1"
        for k, v in kwargs.items():
            setattr(var, k, v)

    def create_specific_variables(self, dataset):
        # create variables
        self.create_soil_temp_variable(dataset)
        self.create_soil_moisture_variable(dataset)
        self.create_soil_heat_flux_variable(dataset)

        # create qc variables
        # qc soil heat flux
        attrs = {"long_name": "Data Quality flag: Soil Heat Flux",
                 "flag_values": "0b, 1b, 2b, 3b, 4b",
                 "flag_meanings": "0: not_used \n1: good data \n2: bad_data_value_outside_operational_range_-30C_to_70C \n3: suspect_data \n4: timestamp_error"}
        self.create_qc_variable(dataset,"qc_flag_soil_heat_flux", self.soil_heat_flux_headers, **attrs)
        
        # qc soil temp
        attrs = {"long_name": "Data Quality flag: Soil Temperature",
                 "flag_values": "0b, 1b, 2b, 3b, 4b",
                 "flag_meanings": "0: not_used \n1: good data \n2: bad_data_outside_operational_range_-35C_to_50C \n3: suspect_data \n4: timestamp_error"}
        self.create_qc_variable(dataset,"qc_flag_soil_temperature", self.soil_temperature_headers, **attrs)
        
        # qc soil water potential 
        attrs = {"long_name": "Data Quality flag: Soil Water Potential",
                 "flag_values": "0b, 1b, 2b, 3b, 4b, 5b",
                 "flag_meanings": "0: not_used \n1: good data \n2: bad_data_soil_water_potential_>_80kPa_contact_between_soil_and_sensor_usually_lost \n3: bad_data_value_outside_operational_range_0_to_200_kPa \n4: suspect_data \n5: timestamp_error"}
        self.create_qc_variable(dataset,"qc_flag_soil_water_potential", self.soil_moisture_headers, **attrs)
