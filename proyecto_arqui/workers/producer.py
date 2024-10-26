import os

# FastAPI
from fastapi import FastAPI

# celery
from celery_config.tasks import wait_and_return, sum_to_n_job
from models import Number

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World, this is a route from the producer or job master"}

# https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html
@app.get("/wait_and_return")
def get_publish_job():
    job = wait_and_return.delay()
    return {
        "message": "job published",
        "job_id": job.id,
    }

@app.get("/wait_and_return/{job_id}")
def get_job(job_id: str):
    job = wait_and_return.AsyncResult(job_id)
    print(job)
    return {
        "ready": job.ready(),
        "result": job.result,
    }

@app.post("/sum")
def post_publish_job(number: Number):
    job = sum_to_n_job.delay(number.number)
    return {
        "message": "job published",
        "job_id": job.id,
    }

@app.get("/sum/{job_id}")
def get_job(job_id: str):
    job = sum_to_n_job.AsyncResult(job_id)
    print(job)
    return {
        "ready": job.ready(),
        "result": job.result,
    }