#Log Cleanup
from modules.config import LOG_FILE, LOG_RETENTION_MINUTES  # Importation des variables de configuration
import logging  # Module pour la gestion des logs
from datetime import datetime, timedelta  # Modules pour la gestion des dates et durées

# 📄 Configuration du logging :
# - Écriture des logs dans le fichier défini par LOG_FILE
# - Niveau INFO pour enregistrer les événements importants
# - Format des logs : 'YYYY-MM-DD HH:MM:SS,ms - Message'
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s')

# 🧹 Fonction pour nettoyer les anciens logs en fonction d'une durée de rétention

def clean_old_logs():
    now = datetime.now()  # 📆 Récupération de l'heure actuelle
    
    # 📂 Ouverture du fichier de logs en mode lecture
    with open(LOG_FILE, "r") as f:
        lines = f.readlines()  # 📖 Lecture de toutes les lignes du fichier
    
    # ✏️ Réouverture du fichier en mode écriture (efface le contenu existant)
    with open(LOG_FILE, "w") as f:
        for line in lines:  # 🔄 Parcours de chaque ligne du fichier de logs
            try:
                # ⏳ Extraction de la date du log à partir du début de la ligne
                log_time = datetime.strptime(line.split(' - ')[0], '%Y-%m-%d %H:%M:%S,%f')
                
                # 🔍 Vérification si le log est toujours valide selon la durée de rétention
                if now - log_time < timedelta(minutes=LOG_RETENTION_MINUTES):
                    f.write(line)  # ✅ Conserver la ligne si elle est encore valide
            except ValueError:
                # ⚠️ Ignorer les lignes mal formatées (ex : ligne vide, erreur de parsing...)
                pass
