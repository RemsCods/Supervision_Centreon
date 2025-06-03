# Supervision_Centreon
Supervision de serveur et environnement avec Centreon via SNMP v3 et des sous-systemes embarqués via MQTT.
Le script python récupére les données dans MQTT et les pousses dans centreon dans les topics scpécifiques. (ex : env/temperature, env/humidite...)
Le script va ensuite chercher sur centreon l'état de tous les hotes et service pour calculer un état synthétique qui sera ensuite envoyé sur MQTT dans des topics spécifiques (ex : etat/service...)

Lien de procédure d'installation pour Centreon et configuration SNMP : 
https://docs.google.com/document/d/1lfm9cOhnyu1Jpp6ny9eD0e2gsDgZnVbmcobVvDr6qoc/edit?usp=sharing 

Ce projet à été fais dans le cadre d'un projet d'étude pour la formation BTS CIEL 2025.
