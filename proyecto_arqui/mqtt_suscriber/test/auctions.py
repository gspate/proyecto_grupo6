import paho.mqtt.publish as publish
import uuid6
import random
import json

# Configuración del broker MQTT
MQTT_HOST = "broker.iic2173.org"
MQTT_PORT = 9000
MQTT_TOPIC = "fixtures/auctions"
MQTT_USER = "students"
MQTT_PASSWORD = "iic2173-2024-2-students"

# Función para generar datos falsos
def generate_fake_data():
    auction_id = "1efabc47-e07c-6ff9-9e6b-41a1ccd465d6"
    proposal_id = "1efabc70-d9a6-63f0-a960-2b708302b04d"
    fixture_id = 1212924  # Número aleatorio entre 1000 y 9999
    league_name = "Premier League"
    league_round = "Round 35"
    result = "away"
    quantity = 3
    group_id = 1000000

    data = {
        "auction_id": auction_id,
        "proposal_id": proposal_id,
        "fixture_id": fixture_id,
        "league_name": league_name,
        "round": league_round,
        "result": result,
        "quantity": quantity,
        "group_id": group_id,
        "type": "acceptance",
    }

    return data

# Función para enviar los datos al broker MQTT
def send_to_broker(data):
    try:
        payload = json.dumps(data)
        publish.single(
            topic=MQTT_TOPIC,
            payload=payload,
            hostname=MQTT_HOST,
            port=MQTT_PORT,
            auth={"username": MQTT_USER, "password": MQTT_PASSWORD},
        )
        print(f"Mensaje enviado exitosamente: {payload}")
    except Exception as e:
        print(f"Error al enviar mensaje: {e}")

# Generar datos falsos y enviarlos al broker
if __name__ == "__main__":
    fake_data = generate_fake_data()
    send_to_broker(fake_data)
