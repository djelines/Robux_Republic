#!/bin/bash

# On s'assure que le dossier existe
mkdir -p /tmp/sql_data
chmod 777 /tmp/sql_data

# On définit le chemin pour que Python trouve le module 'app'
export PYTHONPATH=$PYTHONPATH:/app

echo "🚀 Lancement des Schedulers en arrière-plan..."

# LE "&" EST CRUCIAL ICI :
python -m app.schelduler.finalize_transaction 


echo "✅ Schedulers lancés. Démarrage de l'API..."

# Pas de "&" pour uvicorn car c'est le processus principal qui doit maintenir le container en vie
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}