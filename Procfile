release: python manage.py migrate && python manage.py setup_social_auth && python manage.py cleanup_social_apps
web: gunicorn app.wsgi