# 📡 main_centreon_2_mqtt

import time
import os
import tracemalloc
import psutil
import gc
import logging
from modules.connexion_mqtt import mqtt_client              # 📡 Client MQTT pour la communication avec le broker
from modules.connexion_centreon import get_centreon_data    # 🔍 Fonction pour récupérer les données Centreon
from modules.compare import verifier_et_envoyer_etats, KeepAlive  # ✅ Vérification et envoi des états, gestion du Keep-Alive
from modules.config import CHECK_INTERVAL                   # 🔧 Intervalle entre chaque itération de vérification

logging.basicConfig(
    filename="/home/user/script_centreon/supervision.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def main(max_iterations=None, debug=False):
    if not debug:
        print("🚀 Démarrage de la supervision Centreon vers MQTT...")

    mqtt_client.loop_start()
    keep_alive = KeepAlive()
    tracemalloc.start()
    process = psutil.Process(os.getpid())
    iteration = 0

    while True:
        try:
            tableau_etats_precedents = verifier_et_envoyer_etats()
            keep_alive.verifier_et_envoyer(tableau_etats_precedents)

            if iteration % 10 == 0 and not debug:
                mem = process.memory_info().rss / (1024 ** 2)
                print(f"📊 Mémoire utilisée : {mem:.2f} Mo")

                snapshot = tracemalloc.take_snapshot()
                top_stats = snapshot.statistics('lineno')

                print("[TOP 5 CONSOMMATEURS DE MÉMOIRE]")
                for stat in top_stats[:5]:
                    print(stat)

                logging.info("[TOP 5 CONSOMMATEURS DE MÉMOIRE]")
                for stat in top_stats[:5]:
                    print(stat)
                    logging.info(stat)
                # 🧹 Nettoyage mémoire explicite (optionnel mais utile en debug)
                gc.collect()

            iteration += 1
            if max_iterations is not None and iteration >= max_iterations:
                break

        except Exception as e:
            print(f"❌ Une erreur s'est produite : {e}")

            logging.error(f"❌ Une erreur s'est produite : {e}")
        # ⏳ Pause avant la prochaine itération pour éviter une surcharge inutile
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
