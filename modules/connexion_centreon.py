import logging   # 📜 Gestion des logs pour enregistrer les erreurs et informations utiles
import time      # ⏳ Utilisé pour obtenir l'heure actuelle lors de l'envoi des résultats
import requests  # 🌐 Permet de faire des requêtes HTTP vers l'API Centreon
import os        # 📂 Gestion des chemins de fichiers (ex: certificat SSL)
#import urllib3   # ⚠️ Permet de désactiver les avertissements liés au SSL non sécurisé
from modules.config import IP_CENTREON, USER, PASSWORD  # 🔑 Variables de configuration pour Centreon

# 🚫 Désactiver les avertissements SSL pour éviter le spam dans les logs
#urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 📌 Définition du chemin vers le certificat SSL utilisé pour les requêtes sécurisées
#cert_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "centreon.pem") #utilise le centreon.pem
cert_path = os.getenv("CENTREON_CERT_PATH", "/etc/ssl/certs/centreon7.crt") #utilise le certificat de la vm

# 🔑 Fonction pour obtenir le token d'authentification auprès de Centreon
def get_centreon_token():
    url = f"https://{IP_CENTREON}/centreon/api/index.php?action=authenticate"  # 🔗 URL de connexion
    headers = {"Content-Type": "application/x-www-form-urlencoded"}  # 📩 Type de contenu envoyé
    payload = {"username": USER, "password": PASSWORD}  # 👤 Informations de connexion
    
    try:
        #print(f"🔑 Tentative de connexion à Centreon avec le certificat : {cert_path}")  # Debug
        response = requests.post(url, data=payload, headers=headers, verify=cert_path)  # 📡 Envoi de la requête
        #print(f"📡 Code de réponse : {response.status_code}")  # Debug : afficher le code retour HTTP
        #print(f"📡 Réponse du serveur : {response.text}")  # Debug : afficher la réponse complète
        response.raise_for_status()  # 🛑 Lève une exception si erreur HTTP
        return response.json().get("authToken")  # 🔑 Extraction du token depuis la réponse JSON
    except requests.RequestException as e:
        print(f"❌ Erreur lors de l'authentification : {e}")  # ❗ Affichage de l'erreur
        print(f"📡 Réponse du serveur : {response.text if 'response' in locals() else 'Pas de réponse'}")
        return None  # 🚫 Retourne None en cas d'échec

# 📡 Fonction pour récupérer des données depuis un endpoint Centreon
def get_centreon_data(endpoint=None):
    token = get_centreon_token()  # 🔑 Récupération du token
    if not token:
        print("❌ Impossible d'obtenir le token d'authentification")
        return None  # 🚫 Sortie immédiate en cas d'échec
    
    if endpoint is None:
        endpoint = "centreon_realtime_services"  # 📌 Endpoint par défaut
    
    url = f"https://{IP_CENTREON}/centreon/api/index.php?object={endpoint}&action=list"  # 🔗 URL de récupération
    headers = {"Content-Type": "application/json", "centreon-auth-token": token}  # 🔑 Authentification
    
    try:
        #print(f"🔍 Récupération des données avec le certificat : {cert_path}")  # Debug
        response = requests.get(url, headers=headers, verify=cert_path)  # 📡 Envoi de la requête GET
        #print(f"📡 Code de réponse : {response.status_code}")  # Debug : code HTTP
        #print(f"📡 Réponse du serveur : {response.text}")  # Debug : réponse complète
        response.raise_for_status()  # 🛑 Vérification des erreurs HTTP
        return response.json()  # 📊 Retourne les données JSON reçues
    except requests.RequestException as e:
        print(f"❌ Erreur lors de la récupération des données : {e}")  # ❗ Affichage de l'erreur
        print(f"📡 Réponse du serveur : {response.text if 'response' in locals() else 'Pas de réponse'}")
        return None  # 🚫 Retourne None en cas d'échec

# 📡 Fonction pour soumettre des résultats de monitoring à Centreon
def submit_results(status, host, service, output, perfdata):
    token = get_centreon_token()  # 🔑 Récupération du token
    if not token:
        print("❌ Impossible d'obtenir le token d'authentification")
        return False  # 🚫 Sortie immédiate en cas d'échec
    
    url = f"https://{IP_CENTREON}/centreon/api/index.php?action=submit&object=centreon_submit_results"  # 🔗 URL d'envoi
    headers = {"Content-Type": "application/json", "centreon-auth-token": token}  # 🔑 Authentification
    current_time = int(time.time())  # ⏳ Obtention du timestamp actuel
    payload = {
        "results": [
            {
                "updatetime": current_time,  # 🕒 Heure de mise à jour
                "host": host,                # 🏠 Nom de l'hôte
                "service": service,          # 🔧 Nom du service
                "status": status,            # 📊 État du service (OK, WARNING, CRITICAL, UNKNOWN)
                "output": output,            # 📝 Message affiché sur Centreon
                "perfdata": perfdata         # 📊 Données de performance associées
            }
        ]
    }
    
    try:
        #print(f"📤 Envoi des résultats avec le certificat : {cert_path}")  # Debug
        response = requests.post(url, json=payload, headers=headers, verify=cert_path)  # 📡 Envoi des données
        #print(f"📡 Code de réponse : {response.status_code}")  # Debug : code HTTP
        #print(f"📡 Réponse du serveur : {response.text}")  # Debug : réponse complète
        response.raise_for_status()  # 🛑 Vérification des erreurs HTTP
        return True  # ✅ Succès
    except requests.RequestException as e:
        print(f"❌ Erreur lors de l'envoi des résultats : {e}")  # ❗ Affichage de l'erreur
        print(f"📡 Réponse du serveur : {response.text if 'response' in locals() else 'Pas de réponse'}")
        return False  # 🚫 Échec de l'envoi
