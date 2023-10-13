import json
import os
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData
from database.sql_models import create_dynamic_model
# Read the configuration from the JSON file
config_file_path = '/home/wzero/modbus/w_script.json'
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

# Get the hostname
hostname = os.uname()[1]

devices = config.get("devices", [])
if devices:
    # Establish a connection to the PostgreSQL server using SQLAlchemy
    postgres_engine = create_engine(
        f"postgresql+psycopg2://{config['remote_db_connection']['user']}:{config['remote_db_connection']['password']}@{config['remote_db_connection']['host']}:{config['remote_db_connection']['port']}/{config['remote_db_connection']['database']}",
        pool_recycle=3600,
        echo=True,
    )

    # Establish a connection to the SQLite database using SQLAlchemy
    # Replace the path with the actual SQLite database file path
    sqlite_db_path = '/home/wzero/modbus/mydatabase.db'  # Update this path
    sqlite_engine = create_engine(f'sqlite:///{sqlite_db_path}', echo=True)

    # Define a declarative base for your tables

    # Base = declarative_base()

    for device in config["devices"]:
        device_name = device.get("edge_device_name", "")
        slave_id = device.get("slave_id", "")
        table_name = f"{hostname}_{slave_id}_{device_name}"

        register_dict = device["register"]
        column_names = []
        for reg in register_dict :
            column_names.append(register_dict[reg])
        print(column_names)

        model = create_dynamic_model(table_name, column_names)
        
        model.__table__.create(sqlite_engine, checkfirst = True)
        model.__table__.create(postgres_engine, checkfirst = True)

        record = model()

        
        # # Define your custom table columns
        # columns = [
        #     Column('id', Integer, primary_key=True, autoincrement=True),
        #     Column('timestamp', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        # ]

        # # Add columns dynamically based on the 'register' dictionary in the configuration
        # for col_name in device.get("register", {}).values():
        #     columns.append(Column(col_name, Integer))

        #     # Add columns for keys based on the 'keys' dictionary in the configuration
        # for key, value in device.get("keys", {}).items():
        #     columns.append(Column(key, String, default=value))

        # metadata = MetaData()
        # table = type(table_name, (Base,), {'__tablename__': table_name, '__table_args__': {'extend_existing': True}, **{column.name: column for column in columns}})

        # # Create the table in SQLite
        # table.metadata.create_all(sqlite_engine)
        # print(f"Table '{table_name}' has been created in SQLite for device '{device_name}'.")

        # # Create the table in PostgreSQL
        # table.metadata.create_all(postgres_engine)
        # print(f"Table '{table_name}' has been created in PostgreSQL for device '{device_name}'.")
        
    # Close the database engine connections
    # postgres_engine.dispose()
    # sqlite_engine.dispose()
else:
    print("No device configurations found in the JSON file.")

# import json
# import os
# from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, text
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.exc import SQLAlchemyError

# # Read the configuration from the JSON file
# config_file_path = '/home/wzero/modbus/w_script.json'
# with open(config_file_path, 'r') as config_file:
#     config = json.load(config_file)


# # Dynamic table name
# hostname = os.uname()[1]

# devices = config.get("devices", [])
# found_device = None

# if device_config:
#     name = device_config.get("edge_device_name", "")
#     slave_id = device_config.get("slave_id", "")
#     table_name = f"{hostname}_{slave_id}_{name}"

# else:
#     print("Device configuration not found in the JSON file.")
# # name = selected_device["edge_device_name"]
# # slave_id = selected_device["slave_id"]
# # table_name = f"{hostname}_{slave_id}_{name}"



# # Establish a connection to the PostgreSQL server using SQLAlchemy
# postgres_engine = create_engine(
#     f"postgresql+psycopg2://{config['remote_db_connection']['user']}:{config['remote_db_connection']['password']}@{config['remote_db_connection']['host']}:{config['remote_db_connection']['port']}/{config['remote_db_connection']['database']}",
#     pool_recycle=3600,  # Optional: Configuring connection pooling
#     echo=True,  # Optional: Enable SQLAlchemy query echo for debugging
# )

# # Establish a connection to the SQLite database using SQLAlchemy
# # Replace the path with the actual SQLite database file path
# sqlite_db_path = '/home/wzero/modbus/mydatabase.db'  # Update this path
# sqlite_engine = create_engine(f'sqlite:///{sqlite_db_path}', echo=True)

