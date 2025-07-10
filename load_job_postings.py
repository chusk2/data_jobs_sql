import pandas as pd
from sqlalchemy import create_engine
import os

# --- Database Connection Details (Update with your credentials) ---
DB_USER = "mysqluser"
DB_PASSWORD = "hbmHq7015$mysqluser"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "data_jobs"

def get_db_engine():
    """Creates and returns a SQLAlchemy database engine."""
    connection_string = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    try:
        engine = create_engine(connection_string)
        # Test connection
        with engine.connect() as connection:
            print(f"Successfully connected to the '{DB_NAME}' database.")
        return engine
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        print("Please ensure your database server is running and credentials are correct.")
        return None
    
def load_table(engine, table_name, csv_file):
    """Loads data from a CSV file into a database table."""
    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found at '{csv_file}'. Skipping table '{table_name}'.")
        return

    try:
        df = pd.read_csv(csv_file)
        # Rename columns to match the database schema
        # if column_map:
        #     df.rename(columns=column_map, inplace=True)

        print(f"Loading data into '{table_name}' table...")
        df.to_sql(table_name, con=engine, if_exists='append', index=False)
        print(f"Successfully loaded {len(df):,} rows into '{table_name}'.\n\n")
    except Exception as e:
        print(f"Error loading data into '{table_name}': {e}\n\n")

engine = get_db_engine()

load_table(engine, 'job_postings', 'job_postings.csv')