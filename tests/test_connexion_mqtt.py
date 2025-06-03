import pytest
from unittest.mock import MagicMock, patch
from modules.connexion_mqtt import on_connect, on_message
import logging

# 🧪 Test du callback de connexion
def test_on_connect_logs_and_subscribes(caplog):
    caplog.set_level(logging.INFO)  # 🔧 Active la capture des logs niveau INFO
    client = MagicMock()
    userdata = None
    flags = None
    rc = 0
    properties = None

    # Simule MQTT_ENV_TOPIC avec deux topics
    with patch("modules.connexion_mqtt.MQTT_ENV_TOPIC", ["test/topic1", "test/topic2"]):
        on_connect(client, userdata, flags, rc, properties)
    
    client.subscribe.assert_any_call("test/topic1")
    client.subscribe.assert_any_call("test/topic2")
    assert client.subscribe.call_count == 2
    assert "✅ Connecté au broker MQTT" in caplog.text

# 🧪 Test du callback message avec topic connu (standard)
@patch("modules.connexion_mqtt.submit_results")
@patch("modules.connexion_mqtt.determine_status")
def test_on_message_known_topic_standard(mock_determine, mock_submit):
    mock_determine.return_value = 0  # Simule un statut OK

    client = MagicMock()
    userdata = None
    msg = MagicMock()
    msg.topic = "mqtt/env/temperature"
    msg.payload.decode.return_value = "42.0"

    with patch("modules.connexion_mqtt.CENTREON_SERVICES", {"temperature": "Température"}), \
         patch("modules.connexion_mqtt.SEUILS", {"temperature": {"min": 0, "max": 100}}):

        on_message(client, userdata, msg)

    mock_determine.assert_called_once_with(42.0, {"min": 0, "max": 100})
    mock_submit.assert_called_once_with(0, "Environnement", "Température", "Valeur : 42.0", "perf=42.0")

# 🧪 Test du callback message avec topic "eau"
@patch("modules.connexion_mqtt.submit_results")
@patch("modules.connexion_mqtt.determine_status_eau")
def test_on_message_known_topic_eau(mock_determine_eau, mock_submit):
    mock_determine_eau.return_value = 1  # Simule un statut WARNING

    client = MagicMock()
    userdata = None
    msg = MagicMock()
    msg.topic = "mqtt/env/eau"
    msg.payload.decode.return_value = "22.5"

    with patch("modules.connexion_mqtt.CENTREON_SERVICES", {"eau": "Niveau d'eau"}), \
         patch("modules.connexion_mqtt.SEUILS_eau", {"eau": {"min": 10, "max": 30}}):

        on_message(client, userdata, msg)

    mock_determine_eau.assert_called_once_with(22.5, {"min": 10, "max": 30})
    mock_submit.assert_called_once_with(1, "Environnement", "Niveau d'eau", "Valeur : 22.5", "perf=22.5")

# 🧪 Test du callback message avec topic inconnu
def test_on_message_unknown_topic(caplog):
    client = MagicMock()
    userdata = None
    msg = MagicMock()
    msg.topic = "mqtt/env/unknown"
    msg.payload.decode.return_value = "15.0"

    with patch("modules.connexion_mqtt.CENTREON_SERVICES", {}):
        on_message(client, userdata, msg)

    assert "⚠️ Topic non reconnu" in caplog.text

# 🧪 Test du callback message avec payload non convertible
def test_on_message_invalid_payload(caplog):
    client = MagicMock()
    userdata = None
    msg = MagicMock()
    msg.topic = "mqtt/env/temperature"
    msg.payload.decode.return_value = "not_a_number"

    with patch("modules.connexion_mqtt.CENTREON_SERVICES", {"temperature": "Température"}):
        on_message(client, userdata, msg)

    assert "❌ Erreur lors du traitement du message" in caplog.text
