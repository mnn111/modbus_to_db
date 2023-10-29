# import sqlite3
# import time
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from datetime import datetime
# from modbus_sql import tables_dict

# # Function to fetch data in batches
# def fetch_data_in_batches(session, batch_size):
#     offset = 0
#     while True:
#         data = session.query(CustomDeviceTable).limit(batch_size).offset(offset).all()
#         if not data:
#             break
#         offset += batch_size
#         yield data

# # Connect to SQLite and PostgresSQL databases
# try:
#     sqlite_db_path = "/home/wzero/modbus/mydatabase.db"
#     sqlite_engine = create_engine(f"sqlite:///{sqlite_db_path}", echo=True)
#     print("SQLite database connected successfully.")
#     Sqlite_Session = sessionmaker(bind=sqlite_engine)
#     sqlite_session = Sqlite_Session()

#     PostgresSQL_engine = create_engine('postgresql+psycopg2://postgres:postgres@192.168.1.18:5432/test1')
#     print("PostgresSQL database connected successfully.")
#     Session = sessionmaker(bind=PostgresSQL_engine)
#     PostgresSQL_session = Session()

#     interval = 0.5

#     while True:
#         # Fetch data from SQLite in batches of 1000
#         for batch_data in fetch_data_in_batches(sqlite_session, 1000):
#             # Insert data into PostgresSQL using SQLAlchemy
#             for row in batch_data:
#                 PostgresSQL_data = CustomDeviceTable(timestamp=row.timestamp, reg_no=row.reg_no, value=row.value)
#                 PostgresSQL_session.add(PostgresSQL_data)

#             # Commit the changes to PostgresSQL
#             PostgresSQL_session.commit()

#             # Delete successfully transferred data from SQLite
#             for row in batch_data:
#                 sqlite_session.delete(row)
#             sqlite_session.commit()

#         # Sleep for the specified interval
#         time.sleep(interval)

# except KeyboardInterrupt:
#     sqlite_session.close()
#     PostgresSQL_session.close()
# except sqlite3.Error as e:
#     print("SQLite database connection error:", e)
# except Exception as e:
#     print("Error:", e)

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#  In this code we try to Read all Sqlite data and Write into Postgresql table Dynamically
# import time
# from sqlalchemy import create_engine, Column, Integer, DateTime, Float, text
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.exc import IntegrityError
# from sqlalchemy.orm.exc import NoResultFound
# import os
# import json

# # Import your dynamic model creation function from the 'database.models_1' module
# from database.models_1 import create_dynamic_model

# # Initialize the 'config' variable to None
# config = None

# # Read configuration from JSON file
# config_file_path = '/home/wzero/modbus/w_script.json'

# # Check if the config file exists and load it
# if os.path.isfile(config_file_path):
#     with open(config_file_path, 'r') as config_file:
#         config = json.load(config_file)
# else:
#     print(f"Error: '{config_file_path}' not found")
#     # You may want to handle this situation, such as providing default values or exiting the script.

# # Define paths and create SQLite database and session
# sqlite_db_path = "/home/wzero/modbus/mydatabase.db"
# sqlite_engine = create_engine(f"sqlite:///{sqlite_db_path}", echo=True)
# print("SQLite database connected successfully.")
# Sqlite_Session = sessionmaker(bind=sqlite_engine)
# sqlite_session = Sqlite_Session()

# # Create a PostgreSQL database connection and session
# PostgresSQL_engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost/test1')
# print("PostgresSQL database connected successfully.")
# Session = sessionmaker(bind=PostgresSQL_engine)
# PostgresSQL_session = Session()

# # Define the data transfer interval
# interval = 0.5

# # Create a dictionary to store dynamic table models
# tables_dict = {}

# # Check if the 'config' variable is defined
# if config is not None:
#     com_port = config["modbus"]["port"]
#     devices = config["devices"]

#     for device in devices:
#         hostname = os.uname()[1]
#         device_name = device.get("edge_device_name", "")
#         slave_id = device.get("slave_id", "")
#         table_name = f"{hostname}_{slave_id}_{device_name}"

#         # Extract register information from the device configuration
#         register_dict = device["register"]
#         column_names = []
#         for reg in register_dict:
#             column_names.append(register_dict[reg])
#         print(column_names)

#         # Create a dynamic model for the table and create the table in the PostgreSQL database
#         model = create_dynamic_model(table_name, column_names)
#         model.__table__.create(PostgresSQL_engine, checkfirst=True)

#         tables_dict[device_name] = model

#         try:
#             while True:
#                 # Fetch data from SQLite in batches of 1000
#                 batch_data = sqlite_session.query(model).limit(1000).all()

#                 # Insert data into PostgreSQL using SQLAlchemy
#                 for row in batch_data:
#                     try:
#                         model = tables_dict[device_name]
#                         postgres_data = model()
#                         for col_name in column_names:
#                             setattr(postgres_data, col_name, getattr(row, col_name))
#                         postgres_data.timestamp = row.timestamp
#                         PostgresSQL_session.add(postgres_data)
#                         PostgresSQL_session.commit()
#                     except IntegrityError as e:
#                         # Handle duplicates or other errors as needed
#                         PostgresSQL_session.rollback()
                        
#                 # Delete successfully transferred data from SQLite
#                 for row in batch_data:
#                     try:
#                         sqlite_session.delete(row)
#                         sqlite_session.commit()
#                     except NoResultFound as e:
#                         # Handle if the row was already deleted or other errors as needed
#                         sqlite_session.rollback()

#                 # Sleep for the specified interval
#                 time.sleep(interval)

#         except KeyboardInterrupt:
#             # Close database sessions on keyboard interrupt
#             sqlite_session.close()
#             PostgresSQL_session.close()
#         except Exception as e:
#             print("Error:", e)
# else:
#     # Handle the situation where the 'config' variable is not defined (e.g., provide default values or exit).
#     pass

# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# In This code We Read all data from sqlite and write into postgresql but in this code we add functionality to update last index number table for  each table
# Import necessary libraries
import time
import json
import os
import socket
import threading
from sqlalchemy import create_engine, Column, Integer, DateTime, String, text, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from database.models_1 import create_dynamic_model
from db import get_sqlite_session, get_postgres_session
from datetime import datetime, timedelta

# Initialize 'config' variable to None
config = None

# Read configuration data from a JSON file
config_file_path = '/home/wzero/Public/modbus/w_script.json'

# Check if the configuration file exists
if os.path.isfile(config_file_path):
    with open(config_file_path, 'r') as config_file:
        config = json.load(config_file)
else:
    print(f"Error: '{config_file_path}' not found")
    # Handle the case where the configuration file is missing (e.g., provide default values or exit).

# Define paths and create a SQLite database and session
sqlite_db_path = "/home/wzero/Public/modbus/mydatabase.db"
sqlite_engine = create_engine(f"sqlite:///{sqlite_db_path}", echo=True)
print("SQLite database connected successfully")

# Create a PostgreSQL database connection and session
PostgresSQL_engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost/test1')
print("PostgresSQL database connected successfully")

# Define the data transfer interval
interval = 0.5

# Define the data retention period in minutes
data_retention_period_minutes = 1

# Check if the 'config' variable is defined
if config is not None:
    com_port = config["modbus"]["port"]
    devices = config["devices"]

    # Define a dictionary to store the last_sync_index for each device
    device_last_sync_index = {}
    device_models = {}  # Dictionary to store dynamic models

    # Create a PostgreSQL session to manage the 'last_sync_index' table
    LastSyncIndexBase = declarative_base()

    class LastSyncIndex(LastSyncIndexBase):
        __tablename__ = 'last_sync_index'
        id = Column(Integer, primary_key=True, autoincrement=True)
        device_name = Column(String, unique=True)
        last_index = Column(Integer)
        last_deleted_at = Column(DateTime, server_default=func.now())  # Store the last time data was deleted
        created_at = Column(DateTime, server_default=func.now())
        updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    LastSyncIndexBase.metadata.create_all(sqlite_engine)

    # Create models and tables for each device during initialization
    for device in devices:
        hostname = socket.gethostname()
        device_name = device.get("edge_device_name", "")
        slave_id = device.get("slave_id", "")
        table_name = f"{hostname}_{slave_id}_{device_name}"
        column_names = list(device["register"].values())

        # Create a dynamic database model for the device data
        model = create_dynamic_model(table_name, column_names)
        model.__table__.create(PostgresSQL_engine, checkfirst=True)

        device_models[device_name] = model

    # Function to synchronize data for a single device
    def synchronize_data(device):
        # Create sessions within the thread
        sqlite_session = get_sqlite_session()
        PostgresSQL_session = get_postgres_session()

        # Get device information
        hostname = socket.gethostname()
        device_name = device.get("edge_device_name", "")
        model = device_models.get(device_name)
        
        if model is not None:
            try:
                while True:
                    # Query data from SQLite database for synchronization
                    last_sync_index_record = sqlite_session.query(LastSyncIndex).filter_by(device_name=device_name).first()

                    if last_sync_index_record:
                        last_sync_index = last_sync_index_record.last_index
                    else:
                        last_sync_index = 0

                    # Query data that needs to be synchronized
                    batch_data = sqlite_session.query(model).filter(model.id > last_sync_index).limit(1000).all()

                    if batch_data:
                        for row in batch_data:
                            try:
                                # Create a corresponding record in the PostgreSQL database
                                postgres_data = model()
                                for col_name in column_names:
                                    setattr(postgres_data, col_name, getattr(row, col_name))
                                postgres_data.timestamp = row.timestamp
                                PostgresSQL_session.add(postgres_data)
                            except IntegrityError as e:
                                PostgresSQL_session.rollback()

                        # Commit the changes to the PostgreSQL database
                        PostgresSQL_session.commit()
                        last_sync_index = batch_data[-1].id

                        # Update the last_sync_index record
                        if last_sync_index_record:
                            last_sync_index_record.last_index = last_sync_index
                        else:
                            last_sync_index_record = LastSyncIndex(device_name=device_name, last_index=last_sync_index)
                            sqlite_session.add(last_sync_index_record)

                        # Commit the SQLite session
                        sqlite_session.commit()
                        
                        # Delete data older than data_retention_period_minutes
                        current_time = datetime.utcnow()
                        data_retention_period = current_time - timedelta(minutes=data_retention_period_minutes)
                        data_delete_frequency = current_time - timedelta(minutes=5)

                        if data_delete_frequency > last_sync_index_record.last_deleted_at:
                            all_delete_data = sqlite_session.query(model).filter(model.timestamp < data_retention_period).all()

                            for del_data in all_delete_data:
                                sqlite_session.delete(del_data)

                            last_sync_index_record.last_deleted_at = current_time  # Update the last_deleted_at timestamp
                            sqlite_session.commit()


                    time.sleep(interval)
            except KeyboardInterrupt:
                # Close database sessions on keyboard interrupt
                sqlite_session.close()
                PostgresSQL_session.close()
            except Exception as e:
                print("Error:", e)

    # Create a separate thread for each device
    for device in devices:
        thread = threading.Thread(target=synchronize_data, args=(device,))
        thread.daemon = True
        thread.start()

    try:
        while True:
            # Main thread continues to run
            time.sleep(60)  # Sleep for one minute
    except KeyboardInterrupt:
        pass
else:
    # Handle the situation where the 'config' variable is not defined (e.g., provide default values or exit).
    pass
