import unittest
from unittest.mock import patch, MagicMock
import threading
import time

class TestMainCentreon2MQTT(unittest.TestCase):

    @patch("main_centreon_2_mqtt.mqtt_client")
    @patch("main_centreon_2_mqtt.verifier_et_envoyer_etats")
    @patch("main_centreon_2_mqtt.KeepAlive")
    @patch("main_centreon_2_mqtt.tracemalloc")
    @patch("main_centreon_2_mqtt.psutil.Process")
    @patch("main_centreon_2_mqtt.gc")
    def test_main_loop_runs_once(
        self,
        mock_gc,
        mock_process,
        mock_tracemalloc,
        mock_keep_alive_class,
        mock_verifier,
        mock_mqtt_client
    ):
        # Mock configuration
        mock_process_instance = MagicMock()
        mock_process.return_value = mock_process_instance
        mock_process_instance.memory_info.return_value.rss = 10485760  # 10 Mo
        mock_tracemalloc.take_snapshot.return_value.statistics.return_value = []

        mock_keep_alive = MagicMock()
        mock_keep_alive_class.return_value = mock_keep_alive

        mock_verifier.return_value = [{"host": "srv", "status": "OK"}]
        mock_mqtt_client.loop_start.return_value = None

        # Import dans le thread
        import main_centreon_2_mqtt

        # Lancer le main avec une seule itération
        thread = threading.Thread(target=main_centreon_2_mqtt.main, kwargs={"max_iterations": 1, "debug": True})
        thread.start()
        thread.join(timeout=5)

        self.assertFalse(thread.is_alive(), "Le thread n'a pas terminé correctement")

        # Vérifications des appels
        mock_verifier.assert_called_once()
        mock_keep_alive.verifier_et_envoyer.assert_called_once()

if __name__ == "__main__":
    unittest.main()
