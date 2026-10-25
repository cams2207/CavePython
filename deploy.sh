#!/bin/bash

# ==============================================================================


# Script de Déploiement par Copie - Mon Chai (Version Robuste)
# ==============================================================================

# CONFIGURATION




SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
DEST_DIR="/var/www/monchai"
SERVICE_NAME="monchai.service"
VENV_DIR="venv"

echo "---------------------------------------------------"


echo "🚀 Déploiement : $SRC_DIR -> $DEST_DIR"
echo "---------------------------------------------------"

# 0. Vérification et installation de rsync si nécessaire
if ! command -v rsync &> /dev/null; then
    echo "📦 rsync non trouvé. Tentative d'installation..."
    sudo apt-get update && sudo apt-get install -y rsync || { echo "❌ Échec de l'installation de rsync"; exit 1; }
fi



# 1. Créer le dossier de destination et gérer les droits
if [ ! -d "$DEST_DIR" ]; then
    echo "📂 Création du dossier de destination..."
    sudo mkdir -p "$DEST_DIR"

fi
sudo chown $USER:www-data "$DEST_DIR"
sudo chmod 775 "$DEST_DIR"



# 2. Synchronisation des fichiers




echo "📦 Synchronisation des fichiers..."
rsync -av --delete "$SRC_DIR/" "$DEST_DIR/" \
    --exclude ".git/" \
    --exclude ".venv/" \
    --exclude "venv/" \
    --exclude "__pycache__/" \
    --exclude "data_cave.csv" \
    --exclude "*.json" \
    --exclude "deploy.sh" \
    --exclude "monchai.service" \
    --exclude ".claude/" \
    --exclude ".continue/" \
    --exclude ".gemini/" \
    --exclude ".dsh/"

# 3. Installation des dépendances dans le dossier de destination
cd "$DEST_DIR" || { echo "❌ Impossible d'accéder à $DEST_DIR"; exit 1; }















if [ ! -d "$VENV_DIR" ]; then

    echo "⚠️  Création de l'environnement virtuel..."
    python3 -m venv "$VENV_DIR"
fi



echo "📦 Mise à jour des dépendances Python..."
"$VENV_DIR/bin/pip" install --upgrade pip
if [ -f "requirements.txt" ]; then
    "$VENV_DIR/bin/pip" install -r requirements.txt
else
    echo "⚠️  Attention : requirements.txt introuvable dans $DEST_DIR"
fi

# 4. Initialisation/Permissions des données
echo "🔐 Configuration des accès aux données..."
[ ! -f "data_cave.csv" ] && touch data_cave.csv
sudo chown $USER:www-data data_cave.csv
chmod 664 data_cave.csv

# Gestion des fichiers JSON
for f in *.json; do
    if [ -e "$f" ]; then
        sudo chown $USER:www-data "$f"
        chmod 664 "$f"
    fi
done












# 5. Redémarrage du service
echo "🔄 Redémarrage du service $SERVICE_NAME..."
# On vérifie si le fichier service est installé, sinon on le copie
if [ ! -f "/etc/systemd/system/$SERVICE_NAME" ]; then
    echo "📝 Installation du fichier service systemd..."
    sudo cp "$SRC_DIR/$SERVICE_NAME" "/etc/systemd/system/"
    # Remplacement dynamique de l'utilisateur dans le fichier service
    sudo sed -i "s/User=votre_utilisateur/User=$USER/" "/etc/systemd/system/$SERVICE_NAME"
    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME"
fi






















sudo systemctl restart "$SERVICE_NAME"



# 6. Verdict
sleep 2
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "---------------------------------------------------"


    echo "✅ DÉPLOIEMENT TERMINÉ AVEC SUCCÈS !"
    echo "Site accessible sur le port configuré."
    echo "---------------------------------------------------"
else




    echo "❌ LE SERVICE N'A PAS DÉMARRÉ."
    echo "Logs d'erreur :"
    sudo journalctl -u "$SERVICE_NAME" -n 20 --no-pager
    exit 1
fi

