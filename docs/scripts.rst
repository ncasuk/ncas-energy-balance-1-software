.. _scripts:

=======
Scripts
=======

The scripts make use of the package PyCampbellCR1000 (on an updated fork) - this works for CR3000 loggers as well.
The documentation for this package can be found here: https://pycampbellcr1000.readthedocs.io/en/latest/

1. log_data_tables:

- Created to be set up as a cron job every 5 minutes (or another time interval). This downloads data from tables on the logger and saves to a daily csv file.
- The datalogger URL must be provided as a command line argument e.g. serial:/dev/ttyUSB0:115200 or tcp:host-ip:port
- Edit your local script on line 34 to change the tables that are downloaded.

To run once:
.. code-block:: console

    $ cd scripts
    $ python log_data_tables.py serial:/dev/ttyUSB0:115200

To set up a cron job:

    $ crontab -e 
    
Add a command, such as the one below, to this file:

``*/5 * * * * . /home/pi/ncas-energy-balance-1-software/venv/bin/activate && /home/pi/ncas-energy-balance-1-software/scripts/log_data_tables.py serial:/dev/ttyUSB0:115200 >> /home/pi/campbell_data/cron.log 2>&1``

This sets this script running every 5 minutes. The first file path needs to point to your virtual environment and the second to the location of the script.
The final file path points to the location at which to write a log file. This can be excluded if this is not required.