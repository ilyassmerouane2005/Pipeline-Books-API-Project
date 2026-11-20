import polars as pl 

def clean_data(df: pl.DataFrame) -> pl.DataFrame:
    """
    this function cleans the data coming from the api and returns a cleaned Polars DataFrame.
    for the column id : we will drop the duplicates and nulls if they exist.
    for the column title : we will drop nulls and everything after (; or :) including (;:) and trim the whitespaces
    for the column summary : we will trim the whitespaces and lowercase the text.
    for the column Languages : we will rewrite it not with abreviations but with the full name of the language.
    for the column download_count : we will keep it > 0 and sort it in descending order.
    for the author_name : we will start with the second name if it exists and then the first name and drop the comma, we will also trim the whitespaces.
    the order of the columns will be : id , title , author_name , languages , download_count , summary.
    """
    LANGUAGES = {
    'en': 'english', 'fr': 'french', 'de': 'german', 'es': 'spanish',
    'it': 'italian', 'pt': 'portuguese', 'ru': 'russian',
    'zh': 'chinese', 'ja': 'japanese', 'ar': 'arabic',
    }

    clean_df = (
        df
        .unique(subset="id")
        .drop_nulls(subset=["id", "title" , "summary" , "languages" , "download_count" , "author_name"])
        .filter(
            pl.col("download_count") > 0
        )
        .with_columns(
            pl.col('title').str.replace(r'[;:].*$', '').str.strip_chars(),
            pl.col('summary').str.strip_chars().str.replace('(This is an automatically generated summary.)', '' , literal=True).str.to_lowercase(),
            pl.col('languages').replace(LANGUAGES).str.strip_chars().str.to_lowercase().alias('language'),
            pl.col('author_name').str.strip_chars().str.split(', ').list.reverse().list.join(' '),
        )
        .select('id' , 'title' , 'author_name' , 'language' , 'download_count' , 'summary')
        .sort('download_count' , descending=True)
    )
    return clean_df