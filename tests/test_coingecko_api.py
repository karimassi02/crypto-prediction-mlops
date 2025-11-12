# tests/test_coingecko_api.py

import os
from dotenv import load_dotenv
import requests

# Charger les variables d'environnement
load_dotenv()

print("=" * 60)
print("🧪 TEST COINGECKO API")
print("=" * 60)

# Récupérer la clé
api_key = os.getenv('COINGECKO_API_KEY')

# Vérifier si la clé existe
if not api_key:
    print("❌ ERREUR: Clé CoinGecko manquante dans .env")
    print("   Ajoutez COINGECKO_API_KEY")
    exit(1)

print(f"✅ Clé trouvée")
print(f"   API Key: {api_key[:10]}...{api_key[-4:]}\n")

# Configuration
headers = {'x-cg-demo-api-key': api_key}
base_url = "https://api.coingecko.com/api/v3"

try:
    # Test 1: Prix Bitcoin
    print("📊 Test 1: Prix Bitcoin...")
    url = f"{base_url}/simple/price"
    params = {
        'ids': 'bitcoin',
        'vs_currencies': 'usd',
        'include_market_cap': 'true',
        'include_24hr_vol': 'true'
    }
    
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    btc = data['bitcoin']
    print(f"✅ Prix BTC: ${btc['usd']:,.2f}")
    print(f"   Market Cap: ${btc['usd_market_cap']:,.0f}")
    print(f"   Volume 24h: ${btc['usd_24h_vol']:,.0f}\n")
    
    # Test 2: Plusieurs cryptos
    print("📊 Test 2: Prix de 5 cryptos...")
    params = {
        'ids': 'bitcoin,ethereum,binancecoin,solana,cardano',
        'vs_currencies': 'usd'
    }
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    for crypto, info in data.items():
        print(f"✅ {crypto.upper():15} ${info['usd']:,.2f}")
    
    # Test 3: Données globales
    print("\n📊 Test 3: Données marché global...")
    url = f"{base_url}/global"
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    global_data = data['data']
    btc_dominance = global_data['market_cap_percentage']['btc']
    
    print(f"✅ Market Cap Total: ${global_data['total_market_cap']['usd']:,.0f}")
    print(f"   BTC Dominance: {btc_dominance:.2f}%")
    
    print("\n" + "=" * 60)
    print("🎉 TOUS LES TESTS COINGECKO RÉUSSIS !")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    print("\n🔍 Vérifiez:")
    print("   1. Votre clé CoinGecko est correcte dans .env")
    print("   2. Vous n'avez pas dépassé la limite (50 req/min)")
    print("   3. Votre connexion internet fonctionne")
    exit(1)