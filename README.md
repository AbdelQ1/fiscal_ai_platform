# 🏛️ Fiscal AI Platform

![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Status](https://img.shields.io/badge/status-en%20développement-yellow.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📋 Description

Plateforme d'intelligence artificielle dédiée à l'analyse et au traitement automatique des documents fiscaux. Ce projet utilise des techniques d'OCR et d'analyse de patterns pour extraire et traiter les informations fiscales à partir de documents PDF.

## 🗂️ Structure du Projet

```
fiscal_ai_platform/
├── 📁 api/                    # API endpoints et logique serveur
├── 📁 config/                 # Configuration de l'application
├── 📁 core/                   # Fonctionnalités principales
├── 📁 data/                   # Données et fichiers de test
├── 📁 modules/                # Modules métier spécialisés
├── 📁 scripts/                # Scripts utilitaires
├── 📁 tests/                  # Tests unitaires et d'intégration
├── 📁 ui/                     # Interface utilisateur
├── 📁 invoices_to_test/       # Échantillons de factures pour tests
├── 📄 analyze_pdf_raw.py      # Analyse brute des PDF
├── 📄 debug_*.py              # Scripts de débogage OCR
├── 📄 docker-compose.yml      # Configuration Docker
├── 📄 start.sh                # Script de démarrage
└── 📄 .env                    # Variables d'environnement
```

## ✨ Fonctionnalités

### 🔍 Analyse de Documents
- **Extraction OCR** - Reconnaissance optique de caractères
- **Analyse de patterns** - Détection automatique de structures fiscales
- **Traitement PDF** - Support des documents fiscaux complexes
- **Validation de données** - Vérification de la cohérence des extractions

### 🤖 Intelligence Artificielle
- **Reconnaissance de patterns fiscaux** - Identification automatique des éléments
- **Extraction de données structurées** - Conversion PDF vers données exploitables
- **Diagnostic automatique** - Détection d'anomalies dans les documents

## 🚀 Installation

### Prérequis
- Python 3.8 ou supérieur
- Docker et Docker Compose (optionnel)

### Installation locale

1. **Cloner le dépôt**
```bash
git clone https://github.com/AbdelQ1/fiscal_ai_platform.git
cd fiscal_ai_platform
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt  # À créer si nécessaire
```

4. **Configuration**
```bash
# Le fichier .env est déjà présent, adapter selon vos besoins
cp .env .env.local
```

5. **Lancement avec Docker (recommandé)**
```bash
docker-compose up -d
```

6. **Ou lancement manuel**
```bash
chmod +x start.sh
./start.sh
```

## 🔧 Utilisation

### Analyse de PDF fiscal

```python
# Utilisation du module d'analyse principale
from analyze_pdf_raw import analyze_document

# Analyser un document fiscal
result = analyze_document('invoices_to_test/sample_invoice.pdf')
print(f"Données extraites: {result}")
```

### Scripts de débogage disponibles

```bash
# Diagnostic OCR de base
python diagnostic_ocr_base.py

# Débogage du contenu PDF
python debug_pdf_content.py

# Test OCR réel
python debug_real_ocr.py

# Analyse des patterns
python debug_patterns_precise.py
```

### Tests

```bash
# Lancer tous les tests
python -m pytest tests/ -v

# Tests avec coverage
python -m pytest tests/ --cov=core --cov=modules --cov=api
```

## 📁 Modules Principaux

- **`core/`** - Logique métier centrale
- **`modules/`** - Modules spécialisés (OCR, patterns, extraction)
- **`api/`** - Interface API REST
- **`ui/`** - Interface utilisateur web
- **`config/`** - Configuration centralisée

## 🧪 Données de Test

Le dossier `invoices_to_test/` contient des échantillons de factures et documents fiscaux pour tester les fonctionnalités d'extraction et d'analyse.

## 🐳 Docker

Le projet inclut une configuration Docker complète :

```bash
# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter les services
docker-compose down
```

## 📚 Scripts Utilitaires

| Script | Description |
|--------|-------------|
| `start.sh` | Script de démarrage principal |
| `analyze_pdf_raw.py` | Analyse brute de documents PDF |
| `debug_patterns_precise.py` | Débogage des patterns de reconnaissance |
| `test_patterns_corriges.py` | Tests des patterns corrigés |

## 🔍 Développement

### Débogage OCR
Plusieurs scripts de débogage sont disponibles pour tester et améliorer la précision de l'OCR :

- `diagnostic_ocr_base.py` - Diagnostic de base
- `debug_pdf_content.py` - Analyse du contenu PDF
- `debug_real_ocr.py` - Test OCR en conditions réelles

### Structure de développement
```bash
# Ajouter de nouveaux modules
modules/
├── new_module/
│   ├── __init__.py
│   ├── processor.py
│   └── utils.py

# Ajouter des tests
tests/
├── test_new_module.py
└── integration/
    └── test_full_pipeline.py
```

## 🚧 Roadmap

### Version actuelle
- [x] Extraction OCR de base
- [x] Analyse de patterns fiscaux
- [x] Interface de débogage
- [x] Configuration Docker

### Prochaines étapes
- [ ] API REST complète
- [ ] Interface web finalisée
- [ ] Support multi-formats
- [ ] Intégration base de données
- [ ] Déploiement production

## 🛠️ Technologies Utilisées

### Backend
- **Python 3.8+** - Langage principal
- **FastAPI** - Framework web haute performance
- **PostgreSQL** - Base de données relationnelle
- **Redis** - Cache et sessions
- **Celery** - Tâches asynchrones

### Intelligence Artificielle
- **TensorFlow/PyTorch** - Machine Learning
- **Transformers** - Traitement du langage naturel
- **OpenCV** - Traitement d'images
- **spaCy** - Analyse de texte
- **scikit-learn** - Algorithmes ML classiques

### Frontend
- **HTML/CSS/JavaScript** - Interface utilisateur web
- **Bootstrap** - Framework CSS responsive
- **Chart.js** - Visualisations de données

### Infrastructure
- **Docker** - Conteneurisation
- **AWS/Azure** - Cloud computing
- **GitHub Actions** - CI/CD

## 📦 Dépendances principales

```python
# Traitement PDF et OCR
PyPDF2
pytesseract
opencv-python
Pillow

# Machine Learning et IA
tensorflow
scikit-learn
numpy
pandas

# API et web
fastapi
uvicorn
requests

# Base de données
psycopg2-binary
redis

# Tests
pytest
pytest-cov
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add some AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

### Règles de contribution
- Suivre les conventions de code (PEP 8 pour Python)
- Ajouter des tests pour les nouvelles fonctionnalités
- Mettre à jour la documentation si nécessaire
- Respecter le code de conduite du projet

## 📄 Documentation Technique

Voir `TECHNICAL_CONTEXT.md` pour plus de détails techniques sur l'architecture et les choix de conception.

## 📞 Support

- **Issues GitHub** : [Créer un ticket](https://github.com/AbdelQ1/fiscal_ai_platform/issues)
- **Documentation technique** : `TECHNICAL_CONTEXT.md`

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

*Développé pour automatiser et optimiser le traitement des documents fiscaux* 🚀
