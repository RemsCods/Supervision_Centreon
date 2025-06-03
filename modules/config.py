#Config et Identifiants
import os
# 🔧 Config Centreon
IP_CENTREON = "192.168.17.159"
USER = "userapi"
PASSWORD = "2DmqrLt6JP?9"

# 📡 Config MQTT

# 👉 Broker par défaut (utilisé hors CI/CD)
DEFAULT_MQTT_BROKER = "192.168.17.159"

# 👉 Si la variable d'environnement MQTT_BROKER est définie, on l'utilise.
# Sinon, si on détecte GitLab CI, on force localhost.
# Sinon on utilise le broker par défaut.
if "MQTT_BROKER" in os.environ:
    MQTT_BROKER = os.getenv("MQTT_BROKER")
elif os.getenv("GITLAB_CI") == "true":
    MQTT_BROKER = "localhost"
else:
    MQTT_BROKER = DEFAULT_MQTT_BROKER

# Port MQTT (par défaut 1883)
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
# Topics MQTT
MQTT_ETAT_TOPIC = "etat"  # résultat final à afficher pour l’ESP
MQTT_ENV_TOPIC = ["centreon/+", "env/+"]

# ⏳ Intervalles
CHECK_INTERVAL = 10
KEEP_ALIVE_INTERVAL = 50  # Doit être inferieur à 60

# Seuils
SEUILS = {
    "temperature": {"ok": 30, "warning": 35, "critical": 35},
    "humidite": {"ok": 65, "warning": 75, "critical": 75},
    "gaz": {"ok": 3, "warning": 5, "critical": 6},
}
SEUILS_eau = {
    "eau": {"ok": 4095, "warning": 3200, "critical": 3000}
}

# 🛠️ Mapping topic/service
CENTREON_SERVICES = {
    "temperature": "env_temp",
    "humidite": "env_hum",
    "gaz": "env_gaz",
    "eau": "env_eau"
}

# ✅ Endpoints à surveiller pour keep_alive
CENTREON_ENDPOINTS = ["hosts", "services", "status"]

# 📝 Config Logs
LOG_FILE = "supervision.log"
LOG_RETENTION_MINUTES = 2880  # 2 pour les tests (2 jours = 2880)