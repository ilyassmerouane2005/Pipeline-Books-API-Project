# Gutenberg Books ETL

A small data pipeline that pulls messy book data from the [Gutendex API](https://gutendex.com/books), cleans it in two different ways (**Polars** and **DuckDB**), validates the code with **pytest**, and saves the results to disk.

## What the project does

1. **Extract**: requests book data from the API, keeps only the fields we need, and returns a `pl.DataFrame`.
2. **Clean (Polars)**: a function that applies all the cleaning rules using the Polars expression API.
3. **Clean (DuckDB)**: the same cleaning logic written as a SQL query run by DuckDB.
4. **Test**: pytest checks the extractor and the cleaner using a mocked API response (no real network calls).
5. **Load**: `main.py` runs the pipeline and saves:
   - the Polars-cleaned data to a **Parquet** file,
   - the DuckDB-cleaned data to a **table in a database**.

## Project structure

```
.
├── data/
│   ├── messy/
│   │   └── api_url.txt        # API base URL
│   └── clean/
│       ├── books.parquet      # output of the Polars version
│       └── books.db           # output of the DuckDB version (table: books)
├── src/
│   ├── __init__.py
│   ├── extractor.py           # API request + column selection
│   ├── cleaner.py             # cleaning with Polars
│   └── cleaner_duckdb.py      # cleaning with DuckDB (SQL)
├── test/
│   ├── __init__.py
│   └── test.py                # pytest tests
├── main.py                    # runs the whole pipeline
├── pytest.ini                 # pytest configuration
├── requirements.txt
└── .gitignore
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
mkdir -p data/clean              # output folder must exist
```

## Usage

Run the full pipeline:

```bash
python main.py
```

Run the tests:

```bash
pytest
```

(`pytest.ini` tells pytest where to find the tests in `test/`.)

## How each step works

### 1. Extraction (`src/extractor.py`)

`extract_data(url)` calls the API page by page (up to 4 pages, stopping early if there is no next page), collects the results, and builds a Polars DataFrame with these columns:

| Column | Source field |
|---|---|
| `id` | `id` |
| `title` | `title` |
| `summary` | first item of `summaries` |
| `languages` | first item of `languages` |
| `download_count` | `download_count` |
| `author_name` | name of the first item of `authors` |

### 2. Cleaning (`src/cleaner.py` and `src/cleaner_duckdb.py`)

Both versions apply the same rules:

| Column | Rule |
|---|---|
| `id` | drop duplicates and nulls |
| `title` | drop nulls, remove everything after `;` or `:` (inclusive), trim whitespace |
| `summary` | remove the phrase *"This is an automatically generated summary."*, trim whitespace, lowercase |
| `languages` | replace the language code with the full name (`en` → `english`, `fr` → `french`, ...) and rename the column to `language` |
| `download_count` | keep only values `> 0`, sort in descending order |
| `author_name` | convert `Last, First` to `First Last`, trim whitespace |

Final column order: `id`, `title`, `author_name`, `language`, `download_count`, `summary`.

Supported language codes: `en`, `fr`, `de`, `es`, `it`, `pt`, `ru`, `zh`, `ja`, `ar`. Any other code is kept as is.

### 3. Tests (`test/test.py`)

The tests replace `requests.get` with a mock that returns a fake API response, so they run fast and offline. They check that:

- `extract_data` returns a `pl.DataFrame` with the expected shape, columns, and values;
- `clean_data` returns the expected cleaned values (titles, summaries, languages, author names, ordering).

### 4. Saving (`main.py`)

- **Polars version**: `cleaned_df.write_parquet("data/clean/books.parquet")`
- **DuckDB version**: the result of `clean_data_duckdb` is written to a `books` table in `data/clean/books.db` through ADBC (`if_table_exists='replace'`, so re-running the script overwrites the table). The table currently holds 123 cleaned rows.

Each step is wrapped in `try/except` and logs its progress with the `logging` module.

## Tech stack

- Python 3
- [requests](https://requests.readthedocs.io/): API calls
- [Polars](https://pola.rs/): DataFrames and the first cleaning implementation
- [DuckDB](https://duckdb.org/): SQL-based cleaning implementation
- [ADBC](https://arrow.apache.org/adbc/) (`adbc-driver-sqlite`): writing the DataFrame to a database
- [pytest](https://pytest.org/): testing

## Data source

Book metadata comes from [Gutendex](https://gutendex.com/), a JSON API for [Project Gutenberg](https://www.gutenberg.org/).
