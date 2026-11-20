import duckdb
import polars as pl

def clean_data_duckdb(df: pl.DataFrame) -> pl.DataFrame:
    """Clean the books data using DuckDB and return a polars DataFrame."""
    query = """
        WITH filtered AS (
            SELECT DISTINCT ON (id) * FROM df
            WHERE 
                COLUMNS(['id', 'title', 'summary', 'languages','download_count', 'author_name']) IS NOT NULL
                AND download_count > 0
        ),
        cleaning AS (
            SELECT
                id,
                trim(regexp_replace(title, '[;:].*$', '')) AS title,
                CASE
                    WHEN author_name LIKE '%, %'
                    THEN trim(split_part(author_name, ', ', 2)) || ' ' || trim(split_part(author_name, ', ', 1))
                    ELSE trim(author_name)
                END AS author_name,
                CASE trim(languages)
                    WHEN 'en' THEN 'english'
                    WHEN 'fr' THEN 'french'
                    WHEN 'de' THEN 'german'
                    WHEN 'es' THEN 'spanish'
                    WHEN 'it' THEN 'italian'
                    WHEN 'pt' THEN 'portuguese'
                    WHEN 'ru' THEN 'russian'
                    WHEN 'zh' THEN 'chinese'
                    WHEN 'ja' THEN 'japanese'
                    WHEN 'ar' THEN 'arabic'
                    ELSE trim(languages)
                END AS language,
                download_count,
                lower(trim(replace(summary, '(This is an automatically generated summary.)', ''))) AS summary
            FROM filtered
        )
        SELECT 
            id, 
            title, 
            author_name, 
            language, 
            download_count, 
            summary
        FROM cleaning
        ORDER BY download_count DESC
    """
    return duckdb.sql(query).pl()