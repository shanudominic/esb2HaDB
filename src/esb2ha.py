#!/usr/bin/env python3

import os
import re as re

from util.esbDataCsvDownloader import download_data
from util.uploadCsvDataToHaDB import update_ha_statistics_table

# Configuration
DATABASE_PATH = os.getenv('HA_DB_FILE') # Path to the SQLite DB "/homeassistant/data/home-assistant_v2.db" 
ENTITY_ID = os.getenv('HA_SENSOR')  # Replace with your entity ID sensor.esb_electricity_usage

MPRN = os.getenv('ESB_MPRN')
ESB_USERNAME = os.getenv('ESB_USERNAME')
ESB_PASSWORD = os.getenv('ESB_PASSWORD')
CSV_FILE_NAME = os.getenv('ESB_GENERATED_FILENAME')
CSV_FILE = os.getenv('ESB_DOWNLOAD_LOCATION') + CSV_FILE_NAME

# main
download_data(meter_mprn=MPRN, esb_user_name=ESB_USERNAME, esb_password=ESB_PASSWORD, download_file=CSV_FILE)
update_ha_statistics_table(CSV_FILE, DATABASE_PATH, ENTITY_ID)