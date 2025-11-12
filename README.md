# crypto-prediction-mlops

Développement d'un système intelligent de prédiction et d'analyse de tendances pour les cryptomonnaies, intégrant l'apprentissage automatique, l'analyse de sentiment et le traitement de données en temps réel, afin d'aider les investisseurs à prendre des décisions éclairées sur des marchés hautement volatils.

## 🚀 Crypto Prediction MLOps

Système de prédiction de tendances crypto avec pipeline MLOps complet.

> **Projet M2 Data Science** - Prédiction des prix de cryptomonnaies utilisant Machine Learning et analyse de sentiment de marché.

---

## 📊 État du Projet

**Dernière mise à jour :** 12 novembre 2025

### ✅ Phase 1 : Collecte de Données (Complété à 70%)

- [x] Configuration APIs (CoinGecko, Fear & Greed Index)
- [x] Tests unitaires des APIs
- [x] Collecteurs automatiques de données
- [x] Première collecte réussie (5 cryptos + 365 jours historique)
- [x] Dashboard de visualisation Streamlit
- [ ] Collecteur Binance OHLCV (en attente validation KYC)

### 🔄 Phase 2 : Stockage & Pipeline (À venir)

- [x] Stockage CSV temporaire
- [ ] Migration PostgreSQL
- [ ] Pipeline de collecte automatique
- [ ] Gestion des erreurs et retry logic

### ⏳ Phase 3 : Feature Engineering (À venir)

- [ ] Indicateurs techniques (RSI, MACD, SMA, Bollinger)
- [ ] Features temporelles
- [ ] Features de sentiment (Fear & Greed)
- [ ] Corrélations et features combinées

### ⏳ Phase 4 : Machine Learning (À venir)

- [ ] Préparation dataset ML
- [ ] Modèles de prédiction (régression, LSTM)
- [ ] Évaluation et validation
- [ ] Optimisation hyperparamètres

### ⏳ Phase 5 : MLOps (À venir)

- [ ] MLflow tracking
- [ ] CI/CD avec GitHub Actions
- [ ] API FastAPI de prédiction
- [ ] Monitoring et alertes
- [ ] Déploiement

---

## ✨ Fonctionnalités Actuelles

- ✅ Configuration APIs (CoinGecko, Fear & Greed)
- ✅ Tests unitaires des APIs
- ✅ Collecteurs automatiques de données
- ✅ Collecte de 5 cryptos + 365 jours d'historique
- ✅ Dashboard Streamlit interactif
- ✅ Stockage CSV
- ⏳ Collecteur Binance (en attente KYC)

---

## 🎯 Objectif du Projet

Développer un système complet de prédiction des prix de cryptomonnaies intégrant :

1. **Collecte automatique** de données multi-sources (prix, volume, sentiment)
2. **Feature engineering** avec indicateurs techniques (RSI, MACD, SMA)
3. **Modèles de Machine Learning** (régression, LSTM, XGBoost)
4. **Pipeline MLOps** production-ready avec MLflow
5. **API de prédiction** en temps réel (FastAPI)
6. **Dashboard** de visualisation et monitoring

---

## 🚀 Quick Start

### Prérequis

- Python 3.10+
- Git
- Compte CoinGecko (gratuit)
- Compte Binance avec KYC (optionnel)

### Installation

```bash
# 1. Cloner le repository
git clone https://github.com/karimassi02/crypto-prediction-mlops.git
cd crypto-prediction-mlops

# 2. Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés API (voir section Configuration)
```

---

## 🔑 Configuration des APIs

### CoinGecko (obligatoire)

1. Aller sur https://www.coingecko.com/en/api
2. Créer un compte gratuit
3. Générer une API Key
4. Ajouter dans `.env` :

```bash
COINGECKO_API_KEY=CG-votre_cle_ici
```

### Fear & Greed Index (aucune config)

```bash
# API publique, déjà configurée
FEAR_GREED_URL=https://api.alternative.me/fng/
```

### Binance (optionnel)

1. Créer compte sur https://www.binance.com
2. Compléter la vérification KYC
3. Aller dans API Management
4. Créer une clé avec permission "Enable Reading" uniquement
5. Ajouter dans `.env` :

```bash
BINANCE_API_KEY=votre_cle_ici
BINANCE_SECRET_KEY=votre_secret_ici
```

