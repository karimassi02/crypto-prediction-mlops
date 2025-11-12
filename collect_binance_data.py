# collect_binance_data.py

"""
Script de collecte des données historiques Binance OHLCV
À exécuter après validation KYC et configuration des clés API
"""

import os
from datetime import datetime
from loguru import logger
from src.data.collectors.binance_collector import collect_binance_data

logger.info("="*60)
logger.info("🚀 COLLECTE BINANCE OHLCV - Données Historiques")
logger.info(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logger.info("="*60)

# Vérifier que les clés existent
if not os.getenv('BINANCE_API_KEY') or not os.getenv('BINANCE_SECRET_KEY'):
    logger.error("\n❌ Clés Binance manquantes dans .env")
    logger.info("\nÉtapes:")
    logger.info("1. Aller sur https://www.binance.com/en/my/settings/api-management")
    logger.info("2. Créer une API Key avec permission 'Enable Reading'")
    logger.info("3. Ajouter dans .env:")
    logger.info("   BINANCE_API_KEY=votre_cle")
    logger.info("   BINANCE_SECRET_KEY=votre_secret")
    logger.info("4. Relancer ce script\n")
    exit(1)

# Configuration de la collecte
SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'ADA/USDT']
TIMEFRAME = '1d'  # Bougies quotidiennes
DAYS_BACK = 365   # 1 an d'historique

logger.info(f"\n📋 Configuration:")
logger.info(f"   Cryptos: {', '.join(SYMBOLS)}")
logger.info(f"   Timeframe: {TIMEFRAME} (bougies quotidiennes)")
logger.info(f"   Historique: {DAYS_BACK} jours")
logger.info("")

# Lancer la collecte
try:
    results = collect_binance_data(
        symbols=SYMBOLS,
        timeframe=TIMEFRAME,
        days_back=DAYS_BACK,
        save=True
    )
    
    # Résumé
    logger.info("\n" + "="*60)
    logger.info("📊 RÉSUMÉ DE LA COLLECTE")
    logger.info("="*60)
    
    if results:
        for symbol, df in results.items():
            logger.info(f"\n{symbol}:")
            logger.info(f"   Bougies: {len(df)}")
            logger.info(f"   Période: {df['timestamp'].min()} → {df['timestamp'].max()}")
            logger.info(f"   Prix actuel: ${df['close'].iloc[-1]:,.2f}")
            logger.info(f"   Variation {DAYS_BACK}j: {((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100:+.2f}%")
        
        logger.info("\n" + "="*60)
        logger.success(f"✅ {len(results)}/{len(SYMBOLS)} cryptos collectées avec succès")
        logger.info(f"📁 Fichiers sauvegardés dans: data/raw/")
        logger.info("="*60)
        
        # Prochaine étape
        logger.info("\n💡 PROCHAINE ÉTAPE:")
        logger.info("   Lancez: python process_features.py")
        logger.info("   Pour re-générer les features avec les données historiques")
        
    else:
        logger.error("\n❌ Aucune donnée collectée")
        logger.info("Vérifiez vos clés API et votre connexion")
        
except Exception as e:
    logger.error(f"\n❌ Erreur lors de la collecte: {e}")
    logger.info("\nVérifiez:")
    logger.info("  - Clés API Binance valides")
    logger.info("  - Connexion Internet")
    logger.info("  - Permissions API (Enable Reading)")