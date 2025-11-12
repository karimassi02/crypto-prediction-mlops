# collect_data.py

from src.data.collectors.coingecko_collector import collect_coingecko_data
from src.data.collectors.fear_greed_collector import collect_fear_greed_data
from loguru import logger
from datetime import datetime

logger.info("=" * 60)
logger.info("🚀 COLLECTE DE DONNÉES CRYPTO")
logger.info(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logger.info("=" * 60)

# Collecter CoinGecko
logger.info("\n1️⃣ Collecte CoinGecko...")
df_coingecko = collect_coingecko_data(save=True)

# Collecter Fear & Greed
logger.info("\n2️⃣ Collecte Fear & Greed...")
df_fear_greed = collect_fear_greed_data(days=365, save=True)

# Résumé
logger.info("\n" + "=" * 60)
logger.info("📊 RÉSUMÉ DE LA COLLECTE")
logger.info("=" * 60)

if df_coingecko is not None:
    logger.success(f"✅ CoinGecko: {len(df_coingecko)} cryptos collectées")
else:
    logger.error("❌ CoinGecko: Échec")

if df_fear_greed is not None:
    logger.success(f"✅ Fear & Greed: {len(df_fear_greed)} jours collectés")
else:
    logger.error("❌ Fear & Greed: Échec")

logger.info("=" * 60)
logger.info("✅ Collecte terminée ! Vérifiez le dossier data/raw/")