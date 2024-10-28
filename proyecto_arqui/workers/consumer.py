import os

from celery import Celery

celery_app = Celery(
    __name__,
    # https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/index.html
    broker=os.environ.get('CELERY_BROKER_URL', '')  # Configura solo el broker
)

# Setup to use all the variables in settings
# that begins with 'CELERY_'
celery_app.config_from_object('celery_config.config', namespace='CELERY')