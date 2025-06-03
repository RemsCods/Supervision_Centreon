import pytest
from unittest.mock import patch, MagicMock, call  # 🔧 Importation des outils de mock pour simuler les fonctions et objets
from modules.keep_alive import KeepAlive  # 📡 Importation de la classe KeepAlive
from modules.config import MQTT_ETAT_TOPIC  # 🔧 Importation du topic MQTT utilisé

# ✅ Test de la méthode `verifier_et_envoyer` avec un envoi normal
@patch('modules.keep_alive.send_mqtt_message')  # 📡 Simulation de l'envoi de message MQTT
@patch('modules.keep_alive.time.time', side_effect=[0, 100])  # ⏳ Simulation du temps écoulé (passage de 0 à 100 sec)
def test_verifier_et_envoyer(mock_time, mock_send_mqtt):
    keep_alive = KeepAlive()  # 🔄 Création d'une instance de KeepAlive
    
    # 🔢 Définition d'un état avec des valeurs à envoyer
    etats = {"hote": 0, "service": 0, "env": 0}
    keep_alive.verifier_et_envoyer(etats)  # 📤 Vérification et envoi des états MQTT
    
    # ✅ Vérification que send_mqtt_message a été appelé correctement
    expected_calls = [
        call(f"{MQTT_ETAT_TOPIC}/hote", 0),
        call(f"{MQTT_ETAT_TOPIC}/service", 0),
        call(f"{MQTT_ETAT_TOPIC}/env", 0)
    ]
    assert mock_send_mqtt.call_count == 3  # 🔍 Vérifie que la fonction a bien été appelée 3 fois
    mock_send_mqtt.assert_has_calls(expected_calls, any_order=True)  # 🔍 Vérifie que les appels correspondent aux attentes

# ❌ Test de gestion d'erreur lors de l'envoi MQTT
@patch('modules.keep_alive.send_mqtt_message')  # 📡 Simulation de l'envoi de message MQTT
@patch('modules.keep_alive.time.time', side_effect=[0, 100])  # ⏳ Simulation du temps écoulé (passage de 0 à 100 sec)
def test_verifier_et_envoyer_error_handling(mock_time, mock_send_mqtt):
    keep_alive = KeepAlive()  # 🔄 Création d'une instance de KeepAlive
    
    # 🚨 Simulation d'une erreur lors de l'envoi d'un message MQTT
    mock_send_mqtt.side_effect = Exception("MQTT Error")  
    
    # ⚠️ Vérifie que l'erreur est bien levée lors de l'envoi
    with pytest.raises(Exception) as exc_info:
        keep_alive.verifier_et_envoyer({"hote": 0, "service": 0, "env": 0})
    assert str(exc_info.value) == "MQTT Error"  # ✅ Vérification du message d'erreur attendu
