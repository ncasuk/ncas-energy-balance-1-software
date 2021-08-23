__author__ = 'Elle Smith'
__date__ = '09 Aug 2021'
__contact__ = 'eleanor.smith@stfc.ac.uk'

import pandas as pd
from netCDF4 import Dataset
from datetime import datetime
import numpy as np
import os

from energy_balance import CONFIG

class BaseNetCDF:

    """
    Base class used for creating netCDF files.
    Creates all the common variables found in netCDF files under the NCAS-GENERAL Data Standard.
    Sets all the required global attributes.

    Constant values are taken from the config file, excluding 'headers' and 'data_product' which must be set in each specific implementation.

    :param df: A pandas dataframe containing all columns required to create the netCDF file.
    :param qc: A pandas dataframe with the same columns as df, but containing the quality control values instead. (i.e. 1, 2, 3 etc.)
    :param date: (datetime.datetime) The date to create the netCDF file for. If frequency is monthly, only the year and month will be taken into account.
    :param frequency: (str) 'daily' or 'monthly'. Determines whether the file will use data from one day or for one month.
    """

    dt_header = CONFIG['common']['datetime_header']
    headers = 'UNDEFINED'
    data_product = "UNDEFINED"
    qc_flag_level = CONFIG['common']['qc_flag_level']
    fill_value = CONFIG['common']['fill_value']

    def __init__(self, df, qc, date, frequency):
        self.df = df
        self.qc = qc
        self.get_masked_data(self.qc_flag_level)

        # validate date format
        date = self.convert_date_to_string(date, frequency)

        output_file_name = f"ncas-energy-balance-1_{CONFIG['global']['platform']}_{date}_{self.data_product}_v{CONFIG['global']['product_version']}.nc"
        output_path = CONFIG['common']['netcdf_path']
        output_file = os.path.expanduser(os.path.join(output_path, output_file_name))

        self.dataset = Dataset(output_file, "w", format='NETCDF4_CLASSIC')
        self.create_netcdf()
        self.dataset.close()

        print(f"Dataset created at {output_file}")


    def convert_date_to_string(self, date, frequency):
        """
        Generate a date string for the file name based on the date provided and the frequency required.

        :param date: (datetime.datetime) The date to convert to string.
        :param frequency: (str) The frequency at which to have the date string.
        :returns: (str) The date now converted to string format.
        """

        if frequency == "monthly":
            date = date.strftime("%Y%m")

        elif frequency == "daily":
            date = date.strftime("%Y%m%d")

        else:
            raise ValueError(f'Frequency {self.frequency} is not supported. Options are daily or monthly.')
        
        return date

    @staticmethod
    def convert_times(times):
        """
        Convert times from strings to total seconds since 1970-01-01T00:00:00.

        :param times: (sequence) Times to convert to total seconds since 1970-01-01T00:00:00.
        :returns: (list) The times converted to total seconds since 1970-01-01T00:00:00. 
        """
        ref_time = datetime.strptime("1970-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S")
        
        time_values = []
        for t in times:
            t = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
            diff = t - ref_time
            ts = diff.total_seconds()
            time_values.append(ts)
        return time_values

    @staticmethod
    def times_as_datetimes(times):
        """
        Convert times from strings to datetimes.

        :param times: (sequence) Times to convert to datetimes in format Y-m-d H:M:S.
        :returns: (list) The times converted to datetimes.
        """
        datetimes = []
        for t in times:
            t = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
            datetimes.append(t)
        return datetimes

    def get_masked_data(self, mask_value):
        """
        Create masked pandas dataframe based on self.qc and the qc flag requested.
        Sets self.df_masked.

        :param mask_value: (int) Max value of qc to show i.e. 1 will show only 'good data', 2 will show good data and data marked with a flag of 2.
        """
        self.mask = (self.qc <= mask_value)
        self.df_masked = pd.DataFrame(columns = self.headers)
        self.df_masked[self.dt_header] = self.df[self.dt_header]

        for col in self.headers:
            mask_column = self.mask[col+'_qc']
            self.df_masked[col] = self.df[col][mask_column]

    def create_time_variable(self):
        """
        Create the common time variable.
        """
        time_units = "seconds since 1970-01-01 00:00:00"
        time_var = self.dataset.createVariable("time", np.float64, ("time",))

        self.times = self.df[self.dt_header]
        time_var[:] = self.convert_times(self.times)
        time_var.units = time_units
        time_var.standard_name = "time"
        time_var.calendar = "standard"
        time_var.axis = 'T'
        time_var.long_name = "Time (seconds since 1970-01-01 00:00:00)"

        time_var.valid_min = time_var[:].min()
        time_var.valid_max = time_var[:].max()

    def create_lon_variable(self):
        """
        Create the common longitude variable.
        """
        lon_var = self.dataset.createVariable("longitude", np.float32, ("longitude",))
        lon_var[:] = CONFIG['common']['longitude_value']
        lon_var.units = "degrees_east"
        lon_var.standard_name = "longitude"
        lon_var.long_name = "Longitude"

    def create_lat_variable(self):
        """
        Create the common latitude variable.
        """
        lat_var = self.dataset.createVariable("latitude", np.float32, ("latitude",))
        lat_var[:] = CONFIG['common']['latitude_value']
        lat_var.units = "degrees_north"
        lat_var.standard_name = "latitude"
        lat_var.long_name = "Latitude"

    def create_variable(self, name, data_type, dims, header, **kwargs):
        """
        Generic method to create a variable in the netCDF4 dataset.

        :param name: (str) The name of the variable to be created.
        :param data_type: The data type of the variable to be created e.g. numpy.float32 
        :param dims: (tuple) The dimensions of the variable to be created e.g. ('time', ) or ('time', 'index')
        :param header: (str) The name of the column in the pandas dataframe to use to populate the data of this variable.
        :param kwargs: (dict) Dictionary of attributes {'attr_name': 'attr_value'} to set on the variable e.g. {'standard_name': 'soil_temperature'}
        """
        # Create variable
        var = self.dataset.createVariable(name, data_type, dims, fill_value=self.fill_value)

        # convert any nan values to fill values
        self.df[header][np.isnan(self.df[header])] = self.fill_value

        var[:] = self.df[header]

        # mask the data according to the qc
        var_masked = self.df_masked[header].astype(data_type)
        
        # Set variable attributes
        var.valid_min = np.nanmin(var_masked) # get from valid values
        var.valid_max = np.nanmax(var_masked)

        for k, v in kwargs.items():
            setattr(var, k, v)

    def create_time_related_variable(self, name, data_type, values, long_name):
        """
        Generic method to create variables day of year, day, year, month, hour, second, minute.

        :param name: (str) The name of the variable to be created.
        :param data_type: The data type of the variable to be created e.g. numpy.float32 
        :param values: (sequence) The values to set for this variable.
        :param long_name: (str) The long name of this variable.
        """
        var = self.dataset.createVariable(name, data_type, ("time",))
        var[:] = values
        var.units = "1"
        var.long_name = long_name
        var.valid_min = var[:].min()
        var.valid_max = var[:].max()

    def create_qc_variable(self, name, header, dimensions, **kwargs):
        """
        Generic method to create a qc variable on the dataset.

        :param name: (str) The name of the variable to be created.
        :param header: (str) The name of the column in the df pandas dataframe to use to populate the data of this variable.
        :param dimensions: (tuple) The dimensions of the variable to be created e.g. ('time', ) or ('time', 'index')
        :param kwargs: (dict) Dictionary of attributes {'attr_name': 'attr_value'} to set on the variable e.g. {'standard_name': 'soil_temperature'}

        """
        var = self.dataset.createVariable(name, np.byte, dimensions)
        qc_header = header + '_qc'
        var[:] = self.qc[qc_header]
        var.units = "1"
        for k, v in kwargs.items():
            setattr(var, k, v)

    def set_global_attributes(self):
        """
        Sets the global attributes in the dataset based on those listed in the config file.
        """
        for k, v in CONFIG['global'].items():
            setattr(self.dataset, k, v)

        self.dataset.last_revised_date = datetime.utcnow().isoformat()
        self.dataset.time_coverage_start = datetime.strptime(self.times.iloc[0], "%Y-%m-%d %H:%M:%S").isoformat()
        self.dataset.time_coverage_end = datetime.strptime(self.times.iloc[-1], "%Y-%m-%d %H:%M:%S").isoformat()

    def create_specific_dimensions(self):
        """
        Class specific implementation to create dimensions specific to that data product.
        """
        raise NotImplementedError

    def create_specific_variables(self):
        """
        Class specific implementation to create variables specific to that data product, including any qc variables.
        """
        raise NotImplementedError

    def create_netcdf(self):
        """
        Method to create the netCDF dataset
        """
        # Create the time dimension - with unlimited length
        self.dataset.createDimension("time", None)
        # Create the latitude dimension - with length 1 as stationary
        self.dataset.createDimension("latitude", 1)
        # Create the longitude dimension - with length 1 as stationary
        self.dataset.createDimension("longitude", 1)

        # create basic variables
        self.create_time_variable()
        self.create_lat_variable()
        self.create_lon_variable()

        # create other variables e.g. year of day
        datetimes = self.times_as_datetimes(self.times)
        # day of year
        doy_vals = [t.timetuple().tm_yday for t in datetimes]
        self.create_time_related_variable("day_of_year", np.float32, doy_vals, "Day of Year")
        # year
        year_vals = [t.year for t in datetimes]
        self.create_time_related_variable("year", np.int32, year_vals, "Year")
        # month
        month_vals = [t.month for t in datetimes]
        self.create_time_related_variable("month", np.int32, month_vals, "Month")
        # day
        day_vals = [t.day for t in datetimes]
        self.create_time_related_variable("day", np.int32, day_vals, "Day")
        # hour
        hour_vals = [t.hour for t in datetimes]
        self.create_time_related_variable("hour", np.int32, hour_vals, "Hour")
        # minute
        minute_vals = [t.minute for t in datetimes]
        self.create_time_related_variable("minute", np.int32, minute_vals, "Minute")
        # second
        second_vals = [t.second for t in datetimes]
        self.create_time_related_variable("second", np.float32, second_vals, "Second")

        # create specific dimensions and variables
        self.create_specific_dimensions()
        self.create_specific_variables()

        # set global attributes
        self.set_global_attributes()
        
    