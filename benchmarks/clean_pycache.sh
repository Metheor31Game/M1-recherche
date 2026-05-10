#!/usr/bin/env sh
set -eu

# Supprime tous les dossiers __pycache__ du projet
find . -type d -name "__pycache__" -prune -exec rm -rf {} +

echo "Tous les dossiers __pycache__ ont ete supprimes."