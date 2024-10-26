# mqtt_suscriber/requests/mqtt_subscriber_requests.py
import paho.mqtt.client as mqtt
import json
import requests

API_URL = "http://api:8000/mqtt/requests"

def on_connect_requests(client, userdata, flags, rc):
    try:
        if rc == 0:
            print("Connected to MQTT broker successfully")
            client.subscribe("fixtures/requests")
        else:
            print(f"Connection error. Code: {rc}")
    except Exception as e:
        print(f"Error en on_connect_requests: {e}")

def on_message_requests(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)
        print(f"Request recibido: {data}")
    except Exception as e:
        print(f"Error al procesar mensaje: {e}")
        return

    try:
        # Enviar la solicitud de compra de bonos a la API
        response = requests.post(API_URL, json=data)

        # Verificar si la solicitud fue exitosa (código 201 es éxito para creación)
        response.raise_for_status()

        # Si fue exitosa, mostrar la respuesta
        print(f"Solicitud de compra enviada. Response: {response.json()}")

    except requests.exceptions.HTTPError as http_err:
        # Capturamos errores HTTP y mostramos la respuesta de error de Django
        try:
            error_response = response.json()
            print(f"Error HTTP: {http_err}, Response: {error_response}")
        except ValueError:
            print(f"Error HTTP: {http_err}, pero no se pudo parsear el cuerpo de la respuesta.")

    except requests.exceptions.RequestException as req_err:
        # Captura otros errores relacionados con la solicitud
        print(f"Error al enviar datos a la API: {req_err}")

client = mqtt.Client()
client.username_pw_set("students", "iic2173-2024-2-students")
client.on_connect = on_connect_requests
client.on_message = on_message_requests
client.connect("broker.iic2173.org", 9000, 60)
client.loop_forever()
