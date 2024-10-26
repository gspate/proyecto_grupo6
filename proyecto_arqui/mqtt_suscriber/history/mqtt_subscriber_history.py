import paho.mqtt.client as mqtt
import json
import requests

# URL de la API donde se enviarán los datos
API_URL = "http://api:8000/mqtt/history"  # Ajusta esto a tu URL real

# Callback cuando se conecta al broker
def on_connect_history(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado al broker MQTT exitosamente")
        client.subscribe("fixtures/history")
    else:
        print(f"Error de conexión. Código: {rc}")

# Callback cuando se recibe un mensaje del broker
def on_message_history(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        print(f"Payload recibido: {payload}")  # Ver qué contiene el payload
        
        # Asegurarse de que el payload es un JSON válido
        if isinstance(payload, str):
            try:
                data = json.loads(payload)  # Decodificar el payload si es un string
                print(f"Payload decodificado correctamente: {data}")
            except json.JSONDecodeError as e:
                print(f"Error al decodificar el JSON: {e}")
                return  # Terminar la función si falla la decodificación
        else:
            data = payload  # Si ya es un diccionario, úsalo tal cual

        # Asegurarse de que 'data' es un diccionario
        if isinstance(data, dict):
            # Verificar que se recibieron fixtures
            fixtures = data.get("fixtures", [])
            if not fixtures:
                print("No se encontraron fixtures en el mensaje recibido")
                return

            # Enviar los datos a la API usando una solicitud POST
            response = requests.post(API_URL, json=data)
            if response.status_code == 200:
                print("Datos enviados a la API correctamente")
            else:
                print(f"Error al enviar datos a la API. Código: {response.status_code}")
            response.raise_for_status()  # Lanza una excepción si hay algún error
        else:
            print("El payload no es un diccionario válido")

    except requests.exceptions.RequestException as e:
        print(f"Error al intentar enviar los datos: {e}")

# Configuración del cliente MQTT
client = mqtt.Client()

# Configurar las credenciales de acceso
client.username_pw_set("students", "iic2173-2024-2-students")

# Asignar los callbacks
client.on_connect = on_connect_history
client.on_message = on_message_history

# Conectar al broker MQTT
broker_address = "broker.iic2173.org"
broker_port = 9000
client.connect(broker_address, broker_port, 60)

# Mantener el cliente en ejecución
client.loop_forever()