---

## 🎮 Utilisation

```bash
# 1. Tester les APIs
python tests/test_coingecko_api.py
python tests/test_fear_greed_api.py

# 2. Collecter les données
python collect_data.py

# 3. Visualiser les données
python view_data.py

# 4. Lancer le dashboard
streamlit run src/api/dashboard.py
```

---

## 📁 Structure du Projet

```
crypto-prediction-mlops/
│
├── src/                              # Code source principal
│   ├── api/
│   │   └── dashboard.py              # Dashboard Streamlit
│   ├── data/
│   │   └── collectors/
│   │       ├── coingecko_collector.py    # Collecteur CoinGecko
│   │       └── fear_greed_collector.py   # Collecteur Fear & Greed
│   ├── features/                     # Feature engineering (à venir)
│   ├── models/                       # Modèles ML (à venir)
│   └── utils/                        # Fonctions utilitaires
│
├── data/
│   ├── raw/                          # Données brutes CSV
│   ├── processed/                    # Données transformées
│   └── external/                     # Données externes
│
├── tests/                            # Tests unitaires
│   ├── test_coingecko_api.py
│   ├── test_fear_greed_api.py
│   └── test_binance_api.py
│
├── notebooks/                        # Jupyter notebooks (exploration)
├── config/                           # Fichiers de configuration
├── docs/                             # Documentation détaillée
│
├── collect_data.py                   # Script de collecte principal
├── view_data.py                      # Visualisation rapide des données
├── .env                              # Variables d'environnement (non versionné)
├── .env.example                      # Template des variables
├── requirements.txt                  # Dépendances Python
├── .gitignore                        # Fichiers ignorés par Git
└── README.md                         # Ce fichier
```

---

## 📊 Dashboard Streamlit

### Fonctionnalités

#### Métriques Principales

- Prix en temps réel avec variation 24h
- Market Cap et Volume 24h
- Fear & Greed Index actuel

#### Visualisations

- Comparaison des prix (bar chart interactif)
- Historique Fear & Greed sur 365 jours
- Zones de référence (Extreme Fear/Greed)

#### Statistiques

- Stats Fear & Greed (moyenne, min, max)
- Distribution par zones de sentiment
- Données brutes téléchargeables (CSV)

#### Options

- Sélection de crypto dans sidebar
- Auto-refresh optionnel (60 secondes)
- Export des données en CSV

---

## 🛠️ Technologies Utilisées

- **Python 3.10+** - Langage principal
- **Streamlit** - Dashboard interactif
- **pandas** - Manipulation de données
- **requests** - Appels API
- **python-dotenv** - Gestion variables d'environnement
- **CoinGecko API** - Données de marché
- **Fear & Greed Index API** - Sentiment de marché

---

## 📈 Prochaines Étapes

1. **Phase 2 : Stockage**
   - Migration vers PostgreSQL
   - Pipeline de collecte automatique (cron/scheduler)
   - Gestion d'erreurs et retry logic

2. **Phase 3 : Feature Engineering**
   - Calcul indicateurs techniques (RSI, MACD, SMA)
   - Features temporelles (jour semaine, heure)
   - Features de sentiment

3. **Phase 4 : Machine Learning**
   - Préparation dataset ML
   - Entraînement modèles (régression, LSTM)
   - Validation et optimisation

4. **Phase 5 : MLOps**
   - MLflow pour tracking
   - CI/CD avec GitHub Actions
   - API FastAPI de prédiction
   - Déploiement production

---

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amazing-feature`)
3. Commit vos changements (`git commit -m 'Add amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

---

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 👤 Auteur

**Karim Assi**

- GitHub: [@karimassi02](https://github.com/karimassi02)
- Projet: [crypto-prediction-mlops](https://github.com/karimassi02/crypto-prediction-mlops)

---

## 🙏 Remerciements

- CoinGecko pour l'API de données de marché
- Alternative.me pour l'API Fear & Greed Index
- Communauté Data Science pour les ressources et conseils

---

## 📞 Support

Pour toute question ou problème :

- Ouvrir une [issue](https://github.com/karimassi02/crypto-prediction-mlops/issues)
- Consulter la [documentation](./docs)
- Contacter via GitHub

---

**⭐ N'oubliez pas de mettre une étoile au projet si vous le trouvez utile !**