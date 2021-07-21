.. _scripts:

=======
Scripts
=======

The scripts make use of the package PyCampbellCR1000 (on an updated fork) - this works for CR3000 loggers as well.
The documentation for this package can be found here: https://pycampbellcr1000.readthedocs.io/en/latest/

1. logging:

- Created to be set up as a cron job every 5 minutes (or another time interval). This downloads data from tables on the logger and saves to a daily csv file.
- The datalogger URL must be provided as a command line argument e.g. serial:/dev/ttyUSB0:115200 or tcp:host-ip:port
- Edit your local script on line 34 to change the tables that are downloaded.

.. code-block:: console

    $ python scripts/logging.py serial:/dev/ttyUSB0:115200