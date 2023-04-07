# Description

## Environment

```
python3 -m venv env
```

or

```
python -m venv env
```

### To activate venv:

- MacOS/Linux:

```
source env/bin/activate
```

- Windows:

```
env\Scripts\activate
```

Finally:

```
pip install -r pa1/requirements.txt
```

## Database

### Windows

```
docker run --name postgresql-wier -e POSTGRES_PASSWORD=SecretPassword -e POSTGRES_USER=user -v %cd%/pgdata:/var/lib/postgresql/data -v %cd%/pa1/init-scripts:/docker-entrypoint-initdb.d -p 5432:5432 -d postgres:12.2
```

### Linux

```
docker run --name postgresql-wier -e POSTGRES_PASSWORD=SecretPassword -e POSTGRES_USER=user -v $PWD/pgdata:/var/lib/postgresql/data -v $PWD/pa1/init-scripts:/docker-entrypoint-initdb.d -p 5432:5432 -d postgres:12.2
```

### [Link to backed up database with 50k html pages](https://unilj-my.sharepoint.com/:u:/g/personal/jp6957_student_uni-lj_si/EXO4lXx02Z1HqwAJ_ydwIpcB_z67U-_lU3V8q3WyoWDf7g?e=gnaxeC)

## Run crawler

```
python pa1/crawler/main.py
```

Change the NUMBER_OF_WORKERS parameter in ProjectConfig. 