import paho.mqtt.client as mqtt
import json
import requests
from retry import retry
import time

API_URL = "http://api:8000/mqtt/validations"

def on_connect_validation(client, userdata, flags, rc):
    try:
        if rc == 0:
            print("Connected to MQTT broker successfully")
            client.subscribe("fixtures/validation")
        else:
            print(f"Connection error. Code: {rc}")
    except Exception as e:
        print(f"Error en on_connect_validation: {e}")

@retry(tries=10, delay=5, backoff=2)
def send_validation_request(api_url_with_id, data):
    try:
        # Enviar la validación de la solicitud a la API
        response = requests.put(api_url_with_id, json=data)
        response.raise_for_status()  # Lanza una excepción si la respuesta no fue exitosa
        if response.status_code == 404:
            raise Exception("Request not found")
        print(f"Validación de solicitud enviada. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar datos a la API: {e}")
        raise  # Forzar el reintento

def on_message_validation(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)
        print(f"Validation recibida: {data}")
    except json.JSONDecodeError as e:
        print(f"Error al procesar el mensaje JSON: {e}")
        return
    except Exception as e:
        print(f"Error inesperado al procesar mensaje: {e}")
        return
    
    try:
        # Construir la URL dinámica con el request_id
        request_id = data.get('request_id')
        if not request_id:
            print("Error: request_id no encontrado en la validación")
            return
        
        # Introducir un pequeño retraso inicial para dar tiempo a que se procese la request
        time.sleep(5)

        # Incluir el request_id en la URL
        api_url_with_id = f"{API_URL}/{request_id}"
        
        # Enviar la validación de la solicitud a la API
        send_validation_request(api_url_with_id, data)
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar datos a la API")
    except Exception as e:
        print(f"Error inesperado: {e}")

client = mqtt.Client()
client.username_pw_set("students", "iic2173-2024-2-students")
client.on_connect = on_connect_validation
client.on_message = on_message_validation
client.connect("broker.iic2173.org", 9000, 60)
client.loop_forever()
