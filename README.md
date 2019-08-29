# Open Apostolic Fathers Atlas

ATLAS Server for Open Apostolic Fathers.

## Getting Started

Make sure you are using a virtual environment of some sort (e.g. `virtualenv` or
`pyenv`).

```
pip install -r requirements-dev.txt
```

Create a PostgreSQL database `apostolic_fathers_atlas`:

```
createdb apostolic_fathers_atlas
```

Populate the database:

```
./manage.py migrate
./manage.py loaddata sites
```

Run the Django dev server:
```
./manage.py runserver
```

Browse to http://localhost:8000/

## Loading data

Create a superuser:

```
./manage.py createsuperuser
```

Run the `import_versions` script:

```
python manage.py shell -c 'from apostolic_fathers_atlas.library.importers import import_versions; import_versions();'
```
