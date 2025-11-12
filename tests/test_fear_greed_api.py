# tests/test_fear_greed_api.py

import os
import sys
from dotenv import load_dotenv
import requests
from datetime import datetime

# Charger les variables d'environnement
load_dotenv()

print("=" * 60)
print("🧪 TEST FEAR & GREED INDEX")
print("=" * 60)

# URL de l'API (pas besoin de clé !)
url = os.getenv('FEAR_GREED_URL', 'https://api.alternative.me/fng/')

print(f"✅ URL: {url}\n")

try:
    # Test 1: Index actuel
    print("📊 Test 1: Index actuel...")
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    current = data['data'][0]
    value = int(current['value'])
    classification = current['value_classification']
    
    # Déterminer l'emoji
    if value <= 25:
        emoji = "😱"
    elif value <= 45:
        emoji = "😰"
    elif value <= 55:
        emoji = "😐"
    elif value <= 75:
        emoji = "😃"
    else:
        emoji = "🤑"
    
    print(f"✅ {emoji} Index: {value}/100")
    print(f"   Classification: {classification}")
    print(f"   Timestamp: {datetime.fromtimestamp(int(current['timestamp'])).strftime('%Y-%m-%d %H:%M')}\n")
    
    # Test 2: Historique 30 jours
    print("📊 Test 2: Historique 30 derniers jours...")
    url_history = f"{url}?limit=30"
    response = requests.get(url_history, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    history = data['data']
    values = [int(d['value']) for d in history]
    
    print(f"✅ {len(history)} jours récupérés")
    print(f"   Moyenne: {sum(values)/len(values):.1f}")
    print(f"   Min: {min(values)}")
    print(f"   Max: {max(values)}\n")
    
    # Test 3: Afficher les 7 derniers jours
    print("📊 Test 3: Tendance 7 derniers jours...")
    for entry in history[:7]:
        date = datetime.fromtimestamp(int(entry['timestamp'])).strftime('%Y-%m-%d')
        val = entry['value']
        classif = entry['value_classification']
        print(f"   {date}: {val:>3} - {classif}")
    
    print("\n" + "=" * 60)
    print("🎉 TOUS LES TESTS FEAR & GREED RÉUSSIS !")
    print("=" * 60)
    sys.exit(0)
    
except requests.exceptions.Timeout:
    print(f"\n❌ ERREUR: Timeout - L'API ne répond pas")
    print("   Réessayez dans quelques secondes")
    sys.exit(1)
    
except requests.exceptions.ConnectionError:
    print(f"\n❌ ERREUR: Pas de connexion internet")
    print("   Vérifiez votre connexion réseau")
    sys.exit(1)
    
except requests.exceptions.RequestException as e:
    print(f"\n❌ ERREUR RÉSEAU: {e}")
    sys.exit(1)
    
except KeyError as e:
    print(f"\n❌ ERREUR: Données manquantes dans la réponse - {e}")
    print(f"   Réponse reçue: {data}")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ ERREUR INATTENDUE: {type(e).__name__}: {e}")
    print("\n🔍 Vérifiez:")
    print("   1. Votre connexion internet")
    print("   2. L'URL est correcte dans .env")
    import traceback
    traceback.print_exc()
    sys.exit(1)