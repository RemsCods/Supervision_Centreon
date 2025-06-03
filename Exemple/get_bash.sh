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

#on recupere le nombre d host down
NB_HOST=`$CURL -s "http://$IP_CENTREON/centreon/api/index.php?object=centreon_realtime_hosts&action=list&viewType=unhandled&status=Down" -H 'Content-Type: application/json' -H 'centreon-auth-token: '$TOKEN'' | $JQ 'length'`

#on recupere le nombre de service en crirical
NB_SERVICE=`$CURL -s "http://$IP_CENTREON/centreon/api/index.php?object=centreon_realtime_services&action=list&viewType=unhandled&status=critical" -H 'Content-Type: application/json' -H 'centreon-auth-token: '$TOKEN'' | $JQ 'length'`

#on affiche nombre d host et service en erreur
echo "Critical hosts    : "$NB_HOST
echo "Critical services : "$NB_SERVICE
