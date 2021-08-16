.. _scripts:

=======
Scripts
=======

The scripts make use of the package PyCampbellCR1000 (on an updated fork) - this works for CR3000 loggers as well.
The documentation for this package can be found here: https://pycampbellcr1000.readthedocs.io/en/latest/

To see the API and source code, go to `scripts-api`_.

Various settings used in these scripts can be set/changed in the config file: ncas-energy-balance-1-software/config.ini.
This includes input/output file paths and settings for netcdf global attributes.
Comments explain various settings. To see the config file: https://github.com/ncasuk/ncas-energy-balance-1-software/blob/master/config.ini

Use the ``-h`` option on any script to see the command line arguments available.

**1. download_data:**

- Created to be set up as a cron job every 5 minutes (or another time interval). This downloads data from tables on the logger and saves to a daily csv file.
- The script does not take any command line arguments.
- The files are made in the directory specified in the config file, under ``logger_csv_path``, in a directory named after the table e.g. ``<chosen-directory>/SoilMoisture/SoilMoisture_2021-07-21.csv``
- The datalogger URL must be set in the config file e.g. serial:/dev/ttyUSB0:115200 or tcp:host-ip:port
- Edit ``logger_tables`` in the config file to change the tables downloaded. The default tables are Housekeeping, GPS_datetime, SoilTemperature, SoilMoisture, SoilHeatFlux and Radiation.

To run once:

.. code-block:: console
    
    $ cd energy_balance/scripts
    $ python download_data.py

To set up a cron job:

.. code-block:: console

    $ crontab -e 
    
Add a command, such as the one below, to this file:

.. code-block::

    */5 * * * * . /home/pi/ncas-energy-balance-1-software/venv/bin/activate && /home/pi/ncas-energy-balance-1-software/energy_balance/scripts/download_data.py >> /home/pi/campbell_data/cron.log 2>&1

This sets this script running every 5 minutes. The first file path needs to point to your virtual environment and the second to the location of the script.
The final file path points to the location at which to write a log file. This can be excluded if this is not required.


**2. download_data_by_date:**

- Intended to be used to bulk donwload data over a range of days. 
- Useful if logger has been turned off/ was down etc.
- This downloads data from tables on the logger and saves to a daily csv file.
- The files are made in the directory specified in the config file, under ``logger_csv_path``, in a directory named after the table e.g. ``<chosen-directory>/SoilMoisture/SoilMoisture_2021-07-21.csv``. 
- Can be used in conjuction with the ``download_data.py`` script.
- The datalogger URL must be set in the config file e.g. serial:/dev/ttyUSB0:115200 or tcp:host-ip:port
- The start and end dates of the days to download should be provided on the command line. A start date is required but an end date is not. If an end date is not provided, data is downloaded only for the day provided as the start date.
- If a file for a day has partial data, this script will download the rest of the data for that day, following on from the latest entry in that file.
- Edit ``logger_tables`` in the config file to change the tables downloaded. The default tables are Housekeeping, GPS_datetime, SoilTemperature, SoilMoisture, SoilHeatFlux and Radiation.

To run:

The below command will download data for 21/07/2021, 22/07/2021 and 23/07/2021 and create a csv file for each day.

.. code-block:: console
    
    $ cd energy_balance/scripts
    $ python download_data_by_date.py -s 2021-07-21 -e 2021-07-23


This next command will download data only for 21/07/2021.

.. code-block:: console
    
    $ python download_data_by_date.py -s 2021-07-21


**3. add_to_mysql:**

- This script will load the csv data for today's files, created by the `download_data` script, into my sql tables, providing the tables have already been created in the database.
- This could be set up as cron job along with the `download_data` script, to keep the tables up to date.
- Edit ``logger_tables`` and ``mysql_tables`` in the config file to change the table names. The default dictionary is: {'Housekeeping': 'housekeeping', 'GPS_datetime': 'gps', 'SoilTemperature': 'soil_temp', 'SoilMoisture': 'soil_moisture', 'SoilHeatFlux': 'soil_heat_flux', 'Radiation': 'radiation'}.
- The top level directory containing the csv files is taken from the config file (under ``logger_csv_path``), assumed to be the same as that used to create the files. (i.e. the same as that used for the ``download_data.py`` script)
- The username, password and database name should also be provided as command line arguments. See below:

.. code-block:: console
    
    $ cd energy_balance/scripts
    $ python add_to_mysql.py -u <username> -p <password> -d <database>


**4. create_files.py:**

