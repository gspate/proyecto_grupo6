from celery import shared_task
import requests

@shared_task
def calculate_recommendations(user_id, fixture_id):
    # Paso 1: Obtener el historial de compras del usuario
    url = f"http://api:8000/user_purchases/{user_id}"
    response = requests.get(url)
    if response.status_code != 200:
        return {"error": "No se pudo obtener el historial de compras"}
    
    purchases = response.json()
    equipos_involucrados = set()  # Almacena los equipos en las compras
    aciertos_por_equipo = {}  # Aciertos acumulados por equipo
    recommendations = []

    # Paso 2: Iterar sobre las compras para identificar equipos y calcular aciertos
    for purchase in purchases:
        fixture_id = purchase["fixture_id"]
        
        # Obtener detalles del fixture actual
        fixture_url = f"http://api:8000/fixtures/{fixture_id}"
        fixture_response = requests.get(fixture_url)
        if fixture_response.status_code != 200:
            continue  # Saltar si no se puede obtener el fixture
        
        fixture_data = fixture_response.json()

        # Identificar equipos y actualizar contador de aciertos
        home_team_id = fixture_data["home_team_id"]
        away_team_id = fixture_data["away_team_id"]
        equipos_involucrados.update([home_team_id, away_team_id])

        # Definir equipo apostado y verificar acierto
        equipo_apostado = purchase["result"]
        es_acierto = purchase.get("acierto", False)
        
        equipo_id = home_team_id if equipo_apostado == fixture_data["home_team_name"] else away_team_id
        if equipo_id not in aciertos_por_equipo:
            aciertos_por_equipo[equipo_id] = {"aciertos": 0, "rounds": fixture_data.get("league_round", "1")}
        if es_acierto:
            aciertos_por_equipo[equipo_id]["aciertos"] += 1

    # Paso 3: Obtener todos los fixtures y filtrar por equipos involucrados y partidos no jugados
    all_fixtures_url = "http://api:8000/fixtures"
    all_fixtures_response = requests.get(all_fixtures_url)
    
    if all_fixtures_response.status_code != 200:
        return {"error": "No se pudo obtener la lista de fixtures"}

    all_fixtures = all_fixtures_response.json()

    # Filtrar los próximos partidos de los equipos involucrados
    for fixture in all_fixtures:
        # Verificar si el partido es de un equipo involucrado y aún no ha comenzado
        if (
            fixture["status_long"] == "Not Started" or fixture["status_short"] == "NS"
        ) and (
            fixture["home_team_id"] in equipos_involucrados or fixture["away_team_id"] in equipos_involucrados
        ):
            league_name = fixture["league_name"]
            league_round = int(fixture.get("league_round", "1").split()[-1])
            odds_home_value = fixture.get("odds_home_value", 1)
            odds_draw_value = fixture.get("odds_draw_value", 1)
            odds_away_value = fixture.get("odds_away_value", 1)

            # Aciertos previos para el equipo en el fixture
            equipo_id = fixture["home_team_id"] if fixture["home_team_id"] in equipos_involucrados else fixture["away_team_id"]
            aciertos = aciertos_por_equipo.get(equipo_id, {}).get("aciertos", 0)
            sum_odds = odds_home_value + odds_draw_value + odds_away_value
            pond_score = (aciertos * league_round) / max(sum_odds, 1)

            recommendations.append({
                "fixture_id": fixture["fixture_id"],
                "league_name": league_name,
                "round": league_round,
                "benefit_score": pond_score
            })

    # Ordenar y seleccionar las 3 recomendaciones con mayor puntaje
    top_recommendations = sorted(recommendations, key=lambda x: x["benefit_score"], reverse=True)[:3]

    # Paso 4: Enviar recomendaciones para almacenamiento
    for recommendation in top_recommendations:
        post_url = "http://api:8000/store_recommendation"
        response = requests.post(post_url, json={
            "user_id": user_id,  # Asegúrate de usar el ID del usuario
            "fixture_id": recommendation["fixture_id"],  # Usa el ID del fixture
            "league_name": recommendation["league_name"],
            "round": recommendation["round"],
            "benefit_score": recommendation["benefit_score"]
        })

    return {"status": "Recommendations calculated successfully", "recommendations": top_recommendations}
