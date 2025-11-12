# tests/test_binance_api.py

import os
from dotenv import load_dotenv
import ccxt

# Charger les variables d'environnement
load_dotenv()

print("=" * 60)
print("🧪 TEST BINANCE API")
print("=" * 60)

# Récupérer les clés
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_SECRET_KEY')

# Vérifier si les clés existent
if not api_key or not api_secret:
    print("❌ ERREUR: Clés Binance manquantes dans .env")
    print("   Ajoutez BINANCE_API_KEY et BINANCE_SECRET_KEY")
    exit(1)

print(f"✅ Clés trouvées")
print(f"   API Key: {api_key[:10]}...{api_key[-4:]}\n")

# Initialiser Binance
try:
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
    })
    
    # Test 1: Récupérer le prix BTC/USDT
    print("📊 Test 1: Prix BTC/USDT...")
    ticker = exchange.fetch_ticker('BTC/USDT')
    print(f"✅ Prix: ${ticker['last']:,.2f}")
    print(f"   Volume 24h: ${ticker['quoteVolume']:,.0f}\n")
    
    # Test 2: Récupérer des bougies
    print("📊 Test 2: Récupération 10 bougies horaires...")
    ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1h', limit=10)
    print(f"✅ {len(ohlcv)} bougies récupérées")
    print(f"   Dernière bougie: ${ohlcv[-1][4]:,.2f}\n")
    
    # Test 3: Plusieurs cryptos
    print("📊 Test 3: Prix de 3 cryptos...")
    symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
    for symbol in symbols:
        ticker = exchange.fetch_ticker(symbol)
        print(f"✅ {symbol:12} ${ticker['last']:,.2f}")
    
    print("\n" + "=" * 60)
    print("🎉 TOUS LES TESTS BINANCE RÉUSSIS !")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    print("\n🔍 Vérifiez:")
    print("   1. Vos clés sont correctes dans .env")
    print("   2. 'Enable Reading' est activé sur Binance")
    print("   3. Votre compte Binance est vérifié (KYC)")
    exit(1)