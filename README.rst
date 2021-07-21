Documentation can be found at https://ncas-energy-balance-1-software.readthedocs.io/en/latest/

This repository contains scripts for logging data from an energy balance tower using python.
This replaces the need to use Microsoft Windows software for acquiring the data.

To see which scripts are available and what they do, go to https://ncas-energy-balance-1-software.readthedocs.io/en/latest/scripts.html.

The scripts can be downloaded from the `Github repo`_.

.. code-block:: console

    $ git clone https://github.com/ncasuk/ncas-energy-balance-1-software.git
    $ cd ncas-energy-balance-1-software

In order to use the scripts, create a virtual environment and install the requirements:

.. code-block:: console

    $ python -m venv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt


Sometimes there can be a problem installing numpy on Raspberry Pi. The troubleshooting page for this is: https://numpy.org/devdocs/user/troubleshooting-importerror.html

The command:

.. code-block:: console

    $ sudo apt-get install libatlas-base-dev

usually works.



.. _Github repo: https://github.com/ncasuk/ncas-energy-balance-1-software
