import paho.mqtt.client as mqtt
import json

def on_connect_validation(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker successfully")
        client.subscribe("fixtures/validation")
    else:
        print(f"Connection error. Code: {rc}")

def on_message_validation(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    data = json.loads(payload)
    # Process the data from the validation channel here

client = mqtt.Client()
client.username_pw_set("students", "iic2173-2024-2-students")
client.on_connect = on_connect_validation
client.on_message = on_message_validation
client.connect("broker.iic2173.org", 9000, 60)
client.loop_forever()