import paho.mqtt.client as mqtt
import json
import requests  
import datetime

API_URL = "http://api:8000" # URL DE API EN AWS

# Enviar los datos a la API
def send_to_api(fixture_info: dict):
    fixture_id = fixture_info["fixture_id"]

    # Modificar el campo 'date' para que solo contenga la fecha (sin hora)
    if 'date' in fixture_info and fixture_info['date']:
        fixture_info['date'] = fixture_info['date'].split('T')[0]  # Esto elimina la parte de la hora

    # Convertir los valores de odds a flotantes
    try:
        if 'odds_home_value' in fixture_info:
            fixture_info['odds_home_value'] = float(fixture_info['odds_home_value']) if fixture_info['odds_home_value'] else None
        if 'odds_draw_value' in fixture_info:
            fixture_info['odds_draw_value'] = float(fixture_info['odds_draw_value']) if fixture_info['odds_draw_value'] else None
        if 'odds_away_value' in fixture_info:
            fixture_info['odds_away_value'] = float(fixture_info['odds_away_value']) if fixture_info['odds_away_value'] else None
    except ValueError as e:
        print(f"Error al convertir las odds a float: {e}")
        return

    try:
        print("Datos a enviar:", fixture_info)
        get_response = requests.get(f"{API_URL}/fixtures/{fixture_id}")

        if get_response.status_code == 200:  # Si el fixture existe, hacer un PUT
            response = requests.put(f"{API_URL}/fixtures/{fixture_id}", json=fixture_info)
            print(f"Se actualizaron los datos de la fixture {fixture_id}")

        elif get_response.status_code == 404:  # Si el fixture no existe, hacer un POST
            response = requests.post(API_URL + "/fixtures", json=fixture_info)
            print(f"Se postearon los datos de la fixture {fixture_id}")

        else:
            print(f"Error al verificar el fixture: {get_response.status_code}")
            return

        response.raise_for_status()  # Lanza una excepción si la solicitud falló
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar datos a la API: {e}")



# Callback cuando se conecta al broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado al broker MQTT exitosamente")
        # Suscribirse al canal fixtures/info
        client.subscribe("fixtures/info")
    else:
        print(f"Error de conexión. Código: {rc}")


# Callback cuando se recibe un mensaje del broker
def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    data1 = json.loads(payload)
    data = json.loads(data1)

    fixtures = data.get("fixtures", [])
    for fixture in fixtures:
        fixture_data = fixture.get("fixture", {})
        league_data = fixture.get("league", {})
        teams_data = fixture.get("teams", {})
        goals_data = fixture.get("goals", {})
        odds_data = fixture.get("odds", [])

        # Fixture
        fixture_id = fixture_data.get("id")
        referee = fixture_data.get("referee")
        timezone = fixture_data.get("timezone")
        date = fixture_data.get("date")
        timestamp = fixture_data.get("timestamp")
        status_long = fixture_data.get("status", {}).get("long")
        status_short = fixture_data.get("status", {}).get("short")
        status_elapsed = fixture_data.get("status", {}).get("elapsed")

        # League
        league_id = league_data.get("id")
        league_name = league_data.get("name")
        league_country = league_data.get("country")
        league_logo = league_data.get("logo")
        league_flag = league_data.get("flag")
        league_season = league_data.get("season")
        league_round = league_data.get("round")

        # Teams
        home_team_id = teams_data.get("home", {}).get("id")
        home_team_name = teams_data.get("home", {}).get("name")
        home_team_logo = teams_data.get("home", {}).get("logo")
        home_team_winner = teams_data.get("home", {}).get("winner")
        away_team_id = teams_data.get("away", {}).get("id")
        away_team_name = teams_data.get("away", {}).get("name")
        away_team_logo = teams_data.get("away", {}).get("logo")
        away_team_winner = teams_data.get("away", {}).get("winner")

        # Goals
        home_goals = goals_data.get("home")
        away_goals = goals_data.get("away")

        # Odds (COMPLETAR)
        odds_list = []

        for odd in odds_data:
            odds_id = odd.get("id")
            odds_name = odd.get("name")
            odds_home_value = next((v.get("odd") for v in odd.get("values", []) if v.get("value") == "Home"), None)
            odds_draw_value = next((v.get("odd") for v in odd.get("values", []) if v.get("value") == "Draw"), None)
            odds_away_value = next((v.get("odd") for v in odd.get("values", []) if v.get("value") == "Away"), None)

            # Agregar las odds al diccionario
            odds_list.append({
                "odds_id": odds_id,
                "odds_name": odds_name,
                "odds_home_value": odds_home_value,
                "odds_draw_value": odds_draw_value,
                "odds_away_value": odds_away_value
            })

        # Diccionario con las odds para cada fixture
        odds_info = odds_list[0]
        last_updated = str(datetime.datetime.utcnow().isoformat())

        # Crear el diccionario con la información del fixture
        fixture_info = {
            "fixture_id": fixture_id,
            "referee": referee,
            "timezone": timezone,
            "date": date,
            "timestamp": timestamp,
            "status_long": status_long,
            "status_short": status_short,
            "status_elapsed": status_elapsed,
            "league_id": league_id,
            "league_name": league_name,
            "league_country": league_country,
            "league_logo": league_logo,
            "league_flag": league_flag,
            "league_season": league_season,
            "league_round": league_round,
            "home_team_id": home_team_id,
            "home_team_name": home_team_name,
            "home_team_logo": home_team_logo,
            "home_team_winner": home_team_winner,
            "away_team_id": away_team_id,
            "away_team_name": away_team_name,
            "away_team_logo": away_team_logo,
            "away_team_winner": away_team_winner,
            "home_goals": home_goals,
            "away_goals": away_goals,
            "odds_id": odds_info.get("odds_id"),
            "odds_name": odds_info.get("odds_name"),
            "odds_home_value": odds_info.get("odds_home_value"),
            "odds_draw_value": odds_info.get("odds_draw_value"),
            "odds_away_value": odds_info.get("odds_away_value"),
            "last_updated": last_updated
        }

        # Enviar los datos a la API
        send_to_api(fixture_info)


# Crear una instancia del cliente MQTT
client = mqtt.Client()

# Configurar credenciales de acceso
client.username_pw_set("students", "iic2173-2024-2-students")

# Asignar los callbacks
client.on_connect = on_connect
client.on_message = on_message

# Conectar al broker MQTT
broker_address = "broker.iic2173.org"
broker_port = 9000
client.connect(broker_address, broker_port, 60)

# Mantener el cliente en ejecución
client.loop_forever()
