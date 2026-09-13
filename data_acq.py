# data_acq.py - AquaGuard Data Acquisition Module

import sqlite3
from sqlite3 import Error
import pandas as pd
from datetime import datetime
from init import db_name, db_init

def create_connection(db_file=db_name):
    """create a database connection to the SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(f"DB Error: {e}")
    return conn

def create_table(conn, create_table_sql):
    """create a table from the sql statement"""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        conn.commit()
    except Error as e:
        print(f"Table Error: {e}")

def init_db(database):
    """Initialize SQLite tables for devices and sensor data"""
    tables = [
        """CREATE TABLE IF NOT EXISTS `data` (
            `name` TEXT NOT NULL,
            `timestamp` TEXT NOT NULL,
            `value` TEXT NOT NULL
        );""",
        """CREATE TABLE IF NOT EXISTS `iot_devices` (
            `sys_id` INTEGER PRIMARY KEY AUTOINCREMENT,
            `name` TEXT NOT NULL UNIQUE,
            `status` TEXT,
            `units` TEXT,
            `last_updated` TEXT NOT NULL,
            `dev_type` TEXT NOT NULL,
            `dev_pub_topic` TEXT NOT NULL,
            `dev_sub_topic` TEXT NOT NULL
        );"""
    ]
    conn = create_connection(database)
    if conn is not None:
        for table in tables:
            create_table(conn, table)
        conn.close()
    else:
        print("Error! Cannot create the database connection.")

def timestamp():
    return str(datetime.now()).split('.')[0]

def add_IOT_data(name, updated, value):
    """Add new sensor reading to data table"""
    sql = ''' INSERT INTO data(name, timestamp, value) VALUES(?,?,?) '''
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute(sql, [name, updated, value])
        conn.commit()
        conn.close()

def filter_by_date(table_name, start_date, end_date, meter):
    """Filter records by date and device name"""
    conn = create_connection()
    rows = []
    if conn is not None:
        cur = conn.cursor()
        query = f"SELECT * FROM {table_name} WHERE `name` LIKE ? AND timestamp BETWEEN ? AND ?"
        cur.execute(query, (meter, start_date, end_date))
        rows = cur.fetchall()
        conn.close()
    return rows

if __name__ == '__main__':
    if db_init:
        init_db(db_name)
        print("Database and tables initialized successfully!")