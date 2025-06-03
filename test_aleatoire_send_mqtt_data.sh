#!/bin/bash

# Configuration MQTT
BROKER="192.168.17.159"
PORT=1883
CLIENT_ID="test_publisher"

# Fonction pour générer des données de température
generate_temperature() {
    temperature=$(shuf -i 20-45 -n 1)
    echo "$temperature"
}

# Fonction pour générer des données de gaz
generate_gaz() {
    gaz_level=$(shuf -i 0-3 -n 1)
    echo "$gaz_level"
}

# Fonction pour générer des données d'eau
generate_water() {
    water_level=$(shuf -i 2000-3000 -n 1)
    echo "$water_level"
}

# Boucle principale
while true; do
    # Envoyer les données de température
    temp_data=$(generate_temperature)
    echo "Envoi des données de température: $temp_data"
    mosquitto_pub -h $BROKER -p $PORT -i $CLIENT_ID -t "env/temperature" -m "$temp_data"
    
    # Envoyer les données de gaz
    gaz_data=$(generate_gaz)
    echo "Envoi des données de gaz: $gaz_data"
    mosquitto_pub -h $BROKER -p $PORT -i $CLIENT_ID -t "env/gaz" -m "$gaz_data"
    
    # Envoyer les données d'eau
    water_data=$(generate_water)
    echo "Envoi des données d'eau: $water_data"
    mosquitto_pub -h $BROKER -p $PORT -i $CLIENT_ID -t "env/eau" -m "$water_data"
    
    # Attendre 10 secondes
    sleep 50
done 