# # Define a declarative base for your tables
# Base = declarative_base()

# # Define the DeviceMetadata table
# class DeviceMetadata(Base):
#     __tablename__ = 'device_metadata'
#     id = Column(Integer, primary_key=True)
#     device_name = Column(String, unique=True)

# # Define your custom table for the device
# class CustomDeviceTable(Base):
#     __tablename__ = table_name
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     timestamp = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
#     reg_no = Column(Integer)
#     value = Column(Integer)
#     # reg_no2 = 

# # Create the tables in PostgreSQL
# Base.metadata.create_all(postgres_engine)
# print(f"Table '{table_name}' has been created in PostgreSQL for device '{device_name}'.")

# # Create the tables in SQLite
# Base.metadata.create_all(sqlite_engine)
# print(f"Table '{table_name}' has been created in SQLite for device '{device_name}'.")

# # Close the database engine connections
# postgres_engine.dispose()
# sqlite_engine.dispose()




# # import json
# # from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, text
# # from sqlalchemy.ext.declarative import declarative_base
# # from sqlalchemy.orm import sessionmaker
# # from sqlalchemy.exc import SQLAlchemyError
# # import sqlite3

# # # Read the configuration from the JSON file
# # config_file_path = '/home/wzero/modbus/w_script.json'
# # with open(config_file_path, 'r') as config_file:
# #     config = json.load(config_file)

# # # Dynamic table name
# # hostname = config['host']
# # slave_id = "W01"
# # device_name = input("Enter the new device name: ")
# # table_name = f"{hostname}_{slave_id}_{device_name}"

# # # Establish a connection to the SQLite database
# # sqlite_engine = create_engine('sqlite:///mydata.db', echo=True)  # Use your SQLite database file name

# # # Create a connection to the PostgreSQL server using SQLAlchemy
# # pg_engine = create_engine(
# #     f"postgresql+psycopg2://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}",
# #     pool_recycle=3600,  # Optional: Configuring connection pooling
# #     echo=True,  # Optional: Enable SQLAlchemy query echo for debugging
# # )

# # # Define a declarative base for your tables
# # Base = declarative_base()

# # # Define the SQLite custom table for the device
# # class SQLiteCustomDeviceTable(Base):
# #     __tablename__ = f'sqlite_{table_name}'
# #     id = Column(Integer, primary_key=True, autoincrement=True)
# #     timestamp = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
# #     reg_no = Column(Integer)
# #     value = Column(Integer)

# # # Define the PostgreSQL custom table for the device
# # class PostgresCustomDeviceTable(Base):
# #     __tablename__ = f'postgres_{table_name}'
# #     id = Column(Integer, primary_key=True, autoincrement=True)
# #     timestamp = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
# #     reg_no = Column(Integer)
# #     value = Column(Integer)

# # # Create the tables if they don't exist (for both SQLite and PostgreSQL)
# # Base.metadata.create_all(sqlite_engine)
# # Base.metadata.create_all(pg_engine)
# # print(f"Tables for device '{device_name}' have been created in SQLite and PostgreSQL.")

# # # Create a SQLite session
# # SQLiteSession = sessionmaker(bind=sqlite_engine)
# # sqlite_session = SQLiteSession()

# # # Create a PostgreSQL session
# # PGSession = sessionmaker(bind=pg_engine)
# # pg_session = PGSession()

# # try:
# #     # Insert data into SQLite
# #     sqlite_data = SQLiteCustomDeviceTable(reg_no=1, value=123)
# #     sqlite_session.add(sqlite_data)
# #     sqlite_session.commit()
# #     print("Data written to SQLite")

# #     # Insert data into PostgreSQL
# #     pg_data = PostgresCustomDeviceTable(reg_no=1, value=123)
# #     pg_session.add(pg_data)
# #     pg_session.commit()
# #     print("Data written to PostgreSQL")
# # except SQLAlchemyError as e:
# #     print(f"Data write to database failed: {e}")
# #     sqlite_session.rollback()
# #     pg_session.rollback()
# # finally:
# #     sqlite_session.close()
# #     pg_session.close()

# # # Close the database engine connections
# # sqlite_engine.dispose()
# # pg_engine.dispose()
