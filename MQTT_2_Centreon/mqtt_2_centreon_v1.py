import paho.mqtt.client as mqtt
import requests
import time
import json

# 🔧 Config MQTT
MQTT_BROKER = "192.168.17.159"  # Remplace par l'adresse de ton broker MQTT
MQTT_PORT = 1883
MQTT_TOPICS = ["centreon/+", "env/+"]

# 🔧 Config Centreon
IP_CENTREON = "192.168.17.159"
USER = "userapi"
PASSWORD = "2DmqrLt6JP?9"

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
    value = msg.payload.decode()  # Valeur reçue du topic

    # Vérifier le topic et envoyer les données appropriées à Centreon
    #partie temperature
    if msg.topic == "env/temperature":
        service_name = "env_temp"
        host = "Environnement"
        output = f"Valeur : {value}°C"
        perfdata = f"perf={value}"
        status = 0  # Status OK
        submit_results(status, host, service_name, output, perfdata)

    #partie humidite
    elif msg.topic == "env/humidite":
        service_name = "env_hum"
        host = "Environnement"
        output = f"Valeur : {value}%"
        perfdata = f"perf={value}"
        status = 0  # Status OK
        submit_results(status, host, service_name, output, perfdata)

    #partie gaz
    elif msg.topic == "env/gaz":
        service_name = "env_gaz"
        host = "Environnement"
        output = f"Valeur : {value}Volt"
        perfdata = f"perf={value}"
        status = 0  # Status OK
        submit_results(status, host, service_name, output, perfdata)

    #partie eau
    elif msg.topic == "env/eau":
        service_name = "env_eau"
        host = "Environnement"
        output = f"Valeur : {value} ppm"
        perfdata = f"perf={value}"
        status = 0  # Status OK
        submit_results(status, host, service_name, output, perfdata)

# 📡 Obtenir le token d'authentification Centreon
def get_centreon_token():
    url = f"http://{IP_CENTREON}/centreon/api/index.php?action=authenticate"
    payload = {"username": USER, "password": PASSWORD}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(url, data=payload, headers=headers)
    if response.status_code == 200:
        token = response.json().get("authToken")
        #########################################print(f"✅ Token obtenu : {token}")  # Debug
        return token
    else:
        print("❌ Erreur : Impossible d'obtenir le token d'authentification.")
        exit(1)

# 📡 Envoi des résultats à Centreon
def submit_results(status, host, service, output, perfdata):
    token = get_centreon_token()
    url = f"http://{IP_CENTREON}/centreon/api/index.php?action=submit&object=centreon_submit_results"
    headers = {
        "Content-Type": "application/json",
        "centreon-auth-token": token
    }
    current_time = int(time.time())  # 🕒 Timestamp actuel

    # Données du service à envoyer
    results = {
        "results": [{
            "updatetime": current_time,
            "host": host,
            "service": service,
            "status": status,
            "output": output,
            "perfdata": perfdata
        }]
    }
    
    # Affichage des données pour déboguer
    #############################################print(f"📤 Données à envoyer à Centreon : {json.dumps(results, indent=4)}")
    
    # Envoi de la requête POST
    response = requests.post(url, json=results, headers=headers)
    if response.status_code == 200:
        print(f"✅ Résultat envoyé pour {host} - {service} avec l'état {status}.")
    else:
        print(f"❌ Erreur lors de l'envoi des résultats pour {host} - {service}. Code erreur : {response.status_code}")
        print(f"Réponse de Centreon : {response.text}")

# 🚀 Configurer le client MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# 🔌 Connexion au broker MQTT
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# 🖥️ Lancer la boucle infinie pour écouter les messages
client.loop_forever()
