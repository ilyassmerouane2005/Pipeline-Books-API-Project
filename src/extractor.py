import requests 
import json
import polars as pl

def extract_data(url = 'https://gutendex.com/books'): 
    """"
    this function extracts data from the given URL and returns it as a Polars DataFrame.
    """
    books = []

    for page in range(1 , 5):
        response = requests.get(url, params={'page': page})
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        books.extend(data['results'])

    return pl.DataFrame(books , infer_schema_length=None).select([
        pl.col('id'),
        pl.col('title'),
        pl.col('summaries').list.first().alias('summary'),
        pl.col('languages').list.first(),
        pl.col('download_count'),
        pl.col('authors').list.first().struct.field('name').alias('author_name'),
    ])