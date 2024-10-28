from fastapi import FastAPI, HTTPException
from celery.result import AsyncResult
from celery_config.tasks import calculate_recommendations
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class RecommendationRequest(BaseModel):
    user_id: int
    fixture_id: int

@app.post("/job")
async def create_job(data: RecommendationRequest):
    # Crear la tarea de cálculo de recomendaciones en Celery
    task = calculate_recommendations.delay(data.user_id, data.fixture_id)
    return {"job_id": task.id}

@app.get("/job/{id}")
async def get_job_status(id: str):
    # Obtener el estado del trabajo por su id
    task_result = AsyncResult(id)
    if not task_result:
        raise HTTPException(status_code=404, detail="Job not found")

    # Devolver el estado y el resultado si está disponible
    return {
        "job_id": id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    }

@app.get("/heartbeat")
async def heartbeat():
    # Confirmar que el servicio está operativo
    return {"status": True}
