web: gunicorn config.wsgi:application
worker: celery worker --app=collab_canvas.taskapp --loglevel=info
