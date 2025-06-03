import paho.mqtt.client as mqtt

# 🔧 Config MQTT
MQTT_BROKER = "192.168.17.159"  # Remplace par l'adresse de ton broker MQTT
MQTT_PORT = 1883
# Les topics auxquels on veut s'abonner (+ permet de s abonner a tous les niveaux juste au dessus)
MQTT_TOPICS = ["centreon/+", "env/+"]

# 📡 Callback lorsque le client se connecte au broker MQTT
def on_connect(client, userdata, flags, rc):
    print(f"✅ Connecté au broker MQTT avec le code de retour: {rc}")
    # S'abonner à tous les topics
    for topic in MQTT_TOPICS:
        client.subscribe(topic)
        print(f"📡 Abonné au topic: {topic}")

# 📥 Callback lorsque le client reçoit un message
def on_message(client, userdata, msg):
    print(f"📩 Nouveau message reçu sur le topic {msg.topic}: {msg.payload.decode()}")

# 🚀 Configurer le client MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# 🔌 Connexion au broker MQTT
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# 🖥️ Lancer la boucle infinie pour écouter les messages
client.loop_forever()
