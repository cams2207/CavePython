#!/bin/bash

# ==============================================================================

# Script de Déploiement par Copie - Mon Chai
# ==============================================================================

# CONFIGURATION


SRC_DIR="$(cd "$(dirname "$0")" && pwd)" # Dossier actuel (ton /home/...)
DEST_DIR="/var/www/monchai"              # Dossier de destination final
SERVICE_NAME="monchai.service"
VENV_DIR="venv"

echo "---------------------------------------------------"

echo "🚀 Déploiement de $SRC_DIR vers $DEST_DIR"
echo "---------------------------------------------------"



# 1. Créer le dossier de destination s'il n'existe pas
if [ ! -d "$DEST_DIR" ]; then
    echo "📂 Création du dossier de destination..."
    sudo mkdir -p "$DEST_DIR"
    sudo chown $USER:www-data "$DEST_DIR"
fi



# 2. Synchronisation des fichiers
# --exclude : on n'écrase SURTOUT PAS la base de données réelle (.csv et .json)
# --exclude venv : on ne copie pas l'environnement virtuel, on le gère sur place
echo "📦 Copie des fichiers (rsync)..."
rsync -av --progress "$SRC_DIR/" "$DEST_DIR/" \
    --exclude ".git/" \
    --exclude ".venv/" \
    --exclude "venv/" \
    --exclude "__pycache__/" \
    --exclude "data_cave.csv" \
    --exclude "*.json" \
    --exclude "deploy.sh" \
    --exclude "monchai.service"




# 3. Aller dans le dossier final pour la suite
cd "$DEST_DIR" || exit 1









# 4. Gestion de l'environnement virtuel sur place
if [ ! -d "$VENV_DIR" ]; then
    echo "⚠️  Création de l'environnement virtuel dans $DEST_DIR..."
    python3 -m venv "$VENV_DIR"



fi





echo "📦 Mise à jour des dépendances..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

# 5. Sécurité : S'assurer que les fichiers de données existent dans le dossier final
if [ ! -f "data_cave.csv" ]; then
    echo "📝 Initialisation d'une nouvelle base de données vide..."
    touch data_cave.csv
fi
chmod 664 data_cave.csv

ls *.json >/dev/null 2>&1 && chmod 664 *.json

















# 6. Redémarrage du service
echo "🔄 Redémarrage du serveur..."
sudo systemctl restart "$SERVICE_NAME"

# 7. Vérification
sleep 1
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "---------------------------------------------------"
    echo "✅ DÉPLOIEMENT RÉUSSI !"
    echo "Le site est à jour dans $DEST_DIR"
    echo "---------------------------------------------------"
else



    echo "❌ ERREUR : Le service n'a pas redémarré. Vérifie 'sudo journalctl -u $SERVICE_NAME'"
fi
