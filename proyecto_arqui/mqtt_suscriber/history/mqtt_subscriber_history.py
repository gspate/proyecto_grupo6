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
        # print(f"Payload recibido: {payload}")  # Ver qué contiene el payload
        
        # Asegurarse de que el payload es un JSON válido
        try:
            data = json.loads(payload)  # Decodificar el payload
            if isinstance(data, str):
                # print("El payload está doblemente codificado. Intentando decodificar nuevamente.")
                data = json.loads(data)  # Decodificar el string nuevamente
            # print(f"Payload decodificado correctamente: {data}")
            # print(f"Tipo de data decodificada: {type(data)}")  # Imprimir el tipo de data
        except json.JSONDecodeError as e:
            print(f"Error al decodificar el JSON: {e}")
            return  # Terminar la función si falla la decodificación

        # Comprobar si el data es un diccionario
        if isinstance(data, dict):
            print("El payload es un diccionario válido")
            fixtures = data.get("fixtures", [])
            if not fixtures:
                print("No se encontraron fixtures en el mensaje recibido")
                return

            # Enviar los datos a la API usando una solicitud POST
            # print(f"Data a enviar a la API: {data}")
            print(f"Enviando datos a la API en {API_URL}")
            try:
                response = requests.post(API_URL, json=data)
                if response.status_code == 200:
                    print("Datos enviados a la API correctamente")
                    print(f"Contenido de la respuesta: {response.text}")
                else:
                    print(f"Error al enviar datos a la API. Código de estado: {response.status_code}")
                    print(f"Contenido de la respuesta: {response.text}")  # Mostrar la respuesta de la API
                response.raise_for_status()  # Lanza una excepción si hay algún error
            except requests.exceptions.RequestException as e:
                print(f"Error al intentar enviar los datos: {e}")
        else:
            print("El payload no es un diccionario válido")

    except Exception as e:
        print(f"Error inesperado: {e}")

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
