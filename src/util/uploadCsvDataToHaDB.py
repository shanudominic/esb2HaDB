#!/usr/bin/env python3

from datetime import datetime
import os
import sqlite3
import time
import re as re
import csv

from .logger import getLogger

log = getLogger(os.path.basename(__file__))

# Convert timestamp from DD-MM-YYYY HH:MM to epoch
def timestamp_to_epoch(timestamp):
    dt = datetime.strptime(timestamp, "%d-%m-%Y %H:%M")
    return float(time.mktime(dt.timetuple()))

# Parse CSV and return data as list of tuples
def parse_csv(file_path):
    with open(file_path, "r") as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # Skip header if present
        data = [(timestamp_to_epoch(row[4]), float(row[2]), 0) for row in reader]

    return data

# populate timestamps to CSV inmemory with timestamps till now stepping 30 mins and dat from last entry till now as 0
def populate_data_till_now(data):
    csv_last_epoch = data[0][0]
    # Current epoch time
    end_epoch = time.time()
    # Step size in seconds (30 minutes = 1800 seconds)
    step = 30 * 60

    # invert data so latest becomes at bottom of list, so we can append new entries
    data = data[::-1]

    # Generate epoch times
    current_epoch = csv_last_epoch
    while current_epoch <= end_epoch:
        if current_epoch != csv_last_epoch:
            data.append([current_epoch, 0, 0])
        current_epoch += step

    # invert data so latest becomes at top of list
    data = data[::-1]

    return data

# calculate sum for each field within csv data
def add_sum(data):
    sum = float(0)
    for i in range(len(data)):
        temp_list = list(data[i])
        value = temp_list[1]
        if value is None:
            sum += 0
        else:
            sum += value
        temp_list[2] = sum
        data[i] = tuple(temp_list)

    return data[::-1]

# Main function
def update_ha_statistics_table(csv_file, db_path, entity_id):
    print("################################################################################")

    data = parse_csv(csv_file)
    data = populate_data_till_now(data=data)
    data = add_sum(data=data[::-1])
   
    log.info("Parsed CSV data and got %s entries", len(data))

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Get metadata_id for the entity
        cursor.execute(
            "SELECT id FROM statistics_meta WHERE statistic_id = ?",
            (entity_id,)
        )
        metadata = cursor.fetchone()

        if not metadata:
            log.error("Entity ID '%s' not found in statistics_meta.", entity_id)
            raise SystemExit(0)
        
        metadata_id = int(metadata[0])

        log.debug("MetadataID for entity: %s is %s", (entity_id, metadata_id))
        
        log.info("Delete all statistics entry from table")
        # Delete existing entries for the entity
        cursor.execute(
            "DELETE FROM statistics WHERE metadata_id = ?",
            (metadata_id,)
        )
        conn.commit()
        
        # Insert new data
        log.info("Insert new CSV data for entity: %s to statistics table", entity_id)
        for start_ts, state, sum in data[::-1]:
            cursor.execute(
                """
                INSERT INTO statistics (created, created_ts, metadata_id, start, start_ts, mean, min, max, last_reset, last_reset_ts, state, sum)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (None, start_ts, metadata_id, None, start_ts, None, None, None, None, None, state, sum)
            )

        conn.commit()
        log.info("Updated Statistics table for entity: %s", entity_id)
        
    print("################################################################################")
