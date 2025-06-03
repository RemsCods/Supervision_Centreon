import paho.mqtt.client as mqtt
from modules.config import MQTT_BROKER, MQTT_PORT

mqtt_client = mqtt.Client()

# 📡 Publi sur les topics
def send_mqtt_message(topic, message):
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.publish(topic, message)
    finally:
        mqtt_client.disconnect()
