# process_features.py

"""
Script de traitement : applique le feature engineering aux données collectées
"""

import pandas as pd
import glob
import os
from datetime import datetime
from loguru import logger
from src.features.feature_engineer import engineer_features

logger.info("=" * 60)
logger.info("🔧 FEATURE ENGINEERING - Traitement des Données")
logger.info(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logger.info("=" * 60)

# Trouver les fichiers les plus récents
coingecko_files = glob.glob('data/raw/coingecko_*.csv')
fear_greed_files = glob.glob('data/raw/fear_greed_*.csv')

if not coingecko_files:
    logger.error("❌ Aucun fichier CoinGecko trouvé. Lancez d'abord: python collect_data.py")
    exit(1)

latest_coingecko = max(coingecko_files, key=os.path.getctime)
latest_fear_greed = max(fear_greed_files, key=os.path.getctime) if fear_greed_files else None

logger.info(f"\n📁 Fichiers à traiter:")
logger.info(f"   CoinGecko: {os.path.basename(latest_coingecko)}")
if latest_fear_greed:
    logger.info(f"   Fear & Greed: {os.path.basename(latest_fear_greed)}")

# Charger les données
df_price = pd.read_csv(latest_coingecko)
df_fear_greed = pd.read_csv(latest_fear_greed) if latest_fear_greed else None

logger.info(f"\n📊 Données chargées:")
logger.info(f"   Prix: {len(df_price)} lignes")
if df_fear_greed is not None:
    logger.info(f"   Fear & Greed: {len(df_fear_greed)} lignes")

# Créer dossier processed si nécessaire
os.makedirs('data/processed', exist_ok=True)

# Traiter chaque crypto séparément
symbols = df_price['symbol'].unique()

logger.info(f"\n🔄 Traitement de {len(symbols)} cryptos...\n")

for symbol in symbols:
    logger.info(f"{'='*60}")
    logger.info(f"💰 Traitement: {symbol}")
    logger.info(f"{'='*60}")
    
    # Filtrer sur la crypto
    df_crypto = df_price[df_price['symbol'] == symbol].copy()
    
    # Trier par date
    df_crypto = df_crypto.sort_values('timestamp').reset_index(drop=True)
    
    # Appliquer feature engineering
    df_features = engineer_features(df_crypto, df_fear_greed)
    
    # Nom du fichier de sortie
    date_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_file = f"data/processed/{symbol.lower()}_features_{date_str}.csv"
    
    # Sauvegarder
    df_features.to_csv(output_file, index=False)
    
    logger.info(f"📊 Résultat:")
    logger.info(f"   Shape: {df_features.shape}")
    logger.info(f"   Features créées: {len(df_features.columns)}")
    logger.info(f"💾 Sauvegardé: {output_file}\n")

# Résumé final
logger.info("=" * 60)
logger.info("📊 RÉSUMÉ DU TRAITEMENT")
logger.info("=" * 60)
logger.success(f"✅ {len(symbols)} cryptos traitées avec succès")
logger.info("📁 Fichiers disponibles dans: data/processed/")
logger.info("=" * 60)
logger.success("✅ Feature engineering terminé !")