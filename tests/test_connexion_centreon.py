import pytest
from unittest.mock import patch, MagicMock

import requests
from modules.connexion_centreon import get_centreon_token, get_centreon_data, submit_results

# 🛠️ Test de la récupération du token Centreon
@patch('modules.connexion_centreon.requests.post')  # 🎭 On remplace la requête HTTP POST par une version factice
def test_get_centreon_token(mock_post):
    # ✅ Test de succès : simulation d'une réponse correcte de l'API
    mock_response = MagicMock()  # 📦 Création d'un objet mocké pour la réponse
    mock_response.json.return_value = {"authToken": "fake_token"}  # 📜 Simulation d'un token de réponse
    mock_post.return_value = mock_response  # 🔄 On configure le mock pour qu'il retourne cette réponse

    token = get_centreon_token()  # 🔑 On appelle la fonction
    assert token == "fake_token"  # ✅ On vérifie que le token retourné est correct
    mock_post.assert_called_once()  # 🔍 Vérifie que la requête POST a bien été appelée une seule fois

    # ❌ Test d'erreur : simulation d'une panne de connexion
    mock_post.reset_mock()  # 🔄 On réinitialise le mock pour un nouveau test
    mock_post.side_effect = requests.RequestException("Connection failed")  # ⚠️ Simulation d'une erreur lors de l'appel API

    token = get_centreon_token()
    assert token is None  # ✅ Vérifie que la fonction retourne None en cas d'erreur

    # ❌ Test d'erreur : simulation d'une réponse avec un statut d'erreur
    mock_post.reset_mock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    mock_post.return_value = mock_response

    token = get_centreon_token()
    assert token is None  # ✅ Vérifie que la fonction retourne None en cas d'erreur

# 🛠️ Test de la récupération des données Centreon
@patch('modules.connexion_centreon.requests.get')  # 🎭 On remplace la requête HTTP GET par une version factice
@patch('modules.connexion_centreon.get_centreon_token', return_value="fake_token")  # 🎭 On simule la récupération du token
def test_get_centreon_data(mock_get_token, mock_get):
    # ✅ Test de succès : simulation d'une réponse correcte de l'API
    mock_response = MagicMock()  # 📦 Création d'un objet mocké
    mock_response.json.return_value = [{"state": 0}]  # 📜 Données factices retournées par l'API
    mock_get.return_value = mock_response  # 🔄 On configure le mock pour retourner cette réponse

    data = get_centreon_data("some_endpoint")  # 📡 On appelle la fonction
    assert data == [{"state": 0}]  # ✅ Vérification du retour
    mock_get.assert_called_once()  # 🔍 Vérifie que la requête GET a été appelée une seule fois

    # 🔄 Test avec plusieurs états possibles
    mock_get.reset_mock()
    mock_response.json.return_value = [{"state": 1}, {"state": 2}]  # 📜 Simulation de plusieurs états
    data = get_centreon_data("some_endpoint")
    assert data == [{"state": 1}, {"state": 2}]  # ✅ Vérification des valeurs

    # ❌ Test d'erreur : simulation d'une erreur API
    mock_get.reset_mock()
    mock_get.side_effect = requests.RequestException("API Error")  # ⚠️ Simulation d'une erreur lors de l'appel API

    data = get_centreon_data("some_endpoint")
    assert data is None  # ✅ Vérifie que la fonction retourne None en cas d'erreur

    # ❌ Test d'erreur : simulation d'une réponse avec un statut d'erreur
    mock_get.reset_mock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_get.return_value = mock_response

    data = get_centreon_data("some_endpoint")
    assert data is None  # ✅ Vérifie que la fonction retourne None en cas d'erreur

# 🛠️ Test de la soumission des résultats à Centreon
@patch('modules.connexion_centreon.requests.post')  # 🎭 On remplace la requête HTTP POST par une version factice
@patch('modules.connexion_centreon.get_centreon_token', return_value="fake_token")  # 🎭 On simule la récupération du token
def test_submit_results(mock_get_token, mock_post):
    # ✅ Test de succès : simulation d'une réponse correcte de l'API
    mock_response = MagicMock()  # 📦 Création d'un objet mocké pour la réponse
    mock_post.return_value = mock_response  # 🔄 On configure le mock pour qu'il retourne cette réponse

    result = submit_results(0, "host", "service", "output", "perfdata")  # 📤 On appelle la fonction
    assert result is True  # ✅ On vérifie que la fonction retourne True en cas de succès
    mock_post.assert_called_once()  # 🔍 Vérifie que la requête POST a bien été appelée une seule fois

    # ❌ Test d'erreur : simulation d'une erreur API
    mock_post.reset_mock()
    mock_post.side_effect = requests.RequestException("API Error")  # ⚠️ Simulation d'une erreur lors de l'appel API

    result = submit_results(0, "host", "service", "output", "perfdata")
    assert result is False  # ✅ Vérifie que la fonction retourne False en cas d'erreur

    # ❌ Test d'erreur : simulation d'une réponse avec un statut d'erreur
    mock_post.reset_mock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_post.return_value = mock_response

    result = submit_results(0, "host", "service", "output", "perfdata")
    assert result is False  # ✅ Vérifie que la fonction retourne False en cas d'erreur
