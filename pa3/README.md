# Usage

Move into proper directory and install dependencies.

```shell
cd pa3
pip install -r requirements.txt
cd implementation-indexing
```

## Database

If database not present, first create database inverted-index.db with tables IndexWord and Posting:

```shell
python create-database.py
```

## Preprocess data and create index

```shell
python run-indexing.py
```

## Data retrieval with SQLite and built index

```shell
python run-sqlite-search.py "SEARCH QUERY"
```

## Data retrieval without SQLite

```shell
python run-basic-search.py "SEARCH QUERY"
```

