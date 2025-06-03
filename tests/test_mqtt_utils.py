from unittest.mock import patch, MagicMock
from modules.mqtt_utils import send_mqtt_message
from modules.config import MQTT_BROKER, MQTT_PORT
import pytest

@patch("modules.mqtt_utils.mqtt_client")
def test_send_mqtt_message_success(mock_client):
    mock_client.connect.return_value = 0
    mock_client.publish.return_value = MagicMock(rc=0)
    
    send_mqtt_message("topic/test", "payload")
    
    mock_client.connect.assert_called_once_with(MQTT_BROKER, MQTT_PORT, 60)
    mock_client.publish.assert_called_once_with("topic/test", "payload")
    mock_client.disconnect.assert_called_once()

@patch("modules.mqtt_utils.mqtt_client")
def test_send_mqtt_message_connection_failure(mock_client):
    mock_client.connect.side_effect = Exception("Connection failed")
    
    with pytest.raises(Exception) as exc_info:
        send_mqtt_message("topic/test", "payload")
    
    # Vérifie que l'exception est bien levée
    assert str(exc_info.value) == "Connection failed"
    
    # Vérifie que disconnect est quand même appelé
    mock_client.disconnect.assert_called_once()
