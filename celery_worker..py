# celery_worker.py
from main import app as celery_app

if __name__ == '__main__':
    celery_app.worker_main(['worker', '--loglevel=info'])
