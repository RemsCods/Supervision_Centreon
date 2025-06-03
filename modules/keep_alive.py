# keep_alive
# 🔄 Ce script envoie périodiquement les dernières valeurs reçues sur MQTT
# pour s'assurer que la connexion reste active.

import time  # ⏳ Gestion du temps
from modules.mqtt_utils import send_mqtt_message  # 📡 Fonction pour envoyer des messages MQTT
from modules.config import MQTT_ETAT_TOPIC, KEEP_ALIVE_INTERVAL  # 🔧 Configuration du topic MQTT et de l'intervalle de Keep-Alive

class KeepAlive:
    def __init__(self):
        """
        🛠️ Initialisation de la classe KeepAlive.
        - Stocke le timestamp du dernier message Keep-Alive envoyé.
        """
        self.dernier_temps_keep_alive = time.time()  # ⏳ Stockage du dernier envoi Keep-Alive

    def verifier_et_envoyer(self, tableau_etats_precedents):
        """
        📡 Vérifie si le délai Keep-Alive est dépassé et envoie les dernières valeurs reçues sur MQTT.
        :param tableau_etats_precedents: Dictionnaire contenant les derniers états connus.
        """
        temps_actuel = time.time()  # 🕒 Obtention de l'heure actuelle
        
        # ⏳ Vérifie si le délai défini par KEEP_ALIVE_INTERVAL est écoulé
        if temps_actuel - self.dernier_temps_keep_alive >= KEEP_ALIVE_INTERVAL:
            print("📡 Envoi des derniers états pour garder la connexion active")
            
            # 🔁 Parcours des dernières valeurs enregistrées et envoi sur MQTT
            for cle in tableau_etats_precedents:
                valeur = tableau_etats_precedents[cle]  # 🔎 Récupération de la valeur associée à la clé
                send_mqtt_message(f"{MQTT_ETAT_TOPIC}/{cle}", valeur)  # 🚀 Envoi via MQTT
            
            # 🔄 Mise à jour du dernier timestamp de Keep-Alive
            self.dernier_temps_keep_alive = temps_actuel
