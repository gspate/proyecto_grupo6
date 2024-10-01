import paho.mqtt.client as mqtt
import json
import uuid
from datetime import datetime

# Configuración del broker MQTT
MQTT_BROKER = "broker.iic2173.org"
MQTT_PORT = 9000
MQTT_TOPIC = "fixtures/requests"

# Función para simular la compra de un bono
def simulate_bonus_purchase(fixture_id, league_name, round_name, date, result, quantity, group_id="6"):
    # Crear un request_id único
    request_id = str(uuid.uuid4())
    
    # Generar el cuerpo del mensaje según el formato requerido
    message = {
        "request_id": request_id,
        "group_id": group_id,
        "fixture_id": fixture_id,
        "league_name": league_name,
        "round": round_name,
        "date": date,
        "result": result,
        "deposit_token": "",
        "datetime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "quantity": quantity,
        "seller": 0
    }

    # Enviar la solicitud al canal MQTT
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Conectado al broker MQTT")
            # Publicar el mensaje
            client.publish(MQTT_TOPIC, json.dumps(message))
            print(f"Solicitud de compra enviada:\n{json.dumps(message, indent=2)}")
            client.disconnect()
        else:
            print(f"Error al conectar al broker MQTT. Código: {rc}")

    # Inicializar el cliente MQTT
    client = mqtt.Client()
    client.username_pw_set("students", "iic2173-2024-2-students")
    client.on_connect = on_connect

    # Conectar al broker y enviar la solicitud
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

# Ejemplo de uso
if __name__ == "__main__":
    # Parámetros de la compra de bono (puedes modificar según tus necesidades)
    fixture_id = 1208082
    league_name = "La Liga"
    round_name = "Regular Season - 9"
    date = "2024-09-29T19:00:00Z"
    result = "Espanyol"
    quantity = 1  # Cantidad de bonos a comprar

    # Simular la compra de bono
    simulate_bonus_purchase(fixture_id, league_name, round_name, date, result, quantity)
