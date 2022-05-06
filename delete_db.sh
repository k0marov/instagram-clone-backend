#/bin/sh
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
find . -path "*.sqlite3"  -delete
./manage.py makemigrations
./manage.py migrate --sync-db