- This script can be used to make netCDF files, that conform to the NCAS-GENERAL Data Standard, for soil and radiation data products.
- For this to work, ensure settings in the config file are filled in correctly, e.g. column names, input files, input date format
- Some of the quality control settings can be adjusted in the config file. e.g. the max/min temperature expected for Soil Temperature and the lower and upper bounds for the cleaning time of the radiation sensors.
- It takes some command line arguments to specify options for the creation of the files.
- The files are created at the ``netcdf_path`` specified in the config file.

:: 

    usage: create_files.py [-h] -s START_DATE [-e END_DATE] [-f {daily,monthly}]
                        -d {soil,radiation}

    optional arguments:
    -h, --help            show this help message and exit
    -s START_DATE, --start-date START_DATE
                            The start date to create netCDF files for. e.g.
                            '2021-07-30' when creating daily files, '2021-07' when
                            creating monthly files.
    -e END_DATE, --end-date END_DATE
                            The end date to create netCDF files for. e.g.
                            '2021-07-30' when creating daily files, '2021-07' when
                            creating monthly files. This is inclusive.
    -f {daily,monthly}, --frequency {daily,monthly}
                            The frequency for creating the netCDF files, options
                            are daily or monthly. The default is monthly.
    -d {soil,radiation}, --data-product {soil,radiation}
                            The data product to create files for.


The start date must always be provided, but an end date is not required. If an end date is not provided, files are only created for the date provided as the start date. An example of usage is:

.. code-block:: console
    
    $ cd energy_balance/scripts
    $ python create_files.py -s 2021-07 -e 2021-08 -f monthly -d soil

**5. create_qc_csvs.py:**

- This script will generate csvs for soil/radiation data that have been quality controlled according the level of quality control specified in the config file.
- The file path must be provided as a command line argument.
- Setting the level as 1, means only 'good' data is provided. This can be increased to include data from other qc flags, as described by the variables in the netcdf files. (The level chosen will include data from that level and below.)
- The quality control flags data outside operational bounds, suspect data and data taken when sensors are being cleaned.
- Some of the quality control settings can be adjusted in the config file. e.g. the max/min temperature expected for Soil Temperature and the lower and upper bounds for the cleaning time of the radiation sensors.
- These csvs can be plotted using script #6 below.

:: 


        usage: create_qc_csvs.py [-h] -s START_DATE [-e END_DATE] [-f {daily,monthly}]
                                -d {soil,radiation} -fp FILE_PATH

        optional arguments:
        -h, --help            show this help message and exit
        -s START_DATE, --start-date START_DATE
                                The start date to create netCDF files for. e.g.
                                '2021-07-30' when creating daily files, '2021-07' when
                                creating monthly files.
        -e END_DATE, --end-date END_DATE
                                The end date to create netCDF files for. e.g.
                                '2021-07-30' when creating daily files, '2021-07' when
                                creating monthly files. This is inclusive.
        -f {daily,monthly}, --frequency {daily,monthly}
                                The frequency for creating the netCDF files, options
                                are daily or monthly. The default is monthly.
        -d {soil,radiation}, --data-product {soil,radiation}
                                The data product to create files for.
        -fp FILE_PATH, --file-path FILE_PATH
                                Filename of where to write file e.g. /path/to/file.csv

.. code-block:: console
    
        $ cd energy_balance/scripts
        $ python create_qc_csvs.py -s 2021-07-30 -f daily -d radiation -fp /path/to/output/file.csv

**6. plot_csv.py:**

- This script can be used to generate plots of csv files, using matplotlib.
- The command line options allow you to specify the datetimes to plot between and which columns of the csv to plot.
- The name of the datetime column must be specified in the config file.
- If a start and/or end date are not provided, these will default to the start/end times in the csv.

:: 

    usage: plot_csv.py [-h] [-s START] [-e END] -f FILE -c COLUMNS

    optional arguments:
    -h, --help            show this help message and exit
    -s START, --start START
                            The start date/time for the plot in 'YYYY-MM-dd
                            HH:MM:SS' format. e.g. '2021-07-10 04:00'.
    -e END, --end END     The end date/time for the plot in 'YYYY-MM-dd
                            HH:MM:SS' format. e.g. '2021-07-10 16:00'.
    -fp FILE_PATH, --file-path FILE_PATH
                            The path to the csv file to plot. e.g. /path/to/file.csv
    -c COLUMNS, --columns COLUMNS
                            The columns from the csv to plot against datetime,
                            provide as comma separated list if more than one e.g. 'IR01Dn,IR01Up'.


Note that datetimes should be provided in quotations to allow them to be parsed correctly

.. code-block:: console
    
    $ cd energy_balance/scripts
    $ python plot_csv.py -s '2021-07-10 04:00' -e '2021-07-10 16:00' -f /path/to/my/file.csv -c shf_1,shf_2,shf_3



.. _scripts-api: https://ncas-energy-balance-1-software.readthedocs.io/en/latest/scripts-api.html
