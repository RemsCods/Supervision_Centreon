#MQTT_2_Centreon_V2
#Recupere les valeurs d'environnement publiées sur MQTT, en fait un etat synthétique et le pousse sur centreon avec la donnée et l'état.
#Commande exemple test valeur MQTT_mosquitto :
#mosquitto_pub -h "ip" -t env/temperature -m "30"

import paho.mqtt.client as mqtt
import requests
import time
import json
import logging
from datetime import datetime, timedelta

#Envois des données dés qu'il y a une nouvelle valeur dans les topics.

# 🔧 Config MQTT
MQTT_BROKER = "192.168.17.159"
MQTT_PORT = 1883
MQTT_TOPICS = ["centreon/+", "env/+"]

# 🔧 Config Centreon
IP_CENTREON = "192.168.17.159"
USER = "userapi"
PASSWORD = "2DmqrLt6JP?9"

# 🚦 Définition des seuils (low is better)
SEUILS = {
    "temperature": {"ok": 30, "warning": 35, "critical": 35},  # °C
    "humidite": {"ok": 65, "warning": 75, "critical": 75},  # %
    "gaz": {"ok": 1.5, "warning": 2.5, "critical": 2.5},  # Volt
}

# 🚦 Définition du seuil d'eau (higher is better)
SEUILS_eau = {
    "eau": {"ok": 4095, "warning": 3200, "critical": 3000}  # ppm  critique inferieur à 3000
}

# Mapping entre topics MQTT et services Centreon
CENTREON_SERVICES = {
    "temperature": "env_temp",
    "humidite": "env_hum",
    "gaz": "env_gaz",
    "eau": "env_eau"
}

# 📝 Config Logs
LOG_FILE = "supervision.log"
LOG_RETENTION_MINUTES = 2  # Pour les tests (remplacer par 2 jours = 2880 minutes en production)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s')

def clean_old_logs():
    now = datetime.now()
    with open(LOG_FILE, "r") as f:
        lines = f.readlines()
    with open(LOG_FILE, "w") as f:
        for line in lines:
            try:
                log_time = datetime.strptime(line.split(' - ')[0], '%Y-%m-%d %H:%M:%S,%f')
                if now - log_time < timedelta(minutes=LOG_RETENTION_MINUTES):
                    f.write(line)
            except ValueError:
                pass

# 📡 Callback lorsque le client se connecte au broker MQTT
def on_connect(client, userdata, flags, rc):
    msg = f"✅ Connecté au broker MQTT avec le code de retour: {rc}"
    print(msg)
    logging.info(msg)
    for topic in MQTT_TOPICS:
        client.subscribe(topic)
        print(f"📡 Abonné au topic: {topic}")
        logging.info(f"📡 Abonné au topic: {topic}")

# 📥 Callback lorsque le client reçoit un message
def on_message(client, userdata, msg):
    value = float(msg.payload.decode())
    log_msg = f"📩 Nouveau message reçu sur le topic {msg.topic}: {value}"
    print(log_msg)
    logging.info(log_msg)

    topic_name = msg.topic.split("/")[-1]  # Extraire le nom du paramètre (ex: temperature, humidite...)
    if topic_name in CENTREON_SERVICES:
        service_name = CENTREON_SERVICES[topic_name]
        if topic_name == "eau":
            status = determine_status_eau(value, SEUILS_eau["eau"])
        else:
            status = determine_status(value, SEUILS[topic_name])
        
        host = "Environnement"
        output = f"Valeur : {value}"
        perfdata = f"perf={value}"
        submit_results(status, host, service_name, output, perfdata)
    else:
        print(f"⚠️ Topic non reconnu : {msg.topic}")
        logging.warning(f"⚠️ Topic non reconnu : {msg.topic}")

# 🚦 Déterminer l'état en fonction des seuils
def determine_status(value, seuils):
    if value <= seuils["ok"]:
        return 0
    elif value <= seuils["warning"]:
        return 1
    return 2 #renvois critique si aucune des deux conditions n est respectée.

# 🚦 Déterminer l'état pour l'eau (higher is better)
def determine_status_eau(value, seuils):
    if value >= seuils["ok"]:
        return 0
    elif value >= seuils["warning"]:
        return 1
    return 2

# 📡 Envoi des résultats à Centreon
def submit_results(status, host, service, output, perfdata):
    token = get_centreon_token()
    url = f"http://{IP_CENTREON}/centreon/api/index.php?action=submit&object=centreon_submit_results"
    headers = {"Content-Type": "application/json", "centreon-auth-token": token}
    current_time = int(time.time())
    results = {"results": [{"updatetime": current_time, "host": host, "service": service, "status": status, "output": output, "perfdata": perfdata}]}
    response = requests.post(url, json=results, headers=headers)
    if response.status_code == 200:
        log_msg = f"📨 Résultat envoyé pour {host} - {service} avec état {status}."
    else:
        log_msg = f"❌ Erreur lors de l'envoi des résultats ({response.status_code}): {response.text}"
    print(log_msg)
    logging.info(log_msg)
    clean_old_logs()

# 📡 Obtenir le token d'authentification Centreon
def get_centreon_token():
    url = f"http://{IP_CENTREON}/centreon/api/index.php?action=authenticate"
    payload = {"username": USER, "password": PASSWORD}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get("authToken")
    print("❌ Erreur : Impossible d'obtenir le token d'authentification.")
    exit(1)

# 🚀 Configurer le client MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# 🔌 Connexion au broker MQTT
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# 🖥️ Lancer la boucle infinie
client.loop_forever()
