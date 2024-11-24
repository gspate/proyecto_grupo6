import paho.mqtt.client as mqtt
import json

# Configuración del broker MQTT
MQTT_BROKER = "broker.iic2173.org"
MQTT_PORT = 9000
MQTT_TOPIC = "fixtures/requests"
MQTT_USER = "students"
MQTT_PASSWORD = "iic2173-2024-2-students"

def on_connect_requests(client, userdata, flags, rc):
    try:
        if rc == 0:
            print(f"Conectado al broker MQTT {MQTT_BROKER}:{MQTT_PORT} exitosamente.")
            client.subscribe(MQTT_TOPIC)
            print(f"Suscrito al tema '{MQTT_TOPIC}'")
        else:
            print(f"Error al conectar al broker. Código: {rc}")
    except Exception as e:
        print(f"Error en on_connect_requests: {e}")

def on_message_requests(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)  # Intentar interpretar el mensaje como JSON
        print(f"Mensaje recibido en '{msg.topic}': {json.dumps(data, indent=4)}")
    except json.JSONDecodeError:
        # Si no es JSON, mostrar el payload como texto plano
        print(f"Mensaje recibido en '{msg.topic}': {msg.payload.decode('utf-8')}")
    except Exception as e:
        print(f"Error al procesar el mensaje: {e}")

# Configurar el cliente MQTT
client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
client.on_connect = on_connect_requests
client.on_message = on_message_requests

try:
    print(f"Conectando al broker MQTT {MQTT_BROKER}:{MQTT_PORT}...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    print("Esperando mensajes...")
    client.loop_forever()  # Mantener el cliente escuchando
except KeyboardInterrupt:
    print("\nDesconectando del broker MQTT...")
    client.disconnect()
except Exception as e:
    print(f"Error crítico: {e}")


{
    "user_id": "aadfadsf234234",
    "username": "Admin",
    "email": "alvaro.sotomayor@uc.cl",
    "first_name": "Alvaro",
    "last_name": "Sotomayor",
    "wallet": 1000000000,
}