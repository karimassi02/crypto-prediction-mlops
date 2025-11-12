# view_data.py

import pandas as pd
import glob
import os

print("=" * 60)
print("📊 APERÇU DES DONNÉES COLLECTÉES")
print("=" * 60)

# Trouver les fichiers les plus récents
coingecko_files = glob.glob('data/raw/coingecko_*.csv')
fear_greed_files = glob.glob('data/raw/fear_greed_*.csv')

if not coingecko_files or not fear_greed_files:
    print("❌ Aucun fichier trouvé. Lancez d'abord: python collect_data.py")
    exit(1)

# Fichiers les plus récents
latest_coingecko = max(coingecko_files, key=os.path.getctime)
latest_fear_greed = max(fear_greed_files, key=os.path.getctime)

print(f"\n📁 Fichiers analysés:")
print(f"   CoinGecko: {os.path.basename(latest_coingecko)}")
print(f"   Fear & Greed: {os.path.basename(latest_fear_greed)}")

# Charger CoinGecko
print("\n" + "=" * 60)
print("💰 DONNÉES COINGECKO")
print("=" * 60)

df_cg = pd.read_csv(latest_coingecko)
print(f"\nShape: {df_cg.shape}")
print("\nAperçu:")
print(df_cg.to_string())

print(f"\n📊 Statistiques:")
print(f"   Prix moyen: ${df_cg['price_usd'].mean():,.2f}")
print(f"   Market Cap total: ${df_cg['market_cap_usd'].sum():,.0f}")
print(f"   Volume 24h total: ${df_cg['volume_24h_usd'].sum():,.0f}")

# Charger Fear & Greed
print("\n" + "=" * 60)
print("😱 DONNÉES FEAR & GREED")
print("=" * 60)

df_fg = pd.read_csv(latest_fear_greed)
print(f"\nShape: {df_fg.shape}")
print("\n10 derniers jours:")
print(df_fg.tail(10).to_string())

print(f"\n📊 Statistiques:")
print(f"   Moyenne: {df_fg['value'].mean():.1f}")
print(f"   Médiane: {df_fg['value'].median():.1f}")
print(f"   Min: {df_fg['value'].min()}")
print(f"   Max: {df_fg['value'].max()}")

# Distribution
print(f"\n📊 Distribution:")
print(f"   Extreme Fear (0-25): {len(df_fg[df_fg['value'] <= 25])} jours")
print(f"   Fear (26-45): {len(df_fg[(df_fg['value'] > 25) & (df_fg['value'] <= 45)])} jours")
print(f"   Neutral (46-55): {len(df_fg[(df_fg['value'] > 45) & (df_fg['value'] <= 55)])} jours")
print(f"   Greed (56-75): {len(df_fg[(df_fg['value'] > 55) & (df_fg['value'] <= 75)])} jours")
print(f"   Extreme Greed (76-100): {len(df_fg[df_fg['value'] > 75])} jours")

print("\n" + "=" * 60)
print("✅ Données prêtes pour l'analyse !")
print("=" * 60)