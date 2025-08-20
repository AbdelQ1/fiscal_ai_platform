#!/bin/bash

echo "🚀 Démarrage d'EspoCRM avec Docker..."

# Vérifier si Docker est en cours d'exécution
if ! docker info > /dev/null 2>&1; then
    echo "❌ Erreur: Docker n'est pas démarré. Veuillez lancer Docker Desktop."
    exit 1
fi

# Arrêter les conteneurs existants (si ils existent)
echo "🛑 Arrêt des conteneurs existants..."
docker-compose down

# Démarrer les services
echo "📦 Création et démarrage des conteneurs..."
docker-compose up -d

# Attendre que les services soient prêts
echo "⏳ Attente du démarrage des services..."
sleep 30

# Vérifier le statut
echo "📊 Statut des conteneurs:"
docker-compose ps

echo ""
echo "✅ EspoCRM est maintenant accessible à l'adresse:"
echo "   🌐 http://localhost:8080"
echo ""
echo "📝 Identifiants par défaut:"
echo "   Utilisateur: admin"
echo "   Mot de passe: admin123"
echo ""
echo "🗄️  Base de données MySQL accessible sur le port 3306"
echo "   Host: localhost"
echo "   Database: espocrm" 
echo "   User: espocrm"
echo "   Password: espocrm_password"
echo ""
echo "💡 Pour arrêter les services: docker-compose down"
echo "💡 Pour voir les logs: docker-compose logs -f"

