# For devs

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
pip install -r requirements.txt
```

## Database

### Windows
```
docker run --name postgresql-wier -e POSTGRES_PASSWORD=SecretPassword -e POSTGRES_USER=user -v %cd%/pgdata:/var/lib/postgresql/data -v %cd%/init-scripts:/docker-entrypoint-initdb.d -p 5432:5432 -d postgres:12.2
```

### Linux

```
docker run --name postgresql-wier -e POSTGRES_PASSWORD=SecretPassword -e POSTGRES_USER=user -v $PWD/pgdata:/var/lib/postgresql/data -v $PWD/init-scripts:/docker-entrypoint-initdb.d -p 5432:5432 -d postgres:12.2
```
