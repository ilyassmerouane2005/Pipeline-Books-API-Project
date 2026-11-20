from src.extractor import extract_data
from src.cleaner import clean_data
from src.cleaner_duckdb import clean_data_duckdb
import polars as pl
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():

    # Extract data from the API
    try:
        df = extract_data()
        logging.info('Data extracted successfully.')
    except Exception as e:
        logging.error(f'Error extracting data: {e}')
    # Clean the data
    try:
        cleaned_df = clean_data(df)
        logging.info('Data cleaned successfully using Polars.')
    except Exception as e:
        logging.error(f'Error cleaning data with Polars: {e}')

    # Save the cleaned data to a Parquet file
    try:
        cleaned_df.write_parquet("data/clean/books.parquet")
        logging.info('Cleaned data saved to Parquet file successfully.')
    except Exception as e:
        logging.error(f'Error saving cleaned data to Parquet: {e}')

    # Save the cleaned data to a DuckDB database
    try:
        cleaned_df_duckdb = clean_data_duckdb(df)
        cleaned_df_duckdb.write_database('books' , connection = 'sqlite:///data/clean/books.db' , engine = 'adbc' , if_table_exists = 'replace')
        logging.info('Cleaned data saved to DuckDB database successfully.')
    except Exception as e:
        logging.error(f'Error cleaning data with DuckDB or saving to database: {e}')

if __name__ == "__main__":
    main()