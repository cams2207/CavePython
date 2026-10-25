#!/bin/bash

# ==============================================================================
# Script de Déploiement Automatique - Mon Chai
# ==============================================================================

# CONFIGURATION
# Modifier APP_DIR pour correspondre au chemin absolu sur votre serveur
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVICE_NAME="monchai.service"
VENV_DIR="venv"

echo "---------------------------------------------------"
echo "🚀 Initialisation du déploiement : $(date)"
echo "---------------------------------------------------"

# 1. Aller dans le dossier du projet
cd "$APP_DIR" || { echo "❌ Erreur : Impossible d'accéder au dossier $APP_DIR"; exit 1; }

# 2. Nettoyage Git (optionnel, pour éviter les conflits de permissions locales)
# git checkout -- .

# 3. Récupérer la dernière version
echo "📥 Mise à jour du code (Git pull)..."
git pull origin main || { echo "❌ Erreur : Échec du git pull"; exit 1; }

# 4. Gestion de l'environnement virtuel et dépendances
if [ -d "$VENV_DIR" ]; then
    echo "📦 Mise à jour des dépendances Python..."
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "⚠️  Environnement virtuel non trouvé. Création dans $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# 5. Sécurisation des fichiers de données
# On s'assure que l'application peut écrire dans ses fichiers de stockage
echo "🔐 Vérification des permissions des données..."
touch data_cave.csv
chmod 664 data_cave.csv
# Appliquer aux fichiers JSON s'ils existent
ls *.json >/dev/null 2>&1 && chmod 664 *.json

# 6. Redémarrage du service systemd
echo "🔄 Redémarrage du service $SERVICE_NAME..."
if systemctl list-unit-files | grep -q "$SERVICE_NAME"; then
    sudo systemctl restart "$SERVICE_NAME"
    
    # 7. Vérification finale
    sleep 2
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo "---------------------------------------------------"
        echo "✅ DÉPLOIEMENT RÉUSSI ET SERVICE ACTIF"
        echo "---------------------------------------------------"
    else
        echo "❌ ERREUR : Le service n'a pas redémarré correctement."
        echo "Consultez les logs : sudo journalctl -u $SERVICE_NAME -n 50"
        exit 1
    fi
else
    echo "⚠️  ATTENTION : Le service $SERVICE_NAME n'est pas encore installé sur ce système."
    echo "Utilisez le fichier 'monchai.service' fourni pour configurer systemd."
    exit 0
fi
