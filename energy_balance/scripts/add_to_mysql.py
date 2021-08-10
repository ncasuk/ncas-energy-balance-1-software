#!/usr/bin/env python

__author__ = 'Elle Smith'
__date__ = '22  Jul 2021'
__contact__ = 'eleanor.smith@stfc.ac.uk'

import os
from datetime import datetime
import mysql.connector
import argparse
import subprocess

def arg_parse():
    parser = argparse.ArgumentParser()

    parser.add_argument("-u",
        "--user",
        type=str,
        required=True,
        help="User for mysql database")

    parser.add_argument("-p",
        "--password",
        type=str,
        required=True,
        help="Password for mysql database")

    parser.add_argument("-d",
        "--database",
        type=str,
        required=True,
        help="Database name")

    parser.add_argument("-f",
        "--file-path",
        type=str,
        required=True,
        help="Path of directory containing the csv files.")

    return parser.parse_args()



def insert_into_tables(user, password, database, dir_path):
    """
    Gets data from the csv files found in the specified directory path and inserts it into MySQL tables.
    The MySQL tables must have been created proir to running this.
    The default names used to map the logger tables to MySQL tables are:
    {'Housekeeping': 'housekeeping', 'GPS_datetime': 'gps', 'SoilTemperature': 'soil_temp', 'SoilMoisture': 'soil_moisture', 'SoilHeatFlux': 'soil_heat_flux', 'Radiation': 'radiation'}
    
    :param user: (str) The username for connecting to MySQL.
    :param password: (str) The password for connecting to MySQL.
    :param database: (str) The names of the database in which the tables exist.
    :param dir_path: (str) The path to the top level directory in which the csv files and folders were created.
    :returns: None
    """
    # Connect to server
    cnx = mysql.connector.connect(user=user, password=user, database=user, allow_local_infile=True)

    # Get a cursor
    cur = cnx.cursor()

    tables = {'Housekeeping': 'housekeeping', 'GPS_datetime': 'gps', 'SoilTemperature': 'soil_temp', 'SoilMoisture': 'soil_moisture', 'SoilHeatFlux': 'soil_heat_flux', 'Radiation': 'radiation'}
    date = datetime.utcnow().strftime("%Y-%m-%d")

    for table, name in tables.items():
        datadir = os.path.join(dir_path, table)
        latestfile = os.path.join(datadir, f"{table}_{date}.csv")
        tempfile = os.path.join(datadir, "temp.csv")

        # remove header and save as temp file
        cmd = f"sed '1d' {latestfile} > {tempfile}"
        subprocess.call(cmd, shell=True)

        # Execute a query
        cmd = f"LOAD DATA LOCAL INFILE '{tempfile}' INTO TABLE {name} COLUMNS TERMINATED BY ',' ;"
        cur.execute(cmd)

        # commit the change
        cnx.commit()

        # remove temp file
        os.remove(tempfile)

    # close the connection
    cnx.close()

def main():
    args = arg_parse()

    user = args.user
    password = args.password
    database = args.database
    dir_path = args.file_path

    insert_into_tables(user, password, database, dir_path)

if __name__ == '__main__':
    main()