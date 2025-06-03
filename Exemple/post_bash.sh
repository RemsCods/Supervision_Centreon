#!/bin/bash
# etat_monitoring.sh
# version 2.00
# date 05/02/2025

CURL="/usr/bin/curl"
JQ="/usr/bin/jq"
SED="/bin/sed"

#remplacer par les bonnes valeurs
IP_CENTREON="192.168.17.159"
USER="userapi"
PASSWORD="2DmqrLt6JP?9"

#on recupere le token dans l api
TOKEN=`$CURL -s -d "username=$USER&password=$PASSWORD" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://$IP_CENTREON/centreon/api/index.php?action=authenticate | $JQ '.["authToken"]'| $SED -e 's/^"//' -e 's/"$//'`

#untag la ligne pour afficher le token
#echo $TOKEN

#commande post warning
#curl -X POST 'http://192.168.17.159/centreon/api/index.php?action=submit&object=centreon_submit_results' -H 'Content-Type: application/json'  -H 'centreon-auth-token: '$TOKEN'' -d '{ "results": [{"updatetime": "'`date +%s`'","host": "Apache","service": "test_restapi","status": "1","output": "The service is in WARNING state","perfdata": "perf=20" }]}'


#commande post critical
#curl -X POST 'http://192.168.17.159/centreon/api/index.php?action=submit&object=centreon_submit_results' -H 'Content-Type: application/json'  -H 'centreon-auth-token: '$TOKEN'' -d '{ "results": [{"updatetime": "'`date +%s`'","host": "Apache","service": "test_restapi","status": "2","output": "The service is in CRITICAL state","perfdata": "perf=20" }]}'


#commande post ok
#curl -X POST 'http://192.168.17.159/centreon/api/index.php?action=submit&object=centreon_submit_results' -H 'Content-Type: application/json'  -H 'centreon-auth-token: '$TOKEN'' -d '{ "results": [{"updatetime": "'`date +%s`'","host": "Apache","service": "test_restapi","status": "0","output": "The service is in OK state","perfdata": "perf=20" }]}'
