import requests
import paho.mqtt.client as mqtt

# 🔧 Config Centreon
IP_CENTREON = "192.168.17.159"
USER = "userapi"
PASSWORD = "2DmqrLt6JP?9"

# 📡 Config MQTT
MQTT_BROKER = "192.168.17.159"  # Adresse du broker MQTT
MQTT_PORT = 1883
MQTT_BASE_TOPIC = "centreon"

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

# 🖥️ Récupération et envoi des hôtes
def process_hosts():
    hosts = get_centreon_data("centreon_realtime_hosts")
    print(f"📡 Nombre total d'hôtes : {len(hosts)}")

    for host in hosts:
        host_name = host.get("name", "unknown")
        host_state = host.get("state", 3)

        # Envoi sur MQTT
        mqtt_topic = f"{MQTT_BASE_TOPIC}/host/{host_name}"
        print(f"📡 Envoi MQTT : {mqtt_topic} → {host_state}")
        mqtt_client.publish(mqtt_topic, host_state)

# 🔧 Récupération et envoi des services
def process_services():
    services = get_centreon_data("centreon_realtime_services")
    print(f"🔧 Nombre total de services : {len(services)}")

    for service in services:
        service_name = service.get("description", "unknown")
        service_state = service.get("state", 3)

        # Envoi sur MQTT
        mqtt_topic = f"{MQTT_BASE_TOPIC}/service/{service_name}"
        print(f"📡 Envoi MQTT : {mqtt_topic} → {service_state}")
        mqtt_client.publish(mqtt_topic, service_state)

# 🚀 Exécution
if __name__ == "__main__":
    process_hosts()
    process_services()
    mqtt_client.disconnect()
    print("✅ Données envoyées avec succès !")
