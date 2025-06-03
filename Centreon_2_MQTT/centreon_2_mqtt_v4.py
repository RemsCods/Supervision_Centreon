import requests
import paho.mqtt.client as mqtt
import time

# 🔧 Config Centreon
IP_CENTREON = "192.168.17.159"
USER = "userapi"
PASSWORD = "2DmqrLt6JP?9"

# 📡 Config MQTT
MQTT_BROKER = "192.168.17.159"
MQTT_PORT = 1883
MQTT_BASE_TOPIC = "etat"

# ⏳ Intervalle de vérification (en secondes)
CHECK_INTERVAL = 10
# ⏳ Intervalle pour envoyer des messages keep-alive (en secondes) (doit etre inferieur à 60 pour garder la connexion)
KEEP_ALIVE_INTERVAL = 40

# 🔑 Obtenir le token d'authentification
def get_centreon_token():
    try:
        url = f"http://{IP_CENTREON}/centreon/api/index.php?action=authenticate"
        payload = {"username": USER, "password": PASSWORD}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
        return response.json().get("authToken")
    except requests.RequestException as e:
        print(f"❌ Erreur : Impossible d'obtenir le token d'authentification. {e}")
        return None

# 📡 Récupérer les données de l'API Centreon
def get_centreon_data(endpoint):
    try:
        url = f"http://{IP_CENTREON}/centreon/api/index.php?object={endpoint}&action=list"
        headers = {
            "Content-Type": "application/json",
            "centreon-auth-token": get_centreon_token()
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Erreur : Impossible de récupérer {endpoint}. {e}")
        return []

# 📡 Connexion MQTT
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}\n")

mqtt_client.on_connect = on_connect
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# 🌐 Stockage des états précédents
previous_states = {"hote": None, "service": None, "env": None}
last_keep_alive_time = time.time()

# 🖥️ Vérification et envoi des états si changement détecté
def check_and_send_states():
    global previous_states, last_keep_alive_time

    # Vérification des hôtes
    hosts = get_centreon_data("centreon_realtime_hosts")
    global_host_state = 0
    for host in hosts:
        host_state = host.get("state", 3)
        if host_state == 2:
            global_host_state = 2  # CRITICAL prend la priorité
        elif host_state == 1 and global_host_state == 0:
            global_host_state = 1  # WARNING si pas de CRITICAL

    # Vérification des services
    services = get_centreon_data("centreon_realtime_services")
    global_service_state = 0
    global_env_state = 0

    for service in services:
        service_name = service.get("description", "unknown")
        service_state = service.get("state", 3)

        if service_state == 2:
            global_service_state = 2  # CRITICAL prend la priorité
        elif service_state == 1 and global_service_state == 0:
            global_service_state = 1  # WARNING si pas de CRITICAL

        if service_name.startswith("env_"):
            if service_state == 2:
                global_env_state = 2
            elif service_state == 1 and global_env_state == 0:
                global_env_state = 1

    # Vérification des changements d'état
    if previous_states["hote"] != global_host_state:
        print(f"📡 Changement détecté: etat/hote → {global_host_state}")
        mqtt_client.publish(f"{MQTT_BASE_TOPIC}/hote", global_host_state)
        previous_states["hote"] = global_host_state

    if previous_states["service"] != global_service_state:
        print(f"📡 Changement détecté: etat/service → {global_service_state}")
        mqtt_client.publish(f"{MQTT_BASE_TOPIC}/service", global_service_state)
        previous_states["service"] = global_service_state

    if previous_states["env"] != global_env_state:
        print(f"📡 Changement détecté: etat/env → {global_env_state}")
        mqtt_client.publish(f"{MQTT_BASE_TOPIC}/env", global_env_state)
        previous_states["env"] = global_env_state

    # Envoyer les derniers états périodiquement pour maintenir la connexion
    current_time = time.time()
    if current_time - last_keep_alive_time >= KEEP_ALIVE_INTERVAL:
        print("📡 Envoi des derniers états pour maintenir la connexion")
        mqtt_client.publish(f"{MQTT_BASE_TOPIC}/hote", previous_states["hote"])
        mqtt_client.publish(f"{MQTT_BASE_TOPIC}/service", previous_states["service"])
        mqtt_client.publish(f"{MQTT_BASE_TOPIC}/env", previous_states["env"])
        last_keep_alive_time = current_time

# 🚀 Exécution en boucle
if __name__ == "__main__":
    print("🚀 Démarrage de la supervision Centreon vers MQTT...")
    while True:
        try:
            check_and_send_states()
        except Exception as e:
            print(f"❌ Une erreur s'est produite : {e}")
        time.sleep(CHECK_INTERVAL)
