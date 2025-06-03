#compare_send_data
#compare host et service avec l ancien résultat pour voir si il y a du changement et l'envois
from modules.connexion_centreon import get_centreon_data  # 🔌 Import de la fonction pour récupérer les données Centreon
from modules.mqtt_utils import send_mqtt_message  # 📡 Import de la fonction pour envoyer un message MQTT
from modules.config import MQTT_ETAT_TOPIC, KEEP_ALIVE_INTERVAL  # 🔧 Import des constantes de configuration
import time
import logging

# 🌐 Stockage des états précédents pour détecter les changements
tableau_etats_precedents = {"hote": None, "service": None, "env": None}

class KeepAlive:
    def __init__(self):
        self.dernier_envoi = 0  # ⏳ Stocke le dernier envoi pour éviter un envoi trop fréquent
        self.intervalle = KEEP_ALIVE_INTERVAL  # ⏲️ Intervalle entre chaque Keep-Alive

    def verifier_et_envoyer(self, etats):
        temps_actuel = time.time()  # ⏰ Récupère le temps actuel
        
        # ⏳ Vérifie si l'intervalle est écoulé
        if temps_actuel - self.dernier_envoi >= self.intervalle:
            for cle, etat in etats.items():
                if etat is not None:
                    print(f"💓 Keep-Alive envoyé: {MQTT_ETAT_TOPIC}/{cle} → {etat}")
                    send_mqtt_message(f"{MQTT_ETAT_TOPIC}/{cle}", etat)  # 📡 Envoie l'état via MQTT
                    log_keepalive = f"📤 {MQTT_ETAT_TOPIC}/{cle} → {etat}"
                    print(log_keepalive)
                    logging.info(log_keepalive)
            self.dernier_envoi = temps_actuel  # 🔄 Met à jour le dernier envoi

def verifier_et_envoyer_etats():
    global tableau_etats_precedents  # 🔄 Garde la référence aux états précédents

    # 🔍 Récupération des données Centreon
    data = get_centreon_data()
    if not data:
        print("❌ Aucune donnée récupérée de Centreon")
        return tableau_etats_precedents

    # 🔍 Déterminer l'état global des hôtes, services et environnement
    etat_global_hote = max((h.get("state", 3) for h in data), default=0)  # 🏠 État le plus critique des hôtes (h pour hote)
    etat_global_service = max((s.get("state", 3) for s in data), default=0)  # 🛠️ État le plus critique des services (s pour service)
    etat_global_env = max((s.get("state", 3) for s in data if s.get("name", "").startswith("Environnement")), default=0)  # 🌍 État environnemental

    # 🔄 Vérification des changements et envoi MQTT si nécessaire
    for cle, nouvel_etat in [("hote", etat_global_hote), ("service", etat_global_service), ("env", etat_global_env)]:
        if tableau_etats_precedents[cle] != nouvel_etat:  # ⚠️ Compare avec l'état précédent
            print(f"📡 Changement détecté: {MQTT_ETAT_TOPIC}/{cle} → {nouvel_etat}")
            send_mqtt_message(f"{MQTT_ETAT_TOPIC}/{cle}", nouvel_etat)  # 📡 Envoie le nouvel état
            tableau_etats_precedents[cle] = nouvel_etat  # 🔄 Mise à jour de l'état précédent
    
    return tableau_etats_precedents  # ✅ Retourne les états mis à jour

# 🚦 Déterminer l'état en fonction des seuils (lower is better)
def determine_status(value, seuils):
    if value < 0:  # ⚠️ Valeurs négatives = état critique
        return 2
    if value <= seuils["ok"]:
        return 0  # ✅ OK
    elif value <= seuils["warning"]:
        return 1  # ⚠️ Warning
    return 2  # 🚨 Critique si au-delà des seuils définis

# 🚦 Déterminer l'état spécifique à l'eau (higher is better)
def determine_status_eau(value, seuils):
    if value >= seuils["ok"]:
        return 0  # ✅ Bon niveau d'eau
    elif value >= seuils["warning"]:
        return 1  # ⚠️ Niveau intermédiaire
    return 2  # 🚨 Niveau trop bas
