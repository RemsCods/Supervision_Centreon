# 📡 Connexion MQTT : Publication et souscription aux messages

import logging
from modules.custom_logging import clean_old_logs  # 🧹 Nettoyage des anciens logs
import paho.mqtt.client as mqtt
from modules.compare import determine_status, determine_status_eau
from modules.config import MQTT_BROKER, MQTT_PORT, MQTT_ENV_TOPIC, CENTREON_SERVICES, SEUILS, SEUILS_eau
from modules.connexion_centreon import submit_results
from modules.custom_logging import clean_old_logs

# 📝 Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 🧹 Nettoyage des anciens logs
print(f"Nettoyage des logs")
clean_old_logs()

# 🔌 Affichage des paramètres MQTT
print(f"🔌 Configuration MQTT - Broker: {MQTT_BROKER}, Port: {MQTT_PORT}")
print(f"📡 Topics configurés: {MQTT_ENV_TOPIC}")

# 📡 Création du client MQTT
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# ✅ Callback lors de la connexion au broker MQTT
def on_connect(client, userdata, flags, rc, properties=None):
    msg = f"✅ Connecté au broker MQTT avec le code de retour: {rc}"
    print(msg)
    logging.info(msg)
    
    # 🔄 Abonnement aux topics configurés
    for topic in MQTT_ENV_TOPIC:
        client.subscribe(topic)
        print(f"📡 Abonné au topic: {topic}")
        logging.info(f"📡 Abonné au topic: {topic}")

# 📥 Callback lorsqu'un message est reçu sur un topic MQTT
def on_message(client, userdata, msg):
    try:
        value = float(msg.payload.decode())  # 📩 Conversion du message en float
        log_msg = f"📩 Nouvelle valeure sur le topic {msg.topic}: {value}"
        print(log_msg)
        logging.info(log_msg)

        # 🔍 Extraction du nom du paramètre à partir du topic
        topic_name = msg.topic.split("/")[-1]
        
        if topic_name in CENTREON_SERVICES:
            service_name = CENTREON_SERVICES[topic_name]
            
            # 🔄 Détermination du statut en fonction du paramètre reçu
            if topic_name == "eau":
                status = determine_status_eau(value, SEUILS_eau["eau"])
            else:
                status = determine_status(value, SEUILS[topic_name])
            
            # 📤 Envoi des résultats à Centreon
            host = "Environnement"
            output = f"Valeur : {value}"
            perfdata = f"perf={value}"
            print(f"📤 Envoi des résultats à Centreon - Status: {status}, Host: {host}, Service: {service_name}")
            submit_results(status, host, service_name, output, perfdata)
        else:
            print(f"⚠️ Topic non reconnu : {msg.topic}")
            logging.warning(f"⚠️ Topic non reconnu : {msg.topic}")
    except Exception as e:
        print(f"❌ Erreur lors du traitement du message : {e}")
        logging.error(f"❌ Erreur lors du traitement du message : {e}")

# 🔗 Configuration des callbacks MQTT
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# 🔄 Connexion au broker MQTT
print(f"🔄 Tentative de connexion au broker MQTT {MQTT_BROKER}:{MQTT_PORT}")
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
