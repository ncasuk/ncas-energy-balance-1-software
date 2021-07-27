.. _scripts:

=======
Scripts
=======

The scripts make use of the package PyCampbellCR1000 (on an updated fork) - this works for CR3000 loggers as well.
The documentation for this package can be found here: https://pycampbellcr1000.readthedocs.io/en/latest/

**1. download_data:**

- Created to be set up as a cron job every 5 minutes (or another time interval). This downloads data from tables on the logger and saves to a daily csv file.
- The files are made in the directory specified on the command line, in a directory named after the table e.g. ``<chosen-directory>/SoilMoisture/SoilMoisture_2021-07-21.csv``
- The datalogger URL must be provided as a command line argument e.g. serial:/dev/ttyUSB0:115200 or tcp:host-ip:port
- Edit your local script on line 34 to change the tables that are downloaded. The default tables are Housekeeping, GPS_datetime, SoilTemperature, SoilMoisture, SoilHeatFlux and Radiation.

To run once:

.. code-block:: console
    
    $ cd scripts
    $ python download_data.py serial:/dev/ttyUSB0:115200 -f /home/campbell_data

To set up a cron job:

.. code-block:: console

    $ crontab -e 
    
Add a command, such as the one below, to this file:

.. code-block::

    */5 * * * * . /home/pi/ncas-energy-balance-1-software/venv/bin/activate && /home/pi/ncas-energy-balance-1-software/scripts/download_data.py serial:/dev/ttyUSB0:115200 -f /home/campbell_data >> /home/pi/campbell_data/cron.log 2>&1

This sets this script running every 5 minutes. The first file path needs to point to your virtual environment and the second to the location of the script.
The final file path points to the location at which to write a log file. This can be excluded if this is not required.


**2. download_data_by_date:**

- Intended to be used to bulk donwload data over a range of days. 
- Useful if logger has been turned off/ was down etc.
- This downloads data from tables on the logger and saves to a daily csv file.
- The files are made in the directory specified on the command line, in a directory named after the table e.g. ``<chosen-directory>/SoilMoisture/SoilMoisture_2021-07-21.csv``. 
- If using in conjuction with the ``download_data.py`` script, the same directory should be specified
- The datalogger URL must be provided as a command line argument e.g. serial:/dev/ttyUSB0:115200 or tcp:host-ip:port
- The start and end dates of the days to download should be provided on the command line. A start date is required but an end date is not. If an end date is not provided, data is downloaded only for the day provided as the start date.
- If a file for a day has partial data, this script will download the rest of the data for that day, following on from the latest entry in that file.
- Edit your local script on line 42 to change the tables that are downloaded. The default tables are Housekeeping, GPS_datetime, SoilTemperature, SoilMoisture, SoilHeatFlux and Radiation.

To run:

The below command will download data for 21/07/2021, 22/07/2021 and 23/07/2021 and create a csv file for each day.

.. code-block:: console
    
    $ cd scripts
    $ python download_data_by_date.py serial:/dev/ttyUSB0:115200 -s 2021-07-21 -e 2021-07-23 -f /home/campbell_data


This next command will download data only for 21/07/2021.

.. code-block:: console
    
    $ python download_data_by_date.py serial:/dev/ttyUSB0:115200 -s 2021-07-21 -f /home/campbell_data


**3. add_to_mysql:**

- This script will load the csv data for today's files, created by the `download_data` script, into my sql tables, providing the tables have already been created in the database.
- This could be set up as cron job along with the `download_data` script, to keep the tables up to date.
- Line 45 is a dictionary where the keys are the name of the tables from the logger and the values are the names of your tables in mysql. This should be changed as needed.
- The default dictionary is: {'Housekeeping': 'housekeeping', 'GPS_datetime': 'gps', 'SoilTemperature': 'soil_temp', 'SoilMoisture': 'soil_moisture', 'SoilHeatFlux': 'soil_heat_flux', 'Radiation': 'radiation'}.
- The top level directory containing the csv files should be spceified on the command line. (i.e. the same as that specified for the ``download_data.py`` script)
- The username, password and database name should also be provided as command line arguments. See below:

.. code-block:: console
    
    $ cd scripts
    $ python add_to_mysql.py -u <username> -p <password> -d <database> -f /home/campbell_data



.. automodule:: scripts
    :members: