import pandas as pd
from sqlalchemy import create_engine
import os

# =================================================================
#  Python Script to Load Normalized Job Data into MySQL Database
# =================================================================

# --- Database Connection Details (Update with your credentials) ---
DB_USER = "your_username"
DB_PASSWORD = "your_password"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "data_jobs"

# --- File Paths (assumes CSVs are in the same directory as the script) ---
CSV_FILES = {
    # Dimension Tables
    'companies': 'companies.csv',
    'countries': 'countries.csv',
    'locations': 'locations.csv',
    'job_portals': 'job_via.csv',
    'job_schedules': 'job_schedules.csv',
    'skills': 'job_skills.csv',
    'job_titles': 'job_titles.csv',
    # Fact Table
    'job_postings': 'processed_jobs.csv'
}

# --- Column Mappings (from CSV to Database) ---
# Maps the column names in your CSV files to the column names in the database tables.
COLUMN_MAPPINGS = {
    'companies': {'company': 'company_name'},
    'countries': {'country': 'country_name'},
    'locations': {'location': 'location_name'},
    'job_portals': {'job_via_id': 'portal_id', 'job_via': 'portal_name'},
    'job_schedules': {'schedule': 'schedule_type'},
    'skills': {'skill': 'skill_name'},
    'job_titles': {'job_title_name': 'job_title_name'}, # Already correct from notebook fix
    'job_postings': {
        'job_title': 'job_title_full',
        'job_via': 'portal_id',
        'job_schedule_type': 'schedule_id',
        'job_country': 'job_country_id',
        'company_name': 'company_id',
        'job_skills': 'skill_id',
        'job_title_short': 'job_title_id',
        'job_location': 'job_location_id',
        'search_location': 'search_location_id'
    }
}

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

def load_table(engine, table_name, csv_file, column_map):
    """Loads data from a CSV file into a database table."""
    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found at '{csv_file}'. Skipping table '{table_name}'.")
        return

    try:
        df = pd.read_csv(csv_file)
        # Rename columns to match the database schema
        if column_map:
            df.rename(columns=column_map, inplace=True)

        print(f"Loading data into '{table_name}' table...")
        df.to_sql(table_name, con=engine, if_exists='append', index=False)
        print(f"Successfully loaded {len(df):,} rows into '{table_name}'.")
    except Exception as e:
        print(f"Error loading data into '{table_name}': {e}")

def main():
    """Main function to orchestrate the data loading process."""
    engine = get_db_engine()
    if not engine:
        return

    # Load dimension tables first to satisfy foreign key constraints
    dimension_tables = [
        'companies', 'countries', 'locations', 'job_portals',
        'job_schedules', 'skills', 'job_titles'
    ]
    for table in dimension_tables:
        load_table(engine, table, CSV_FILES[table], COLUMN_MAPPINGS.get(table))

    # Load the fact table last
    load_table(engine, 'job_postings', CSV_FILES['job_postings'], COLUMN_MAPPINGS.get('job_postings'))

    print("\nData loading process complete.")

if __name__ == "__main__":
    main()

