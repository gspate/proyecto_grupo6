from fastapi import FastAPI, HTTPException
from celery_config.tasks import calculate_recommendations
from pydantic import BaseModel

app = FastAPI()

class RecommendationRequest(BaseModel):
    user_id: int
    fixture_id: int

@app.post("/api/calculate_recommendations/")
async def calculate_recommendations_endpoint(data: RecommendationRequest):
    # Crear la tarea de cálculo de recomendaciones en Celery
    task = calculate_recommendations.delay(data.user_id, data.fixture_id)
    return {"job_id": task.id}
