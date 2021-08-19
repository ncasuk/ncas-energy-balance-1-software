===============
Quality Control
===============

This explains the quality control values and definitions used when creating quality control csvs and netCDF files (which include quality control variables once created)
For more information on how these netCDF files have been built see https://sites.google.com/ncas.ac.uk/ncasobservations/home/data-project/ncas-data-standards/ncas-amof/. 
The control quality control variables are included as they are 'Data Product Specific Variables'. 


soil
====

For the soil data product, 3 quality control variables are created.
Below each, the values and meanings used are listed. These are also included in the netCDF file created.
These are:

1. qc_flag_soil_heat_flux

    0: not used
    1: good data
    2: bad data - value outside operational range (-30 to 70 C) (e.g. if the soil temperature is outside this range, the corresponding value of soil heat flux is flagged)
    3: suspect data
    4: timestamp error

    * flag 2 is applied automatically, all other data is marked as 1.

2. qc_flag_soil_temperature

    0: not used
    1: good data
    2: bad data - value outside operational range (-35 to 50 C)
    3: suspect data (includes temperature data that is higher/ lower than expected - these expected values can be set in the config file - speak to instrument scientist to find out what this should be)
    4: timestamp error

    * flags 2 and 3 (3 for outside range of expected temperature) are applied automatically, all other data is marked as 1. More data can be manually marked as suspect if needed.

3. qc_flag_soil_water_potential

    0: not used
    1: good data
    2: bad data - soil water potential over 80kPa (contact between soil and sensor usually lost at this point)
    3: bad data - value outside operational range (0 to 200 kPa)
    4: suspect data
    5: timestamp error

    * flags 2 and 3 are applied automatically, all other data is marked as 1.

radiation
=========

For the radiation data product, 6 quality control variables are created.

1. qc_flag_upwelling_shortwave

    0: not used
    1: good data
    2: no data
    3: bad data sw radiation < 0
    4: bad data sw radiation > 2000 W m-2
    5: suspect data
    6: timestamp error

    * flags 2, 3 and 4 are applied automatically, all other data is marked as 1.
  
2. qc_flag_downwelling_shortwave

    0: not used
    1: good data
    2: no data
    3: bad data sw radiation < 0
    4: bad data sw radiation > 2000 W m-2
    5: suspect data
    6: timestamp error

    * flags 2, 3 and 4 are applied automatically, all other data is marked as 1.
  
3. qc_flag_upwelling_longwave

    0: not used
    1: good data
    2: no data
    3: bad data sw radiation < 0
    4: bad data sw radiation > 1000 W m-2
    5: suspect data
    6: timestamp error  

    * flags 2, 3 and 4 are applied automatically, all other data is marked as 1.

4. qc_flag_downwelling_longwave

    0: not used
    1: good data
    2: no data
    3: bad data sw radiation < 0
    4: bad data sw radiation > 1000 W m-2
    5: suspect data
    6: timestamp error

    * flags 2, 3 and 4 are applied automatically, all other data is marked as 1.

5. qc_flag_body_temperature

    0: not used
    1: good data
    2: bad data body temperature outside operational range -40 to 80C
    3: suspect data
    4: timestamp error

    * flag 2 is applied automatically, all other data is marked as 1. This flag is applied to all variables, as they are all affected if the body temperature is outside operational bounds.

6. qc_flag_cleaning

    0: not used
    1: good data
    2: bad data sensor being cleaned (the times for this should be set in the config file - speak to instrument scientist to find out what this should be)
    3: suspect data
    4: timestamp error

    * flag 2 is applied automatically, all other data is marked as 1. This flag is applied to all variables, as they are all affected when the sensor is being cleaned.

* The script to create netCDF files or that which makes the qc csvs, automatically applies flags as mentioned under each variable. Any other flags are there to be added manually after inspection of the data.
* Manually adding flags may result in the valid max/min values of variables needing to be changed - these are calculated only from 'good data'.
* Suspect data has been included to cover other scenarios not covered by the other flags e.g. data is higher/lower than expected, the data has changed significantly since the last reading.