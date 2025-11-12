# tests/test_binance_api.py

"""
Tests pour l'API Binance
À exécuter après configuration des clés
"""

import os
import sys
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

logger.info("="*60)
logger.info("🧪 TEST BINANCE API")
logger.info("="*60)

# Test 1: Vérifier les clés
logger.info("\n📊 Test 1: Vérification des clés API...")

api_key = os.getenv('BINANCE_API_KEY')
secret_key = os.getenv('BINANCE_SECRET_KEY')

if not api_key or not secret_key:
    logger.error("❌ Clés manquantes dans .env")
    logger.info("\nÉtapes pour obtenir vos clés:")
    logger.info("1. Aller sur https://www.binance.com/en/my/settings/api-management")
    logger.info("2. Créer une API Key")
    logger.info("3. Activer 'Enable Reading' uniquement")
    logger.info("4. Copier la clé et le secret dans .env:")
    logger.info("   BINANCE_API_KEY=votre_cle")
    logger.info("   BINANCE_SECRET_KEY=votre_secret")
    sys.exit(1)

logger.success("✅ Clés trouvées")
logger.info(f"   API Key: {api_key[:10]}...{api_key[-4:]}")
logger.info(f"   Secret: {secret_key[:10]}...{secret_key[-4:]}")

# Test 2: Import CCXT
logger.info("\n📊 Test 2: Vérification module CCXT...")

try:
    import ccxt
    logger.success(f"✅ CCXT version {ccxt.__version__}")
except ImportError:
    logger.error("❌ Module CCXT non installé")
    logger.info("   Installez: pip install ccxt")
    sys.exit(1)

# Test 3: Connexion Binance
logger.info("\n📊 Test 3: Connexion à Binance...")

try:
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': secret_key,
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
    exchange.load_markets()
    
    logger.success("✅ Connexion réussie")
    logger.info(f"   Exchange: {exchange.id}")
    logger.info(f"   Markets disponibles: {len(exchange.markets)}")
    
except Exception as e:
    logger.error(f"❌ Erreur connexion: {e}")
    logger.info("\nVérifiez votre connexion Internet")
    sys.exit(1)

# Test 4: Récupérer prix Bitcoin
logger.info("\n📊 Test 4: Récupération prix BTC/USDT...")

try:
    ticker = exchange.fetch_ticker('BTC/USDT')
    
    logger.success("✅ Prix récupéré")
    logger.info(f"   Prix actuel: ${ticker['last']:,.2f}")
    logger.info(f"   High 24h: ${ticker['high']:,.2f}")
    logger.info(f"   Low 24h: ${ticker['low']:,.2f}")
    logger.info(f"   Volume 24h: {ticker['baseVolume']:,.2f} BTC")
    logger.info(f"   Volume 24h (USD): ${ticker['quoteVolume']/1e9:.2f}B")
    
except Exception as e:
    logger.error(f"❌ Erreur récupération prix: {e}")
    sys.exit(1)

# Test 5: Récupérer OHLCV (bougies)
logger.info("\n📊 Test 5: Récupération 10 bougies (1h)...")

try:
    ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1h', limit=10)
    
    logger.success(f"✅ {len(ohlcv)} bougies récupérées")
    
    # Dernière bougie
    last_candle = ohlcv[-1]
    logger.info(f"   Dernière bougie (1h):")
    logger.info(f"      Open:  ${last_candle[1]:,.2f}")
    logger.info(f"      High:  ${last_candle[2]:,.2f}")
    logger.info(f"      Low:   ${last_candle[3]:,.2f}")
    logger.info(f"      Close: ${last_candle[4]:,.2f}")
    logger.info(f"      Volume: {last_candle[5]:,.2f} BTC")
    
except Exception as e:
    logger.error(f"❌ Erreur récupération bougies: {e}")
    sys.exit(1)

# Test 6: Tester plusieurs cryptos
logger.info("\n📊 Test 6: Prix de 5 cryptos...")

symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'ADA/USDT']

try:
    for symbol in symbols:
        ticker = exchange.fetch_ticker(symbol)
        price = ticker['last']
        change_24h = ticker['percentage']
        
        emoji = "🟢" if change_24h > 0 else "🔴" if change_24h < 0 else "⚪"
        
        logger.info(f"   {emoji} {symbol:12} ${price:>10,.2f}  ({change_24h:+.2f}%)")
    
    logger.success("✅ Toutes les cryptos récupérées")
    
except Exception as e:
    logger.error(f"❌ Erreur: {e}")
    sys.exit(1)

# Test 7: Tester collecte historique (30 jours)
logger.info("\n📊 Test 7: Collecte historique (30 jours)...")

try:
    ohlcv_30d = exchange.fetch_ohlcv('BTC/USDT', '1d', limit=30)
    
    logger.success(f"✅ {len(ohlcv_30d)} jours collectés")
    
    # Calculer variation
    price_start = ohlcv_30d[0][4]  # Close du premier jour
    price_end = ohlcv_30d[-1][4]   # Close du dernier jour
    change_pct = ((price_end / price_start) - 1) * 100
    
    logger.info(f"   Prix il y a 30j: ${price_start:,.2f}")
    logger.info(f"   Prix aujourd'hui: ${price_end:,.2f}")
    logger.info(f"   Variation 30j: {change_pct:+.2f}%")
    
except Exception as e:
    logger.error(f"❌ Erreur collecte historique: {e}")
    sys.exit(1)

# Test 8: Vérifier permissions (optionnel)
logger.info("\n📊 Test 8: Vérification des permissions...")

try:
    # Essayer de récupérer le compte (nécessite permission Reading)
    balance = exchange.fetch_balance()
    
    logger.success("✅ Permissions valides (Enable Reading activé)")
    logger.info(f"   Type de compte accessible")
    
except ccxt.AuthenticationError:
    logger.error("❌ Erreur authentification")
    logger.info("   Vérifiez vos clés API dans .env")
    sys.exit(1)
except ccxt.PermissionDenied:
    logger.warning("⚠️ Permission 'Enable Reading' non activée")
    logger.info("   Activez 'Enable Reading' dans les paramètres API Binance")
    logger.info("   Cela n'empêche pas la collecte OHLCV de fonctionner")
except Exception as e:
    logger.warning(f"⚠️ Test permissions: {e}")
    logger.info("   Les clés fonctionnent pour la collecte de données (c'est l'essentiel)")

# Résumé final
logger.info("\n" + "="*60)
logger.success("🎉 TOUS LES TESTS BINANCE RÉUSSIS !")
logger.info("="*60)

logger.info("\n✅ Prêt pour la collecte de données:")
logger.info("   1. Collecte simple (test):")
logger.info("      python src/data/collectors/binance_collector.py")
logger.info("")
logger.info("   2. Collecte complète (365 jours):")
logger.info("      python collect_binance_data.py")
logger.info("")
logger.info("   3. Ensuite, re-générer les features:")
logger.info("      python process_features.py")
logger.info("")
logger.info("   4. Et re-run le notebook pour voir les vrais signaux !")
logger.info("="*60)