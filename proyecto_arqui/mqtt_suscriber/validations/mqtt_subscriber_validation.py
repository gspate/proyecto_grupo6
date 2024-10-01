# mqtt_suscriber/validations/mqtt_subscriber_validation.py
import paho.mqtt.client as mqtt
import json
import requests
from retry import retry

API_URL = "http://api:8000/bonus/request"

def on_connect_validation(client, userdata, flags, rc):
    try:
        if rc == 0:
            print("Connected to MQTT broker successfully")
            client.subscribe("fixtures/validation")
        else:
            print(f"Connection error. Code: {rc}")
    except Exception as e:
        print(f"Error en on_connect_validation: {e}")

@retry(tries=5, delay=2, backoff=2)
def send_validation_request(api_url_with_id, data):
    # Enviar la validación de la solicitud a la API
    response = requests.put(api_url_with_id, json=data)
    if response.status_code == 404:
        raise Exception("Request not found")
    print(f"Validación de solicitud enviada. Status code: {response.status_code}, Response: {response.text}")

def on_message_validation(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)
        print(f"Validation recibida: {data}")
    except Exception as e:
        print(f"Error al procesar mensaje: {e}")
        return
    
    try:
        # Construir la URL dinámica con el request_id
        request_id = data.get('request_id')
        if not request_id:
            print("Error: request_id no encontrado en la validación")
            return
        
        # Incluir el request_id en la URL
        api_url_with_id = f"{API_URL}/{request_id}/"
        
        # Enviar la validación de la solicitud a la API
        send_validation_request(api_url_with_id, data)
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar datos a la API: {e}")
        
client = mqtt.Client()
client.username_pw_set("students", "iic2173-2024-2-students")
client.on_connect = on_connect_validation
client.on_message = on_message_validation
client.connect("broker.iic2173.org", 9000, 60)
client.loop_forever()
