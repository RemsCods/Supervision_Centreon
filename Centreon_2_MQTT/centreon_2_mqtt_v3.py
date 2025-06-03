#Centreon_2_MQTT_V3
#Check à intervalle x si des etats on changé (hote et service) et les envois sur MQTT.

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

# 🔑 Obtenir le token d'authentification
def get_centreon_token():
    url = f"http://{IP_CENTREON}/centreon/api/index.php?action=authenticate"
    payload = {"username": USER, "password": PASSWORD}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(url, data=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get("authToken")
    else:
        print("❌ Erreur : Impossible d'obtenir le token d'authentification.")
        exit(1)

# 📡 Récupérer les données de l'API Centreon
def get_centreon_data(endpoint):
    url = f"http://{IP_CENTREON}/centreon/api/index.php?object={endpoint}&action=list"
    headers = {
        "Content-Type": "application/json",
        "centreon-auth-token": get_centreon_token()
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Erreur : Impossible de récupérer {endpoint}")
        return []

# 📡 Connexion MQTT
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# 🌐 Stockage des états précédents
previous_states = {"hote": None, "service": None, "env": None}

# 🖥️ Vérification et envoi des états si changement détecté
def check_and_send_states():
    global previous_states
    
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

# 🚀 Exécution en boucle
if __name__ == "__main__":
    print("🚀 Démarrage de la supervision Centreon vers MQTT...")
    while True:
        check_and_send_states()
        time.sleep(CHECK_INTERVAL)
