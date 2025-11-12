# test_all.py

import subprocess
import sys
from datetime import datetime

print("=" * 60)
print("🧪 TEST DE TOUTES LES APIs")
print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)
print()

# Liste des tests à exécuter
tests = [
    ('Binance', 'tests/test_binance.py'),
    ('CoinGecko', 'tests/test_coingecko.py'),
    ('Fear & Greed', 'tests/test_fear_greed.py'),
]

results = {}

# Exécuter chaque test
for name, script in tests:
    print(f"\n{'='*60}")
    print(f"🔍 Test: {name}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, script],
            capture_output=False,
            check=True
        )
        results[name] = True
        print(f"\n✅ {name}: OK\n")
        
    except subprocess.CalledProcessError:
        results[name] = False
        print(f"\n❌ {name}: ÉCHEC\n")
    
    except FileNotFoundError:
        results[name] = False
        print(f"\n❌ {name}: Fichier non trouvé ({script})\n")

# Résumé final
print("\n" + "=" * 60)
print("📊 RÉSUMÉ FINAL")
print("=" * 60)

for api, status in results.items():
    emoji = "✅" if status else "❌"
    status_text = "OK" if status else "ÉCHEC"
    print(f"{emoji} {api:20} {status_text}")

# Statistiques
total = len(results)
success = sum(results.values())
rate = (success / total * 100) if total > 0 else 0

print(f"\n🎯 Taux de réussite: {success}/{total} ({rate:.0f}%)")

if all(results.values()):
    print("\n🎉 Toutes les APIs fonctionnent parfaitement !")
    print("👉 Vous pouvez passer à la collecte de données.")
    sys.exit(0)
elif success >= 2:
    print("\n⚠️ La plupart des APIs fonctionnent.")
    print("👉 Vous pouvez continuer (corrigez les erreurs plus tard).")
    sys.exit(0)
else:
    print("\n❌ Trop d'APIs ne fonctionnent pas.")
    print("👉 Vérifiez vos clés dans le fichier .env")
    sys.exit(1)

print("=" * 60)