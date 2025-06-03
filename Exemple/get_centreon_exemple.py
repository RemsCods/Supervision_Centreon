#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#get data from centreon to post in mqtt


import requests

# données authentification
payload = {'username': 'userapi', 'password': '2DmqrLt6JP?9'}

#requête authentification
r = requests.post('http://192.168.17.159/centreon/api/index.php?action=authenticate', data=payload)

#on récupère le token
json = r.json()

#initialisation du header pour le token
headers = dict()
headers['centreon-auth-token'] = json['authToken']

#requête liste des hôtes
r = requests.get('http://192.168.17.159/centreon/api/index.php?object=centreon_realtime_hosts&action=list',headers=headers)

#résultat complet du fichier JSON brut
print (r.text)

#résultat partiel
hote = r.json()

print ("Le premier hote est " + hote[0]['name'])
