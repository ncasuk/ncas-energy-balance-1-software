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
        output_path = CONFIG['common']['output_path']
        output_file = os.path.join(output_path, output_file_name)

        self.dataset = Dataset(output_file, "w", format='NETCDF4_CLASSIC')
        self.create_netcdf()
        self.dataset.close()

        print(f"Dataset created at {output_file}")

    def convert_date_to_string(self, date, frequency):
        if frequency == "monthly":
            date = date.strftime("%Y%m")

        elif frequency == "daily":
            date = date.strftime("%Y%m%d")

        else:
            raise ValueError(f'Frequency {self.frequency} is not supported. Options are daily or monthly.')
        
        return date

    @staticmethod
    def convert_times(times):
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
        datetimes = []
        for t in times:
            t = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
            datetimes.append(t)
        return datetimes

    def get_masked_data(self, mask_value):
        self.mask = (self.qc <= mask_value)
        self.df_masked = pd.DataFrame(columns = self.headers)
        self.df_masked[self.dt_header] = self.df[self.dt_header]

        for col in self.headers:
            mask_column = self.mask[col+'_qc']
            self.df_masked[col] = self.df[col][mask_column]

    def create_time_variable(self):
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
        lon_var = self.dataset.createVariable("longitude", np.float32, ("longitude",))
        lon_var[:] = CONFIG['common']['longitude_value']
        lon_var.units = "degrees_east"
        lon_var.standard_name = "longitude"
        lon_var.long_name = "Longitude"

    def create_lat_variable(self):
        lat_var = self.dataset.createVariable("latitude", np.float32, ("latitude",))
        lat_var[:] = CONFIG['common']['latitude_value']
        lat_var.units = "degrees_north"
        lat_var.standard_name = "latitude"
        lat_var.long_name = "Latitude"

    def create_variable(self, var_name, data_type, dims, header, **kwargs):
        # Create variable
        var = self.dataset.createVariable(var_name, data_type, dims, fill_value=self.fill_value)

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
        var = self.dataset.createVariable(name, data_type, ("time",))
        var[:] = values
        var.units = "1"
        var.long_name = long_name
        var.valid_min = var[:].min()
        var.valid_max = var[:].max()

    def create_qc_variable(self, name, header, dimensions, **kwargs):
        var = self.dataset.createVariable(name, np.byte, dimensions)
        qc_header = header + '_qc'
        var[:] = self.qc[qc_header]
        var.units = "1"
        for k, v in kwargs.items():
            setattr(var, k, v)

    def set_global_attributes(self):
        for k, v in CONFIG['global'].items():
            setattr(self.dataset, k, v)

        self.dataset.last_revised_date = datetime.utcnow().isoformat()
        self.dataset.time_coverage_start = datetime.strptime(self.times.iloc[0], "%Y-%m-%d %H:%M:%S").isoformat()
        self.dataset.time_coverage_end = datetime.strptime(self.times.iloc[-1], "%Y-%m-%d %H:%M:%S").isoformat()

    def create_specific_dimensions(self):
        raise NotImplementedError

    def create_specific_variables(self):
        raise NotImplementedError

    def create_netcdf(self):
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
        
    