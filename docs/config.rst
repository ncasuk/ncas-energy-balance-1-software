======
Config
======

This explains the various options that can be set when using the scripts.
To see the config file: https://github.com/ncasuk/ncas-energy-balance-1-software/blob/master/energy_balance/etc/config.ini

To override these settings, provide your own config file by setting the environment variable CONFIG as the file path to your file.
e.g.

.. code-block:: console

    $ export CONFIG='path/to/my/config.ini'

Specifying types
################
    
It is possible to specify the type of the entries in the configuration file, for example if you want a value to be a list when the file is parsed.
    
This is managed through a ``[config_data_types]`` section at the top of the INI file which has the following options::
    
    [config_data_types]
    # only used by installed package
    lists =
    dicts =
    ints =
    floats =
    boolean =
    # use the below when creating your own file
    extra_lists =
    extra_dicts =
    extra_ints =
    extra_floats =
    extra_booleans =
    
Simply adding the name of the value you want to format afer ``=`` will render the correct format. e.g. ``ints = index_length processing_level qc_flag_level`` will set ``index_length``, ``processing_level`` and ``qc_flag_level`` as ints.

Settings
########

These settings apply across the scripts::

    [common]
    # url for logger E.g. tcp:iphost:port or serial:/dev/ttyUSB0:19200:8N1 or serial:/COM1:19200:8N1
    logger_url = serial:/dev/ttyUSB0:115200
    # latitude of station
    latitude_value = 13.1
    # longitude of station
    longitude_value = 25.5
    # name of date/time column in files/on logger
    datetime_header = Datetime
    # path to output/read logger csv files from
    logger_csv_path = /Users/qsp95418/AMOF/ncas-energy-balance-1-software
    # where to output netcdf files
    netcdf_path = /Users/qsp95418/AMOF/ncas-energy-balance-1-software
    # path to output qc csv files
    qc_csv_path = /Users/qsp95418/AMOF/ncas-energy-balance-1-software
    # masking will include values that have been quality controlled to this level or less (e.g. <= 1)
    qc_flag_level = 1
    # fill value to use in netcdf files
    fill_value = -1e+20
    # names of the tables in the logger to process in scripts
    logger_tables = Housekeeping GPS_datetime SoilTemperature SoilMoisture SoilHeatFlux Radiation
    # names of the tables you have created in mysql (must map to logger tables)
    mysql_tables = housekeeping gps soil_temp soil_moisture soil_heat_flux radiation


These settings are specific for the soil data product::

    [soil]
    # number of sensors
    index_length = 3
    # input file path to directory containing soil csv files to turn into netcdf files
    input_file_path = /Users/qsp95418/AMOF/
    # double % to escape as it is a special character
    # date format as it is on the input files
    input_date_format = %%Y-%%m-%%d
    # format of files - use {date} where the date exists in the file name
    soil_moisture_file = SoilMoisture_{date}.csv
    soil_temperature_file = SoilTemperature_{date}.csv
    soil_heat_flux_file = SoilHeatFlux_{date}.csv
    # columns to extract: what the columns are called in the input csv file to allow them to be extracted 
    # give the below in index order i.e. the first listed will be given index 1
    soil_moisture_headers = WP_kPa_1 WP_kPa_2 WP_kPa_3 
    soil_temperature_headers = T107_1 T107_2 T107_3 
    soil_heat_flux_headers = shf_1 shf_2 shf_3
    # the max/min expected soil temp in degrees C. Any temperature outside this will be flagged as suspect data
    max_expected_temp = 28
    min_expected_temp = 18
    
These settings are specific for the radiation data product::

    [radiation]
    # input file path to directory containing radiation csv files to turn into netcdf files
    input_file_path = /Users/qsp95418/AMOF/
    # double % to escape as it is a special character
    # date format as it is on the input files
    input_date_format = %%Y-%%m-%%d
    # format of file
    radiation_file = Radiation_{date}.csv
    # columns to extract: what the columns are called in the input csv file to allow them to be extracted 
    # give the below in index order i.e. the first listed will be given index 1
    # longwave downwelling
    lwdn_header = IR01Dn
    # longwave upwelling
    lwup_header = IR01Up
    # shortwave downwelling
    swdn_header = SR01Dn
    # shortwave upwelling
    swup_header = SR01Up
    # radiometer body temperature (in kelvin)
    body_temp_header = NR01TK
    # the time range to qc as 'sensor being cleaned'
    # give in hh:mm:ss
    cleaning_time_lower = 05:55:00
    cleaning_time_upper = 06:05:00

These settings correspond to the global attributes on the netCDF files produced. Anything set here will be set as a global attribute::
    
    [global]
    Conventions = CF-1.6, NCAS-AMF-2.0.0
    source = NCAS Energy Balance Station unit 1
    instrument_manufacturer = Campbell Scientific
    instrument_model = CR3000
    # fixed but don't have at the moment
    instrument_serial_number = 
    instrument_software = EB1_logger.cr5
    instrument_software_version = v1
    creator_name = Eleanor Smith
    creator_email = eleanor.smith@stfc.ac.uk
    creator_url = https://orcid.org/0000-0002-6448-5778
    institution = Centre for Environmental Data Analysis (CEDA)
    processing_software_url = https://github.com/ncasuk/ncas-energy-balance-1-software
    processing_software_version = v0.1
    calibration_sensitivity =
    calibration_certification_date =
    calibration_certification_url =
    sampling_interval = 5 minute
    averaging_interval = 5 minute
    product_version = 0.1
    processing_level = 1
    project = energy balance placement
    project_principal_invesitgator = Eleanor Smith
    project_principal_invesitgator_email = eleanor.smith@stfc.ac.uk
    project_principal_invesitgator_url = https://orcid.org/0000-0002-6448-5778
    licence = Data usage licence - UK Government Open Licence agreement: http://www.nationalarchives.gov.uk/doc/open-government-licence
    acknowledment = Acknowledgement of NCAS as the data provider is required whenever and wherever these data are used
    platform = lab
    platform_type = stationary_platform
    deployment_mode = land
    title = Measurements from the NCAS energy balance station.
    featureType = timeSeries
    geospatial_bounds = 
    platform_altitude = 
    location_keywords = 
    amf_vocabularies_release = https://github.com/ncasuk/AMF_CVs/tree/v2.0.0
    history = 
    comment = 