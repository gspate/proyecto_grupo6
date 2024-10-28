from celery import shared_task
import requests

@shared_task
def calculate_recommendations(user_id, fixture_id):
    # Paso 1: Obtener el historial de compras del usuario desde Django
    url = f"http://api:8000/user_purchases/{user_id}/"
    response = requests.get(url)
    if response.status_code != 200:
        return {"error": "No se pudo obtener el historial de compras"}

    purchases = response.json()

    # Paso 2: Calcular estadísticas y beneficios de próximos partidos
    recommendations = []
    for purchase in purchases:
        fixture_id = purchase['fixture']['fixture_id']
        league_round = purchase['fixture']['league_round']
        odds_home_value = purchase['fixture']['odds_home_value']
        success_rate = purchase.get('success_rate', 1)  # Porcentaje de éxito de apuestas previas
        pond_score = (success_rate * league_round) / max(odds_home_value, 1)

        recommendations.append({
            "fixture_id": fixture_id,
            "league_name": purchase['fixture']['league_name'],
            "round": league_round,
            "benefit_score": pond_score
        })

    # Ordenar y seleccionar las 3 mejores recomendaciones
    top_recommendations = sorted(recommendations, key=lambda x: x["benefit_score"], reverse=True)[:3]

    # Paso 3: Enviar recomendaciones a Django para almacenarlas
    for recommendation in top_recommendations:
        post_url = "http://api:8000/store_recommendation/"
        response = requests.post(post_url, json={
            "user_id": user_id,
            "fixture_id": recommendation["fixture_id"],
            "league_name": recommendation["league_name"],
            "round": recommendation["round"],
            "benefit_score": recommendation["benefit_score"]
        })
