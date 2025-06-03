# Utiliser l'image officielle Mosquitto comme base
FROM eclipse-mosquitto:latest

# Copier le fichier de configuration dans l'image
COPY mosquitto.conf /mosquitto/config/mosquitto.conf

# Définir le point d'entrée par défaut
CMD ["/usr/sbin/mosquitto", "-c", "/mosquitto/config/mosquitto.conf"]