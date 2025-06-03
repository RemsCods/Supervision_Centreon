#!/bin/bash
echo "🚀 Lancement du déploiement du script Centreon..."

# 1. Mises à jour système
echo "🛠️ Mise à jour du système..."
sudo apt update && sudo apt upgrade -y

# 2. Installation des dépendances nécessaires
echo "📦 Installation de Python et des outils..."
sudo apt install -y python3 python3-venv python3-pip git

# 3. Récupération sécurisée du token GitLab
echo ""
echo "🔐 Clonage du dépôt privé GitLab"
read -p "👤 Entrez votre identifiant GitLab : " GITLAB_USERNAME
read -sp "🔑 Entrez votre token GitLab (non affiché) : " GITLAB_TOKEN
echo ""

# 4. Clonage du dépôt
cd ~
REPO_URL="https://$GITLAB_USERNAME:$GITLAB_TOKEN@gitlab.ciel-kastler.fr/projets-etudiants-2eme-ann-es/projets-ciel-2025/2025-supervision/script_centreon.git"

echo "📥 Clonage en cours..."
git clone "$REPO_URL"
if [ $? -ne 0 ]; then
	echo "❌ Échec du clonage. Vérifie tes identifiants/token."
	exit 1
fi

cd script_centreon || exit 1

# 5. Création de l'environnement virtuel
echo "🐍 Création de l'environnement virtuel..."
python3 -m venv .venv
source .venv/bin/activate

# 6. Installation des dépendances
echo "📦 Installation des dépendances Python..."
cat <<EOF > requirements.txt
certifi==2025.1.31
charset-normalizer==3.4.1
coverage==7.7.1
idna==3.10
iniconfig==2.0.0
mqtt==0.0.1
packaging==24.2
paho-mqtt==2.1.0
pluggy==1.5.0
psutil==7.0.0
pytest==8.3.5
pytest-cov==6.0.0
requests==2.32.3
urllib3==2.3.0
EOF

pip install --upgrade pip
pip install -r requirements.txt

# 7. Création du service systemd
echo "🧩 Création du service systemd..."

SERVICE_PATH="/etc/systemd/system/script_centreon.service"
sudo tee "$SERVICE_PATH" > /dev/null <<EOF
[Unit]
Description=Script supervision Centreon vers MQTT
After=network.target

[Service]
ExecStart=/root/script_centreon/.venv/bin/python3 /root/script_centreon/main_centreon_2_mqtt.py
WorkingDirectory=/root/script_centreon
User=root
Group=root
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 8. Activation du service
echo "✅ Activation du service..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable script_centreon.service
sudo systemctl start script_centreon.service
sudo systemctl status script_centreon.service --no-pager

echo "🎉 Déploiement terminé avec succès !"
