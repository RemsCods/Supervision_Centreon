import requests
import time

# 🔧 Config Centreon
IP_CENTREON = "192.168.17.159"
USER = "userapi"
PASSWORD = "2DmqrLt6JP?9"

# 📡 Obtenir le token d'authentification
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

    # Envoi de la requête POST
    response = requests.post(url, json=results, headers=headers)
    if response.status_code == 200:
        print(f"✅ Résultat envoyé pour {host} - {service} avec l'état {status}.")
    else:
        print(f"❌ Erreur lors de l'envoi des résultats pour {host} - {service}.")

# 🚀 Exemple d'utilisation
if __name__ == "__main__":
    # Envoi d'un état pour la temp
    submit_results(0, "Apache", "test_restapi", "Stat is OK", "perf=20")

    # Envoi d'un état l'hum
    #submit_results(1, "Apache", "test_restapi", "Stat is WARNING", "perf=20")

    # Envoi d'un état gaz
    #submit_results(2, "Apache", "test_restapi", "Stat is CRITICAL", "perf=20")
