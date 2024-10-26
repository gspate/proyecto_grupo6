# celery
from celery import shared_task
from celery_config.controllers import sum_to_n

# standard
import time

# The "shared_task" decorator allows creation
# of Celery tasks for reusable apps as it doesn't
# need the instance of the Celery app.
# @celery_app.task()
@shared_task()
def add(x, y):
    return x + y

@shared_task
def wait_and_return():
    time.sleep(20)
    return 'Hello World!'

@shared_task
def sum_to_n_job(number):
    result = sum_to_n(number)
    return result