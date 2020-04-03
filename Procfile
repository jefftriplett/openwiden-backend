release: python manage.py migrate
worker: python manage.py qcluster
web: gunicorn -w 3 config.wsgi --log-file -
