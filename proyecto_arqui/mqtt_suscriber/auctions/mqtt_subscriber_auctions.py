import paho.mqtt.client as mqtt
import json
import requests

# URL de la API donde se enviarán los datos
API_URL = "http://api:8000/mqtt/auctions"

# Almacén de mensajes ya procesados
processed_messages = set()

# Callback cuando se conecta al broker
def on_connect_auctions(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado al broker MQTT exitosamente")
        client.subscribe("fixtures/auctions")
    else:
        print(f"Error de conexión. Código: {rc}")

# Callback cuando se recibe un mensaje del broker
def on_message_auctions(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        print(f"Mensaje recibido en '{msg.topic}': {payload}")
        # Identificar el mensaje por un identificador único
        message_id = hash(payload)

        # Evitar procesar mensajes duplicados
        if message_id in processed_messages:
            print("Mensaje duplicado detectado. Ignorando.")
            return
        processed_messages.add(message_id)

        # Decodificar el payload como JSON
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as e:
            print(f"Error al decodificar el JSON: {e}")
            return

        # Enviar los datos a la API usando una solicitud POST
        print(f"Enviando datos a la API en {API_URL}")
        try:
            response = requests.post(API_URL, json=data)
            if response.status_code == 201:
                print("Datos enviados a la API correctamente")
                print(f"Contenido de la respuesta: {response.text}")
            else:
                print(f"Error al enviar datos a la API. Código de estado: {response.status_code}")
                print(f"Contenido de la respuesta: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error al intentar enviar los datos: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

# Configuración del cliente MQTT
client = mqtt.Client()

# Configurar las credenciales de acceso
client.username_pw_set("students", "iic2173-2024-2-students")

# Asignar los callbacks
client.on_connect = on_connect_auctions
client.on_message = on_message_auctions

# Conectar al broker MQTT
broker_address = "broker.iic2173.org"
broker_port = 9000
client.connect(broker_address, broker_port, 60)

# Mantener el cliente en ejecución
client.loop_forever()