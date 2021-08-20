.. energy-balance-software documentation master file, created by
   sphinx-quickstart on Mon Jul 19 16:02:05 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to energy-balance-software's documentation!
===================================================

This software is intended to be used for logging data from an NCAS AMOF energy balance tower via an Campbell Scientific CR3000 logger using python.
The software is intended to be used for soil and radiation data products, and where data is referred to, it is data relating to these data products.
It may also work with with CR1000 or other Campbell loggers but this has not been tested.

There are various components as explained briefly below:

 - The software provides capabilities for streaming data from the Campbell logger, downloading data from specific dates and producing a csv file containing this data for each day.
 - There is functionality to put the data from these daily csv files into a MySQL database, to allow for visualization e.g. with Grafana.
 - There is a script to create daily or monthly netCDF files that conform to the NCAS-GENERAL Data Standard from these daily csv files. As part of this process, quality control is carried out on the variables, and quality control variables are added to the netCDF datasets.
 - It is also possible to create csv files for soil and radiation that have had quality control applied, to allow you to view the data manually or plot via the plotting script provided.
 - A plotting script is provided to plot specified csv columns against time, provided a timestamp exists in the csv file.

 With this software, the process of collecting data, applying quality control, plotting and creating netCDF files should be much more straightforward.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   readme
   scripts
   config
   quality_control
   api



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
