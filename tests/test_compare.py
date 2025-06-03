import pytest
from unittest.mock import patch, MagicMock
from modules.compare import determine_status, determine_status_eau, verifier_et_envoyer_etats

@patch('modules.compare.get_centreon_data')
@patch('modules.compare.send_mqtt_message')
def test_verifier_et_envoyer_etats(mock_send_mqtt, mock_get_centreon_data):
    # Test avec tous les états OK
    mock_get_centreon_data.return_value = [{"state": 0}]  # Un seul appel avec tous les états
    result = verifier_et_envoyer_etats()
    assert result == {"hote": 0, "service": 0, "env": 0}
    mock_send_mqtt.assert_called()
    
    # Test avec un hôte en warning
    mock_get_centreon_data.return_value = [{"state": 1}]
    result = verifier_et_envoyer_etats()
    assert result == {"hote": 1, "service": 1, "env": 0}  # Le service prend l'état de l'hôte
    
    # Test avec un service critique
    mock_get_centreon_data.return_value = [{"state": 2}]
    result = verifier_et_envoyer_etats()
    assert result == {"hote": 2, "service": 2, "env": 0}  # L'état env reste à 0 car pas de service environnemental

def test_determine_status():
    seuils = {"ok": 10, "warning": 20}
    
    # Test des limites exactes
    assert determine_status(10, seuils) == 0  # OK exact
    assert determine_status(20, seuils) == 1  # Warning exact
    
    # Test des valeurs intermédiaires
    assert determine_status(5, seuils) == 0   # OK
    assert determine_status(15, seuils) == 1  # Warning
    assert determine_status(25, seuils) == 2  # Critique
    
    # Test des valeurs négatives
    assert determine_status(-5, seuils) == 2  # Critique

def test_determine_status_eau():
    seuils = {"ok": 10, "warning": 5}
    
    # Test des limites exactes
    assert determine_status_eau(10, seuils) == 0  # OK exact
    assert determine_status_eau(5, seuils) == 1   # Warning exact
    
    # Test des valeurs intermédiaires
    assert determine_status_eau(15, seuils) == 0  # OK
    assert determine_status_eau(7, seuils) == 1   # Warning
    assert determine_status_eau(2, seuils) == 2   # Critique
    
    # Test des valeurs négatives
    assert determine_status_eau(-5, seuils) == 2  # Critique