The full documentation can be found at https://ncas-energy-balance-1-software.readthedocs.io/en/latest/

This repository contains scripts for logging data from an NCAS AMOF energy balance via an Campbell Scientific CR3000 logger using python.
This replaces the need to use Microsoft Windows software for acquiring the data.

Before attempting to install this software, ensure you have Python 3.7 and git installed.
(What is Git: https://github.com/git-guides/)
(Installing Git: https://github.com/git-guides/install-git )

The software is intended to be used for soil and radiation data products, and where data is referred to, it is data relating to these data products.
It may also work with with CR1000 or other Campbell loggers but this has not been tested.

There are various components as explained briefly below:

 - The software provides capabilities for streaming data from the Campbell logger, downloading data from specific dates and producing a csv file containing this data for each day.
 - There is funcitonality to put the data from these daily csv files into a MySQL database, to allow for visualisation e.g. with grafana.
 - There is a script to create daily or monthly netCDF files that conform to the NCAS-GENERAL Data Standard from these daily csv files. As part of this process quality control is carried out on the variables, allowing quality control variables to be added to the netCDF datasets.
 - It is also possible to create csv files for soil and radiation that have had quality control applied, to allow you to view the data manually or plot via the plotting script provided.
 - A plotting script is provided to plot specified csv columns against time, provided a timestamp exists in the csv file.

With this software the process of collecting data, applying quality control, plotting and creating netCDF files should be much more straightforward.


To see which scripts are available and what they do, go to `scripts`_.

All scripts can be downloaded from the `Github repo`_.
An explanattion of using `git clone` can be found here: https://github.com/git-guides/git-clone

.. code-block:: console

    $ git clone https://github.com/ncasuk/ncas-energy-balance-1-software.git
    $ cd ncas-energy-balance-1-software

In order to use the scripts, create a virtual environment and install the package within the ncas-energy-balance-1-software repository:
The package is called ``energy_balance`` and contains the scripts and all you will need to use them.

.. code-block:: console

    $ python -m venv venv
    $ source venv/bin/activate
    $ pip install .

If you would like to be able to edit the scripts, change the final line to

.. code-block:: console

    $ pip install -e .

Creating a virtual environemnt allows you to manage the installation requirements. You will need to activate the virtual environemnt before using the scripts (`source venv/bin/activate`) after opening a new terminal window.

It is likely that you will use a Raspberry Pi to connect to the logger using a Moxa NPort either via TCP/IP or in Real COM mode. Therefore you will run the scripts on the Raspberry Pi.
If using Real COM mode the driver is installed along with raspberrypi-kernel-headers (run ``sudo apt install raspberrypi-kernel-headers``)
You will then need to map the target IP to the Real COM port - find the readme explaining how to do this at `/usr/lib/npreal2` on the pi.
You may then have to change the group and permission of the port:

.. code-block:: console

    $ sudo chown root:dialout /dev/ttyr0
    $ sudo chmod 660 /dev/ttyr0

Sometimes there can be a problem installing numpy on Raspberry Pi. The troubleshooting page for this is: https://numpy.org/devdocs/user/troubleshooting-importerror.html

The command:

.. code-block:: console

    $ sudo apt-get install libatlas-base-dev

usually works.

You also may encounter problems installing netCDF4 on RaspberryPi. The below steps should be used in the case where you get the error `ValueError: did not find HDF5 headers`.

.. code-block:: console
    
    $ pip install wheel
    $ sudo apt-get install libhdf5-dev
    $ sudo apt-get install libnetcdf-dev
    


.. _Github repo: https://github.com/ncasuk/ncas-energy-balance-1-software
.. _scripts: https://ncas-energy-balance-1-software.readthedocs.io/en/latest/scripts.html
