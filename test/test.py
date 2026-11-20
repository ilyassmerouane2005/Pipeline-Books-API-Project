from unittest.mock import Mock , patch
from src.extractor import extract_data
from src.cleaner import clean_data
import pytest
import polars as pl

FAKE_RESPONSE = {
    'next': None,
    'results': [
        {
            'id': 1342,
            'title': 'Pride and Prejudice',
            'summaries': ['"Pride and Prejudice" is a novel by Jane Austen.(This is an automatically generated summary.)'],
            'languages': ['en'],
            'download_count': 200,
            'authors': [{'name': 'Austen, Jane', 'birth_year': 1775, 'death_year': 1817}],
        },
        {
            'id': 84,
            'title': 'Frankenstein; Or, The Modern Prometheus',
            'summaries': ['A Gothic novel by Mary Shelley.(This is an automatically generated summary.)'],
            'languages': ['en'],
            'download_count': 100,
            'authors': [{'name': 'Shelley, Mary Wollstonecraft', 'birth_year': 1797, 'death_year': 1851}],
        },
    ],
}

def get_fake(*args , **kwargs):
    mock_response = Mock()
    mock_response.json.return_value = FAKE_RESPONSE 
    mock_response.raise_for_status.return_value = None
    return mock_response

@patch('src.extractor.requests.get' , new=get_fake)

def test_extract_data():

    df = extract_data()
    assert isinstance(df , pl.DataFrame)
    assert df.shape[0] == 2
    assert df.columns == ['id', 'title', 'summary', 'languages', 'download_count', 'author_name']
    assert df['id'].to_list() == [1342, 84] 
    assert df['title'].to_list() == ['Pride and Prejudice', 'Frankenstein; Or, The Modern Prometheus']
    assert df['summary'].to_list() == [
        '"Pride and Prejudice" is a novel by Jane Austen.(This is an automatically generated summary.)', 
        'A Gothic novel by Mary Shelley.(This is an automatically generated summary.)'
    ]
    assert df['languages'].to_list() == ['en', 'en']
    assert df['download_count'].to_list() == [200, 100]
    assert df['author_name'].to_list() == ['Austen, Jane', 'Shelley, Mary Wollstonecraft']

@pytest.fixture

def test_clean_data(messy_data):

    with patch('src.extractor.requests.get' , new=get_fake):
        messy_data = extract_data()

    cleaned_df = clean_data(messy_data)
    assert isinstance(cleaned_df , pl.DataFrame)
    assert cleaned_df.shape[0] == 2
    assert cleaned_df.columns == ['id', 'title', 'author_name', 'language', 'download_count', 'summary']
    assert cleaned_df['id'].to_list() == [1342, 84]
    assert cleaned_df['title'].to_list() == ['Pride and Prejudice', 'Frankenstein']
    assert cleaned_df['summary'].to_list() == [
        '"pride and prejudice" is a novel by jane austen.', 
        'a gothic novel by mary shelley.'
    ]
    assert cleaned_df['language'].to_list() == ['english', 'english']
    assert cleaned_df['download_count'].to_list() == [200, 100]
    assert cleaned_df['author_name'].to_list() == ['Jane Austen', 'Mary Wollstonecraft Shelley']