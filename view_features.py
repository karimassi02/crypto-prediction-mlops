# view_features.py

import pandas as pd
import glob
import os

print("=" * 60)
print("🔍 APERÇU DES FEATURES CRÉÉES")
print("=" * 60)

# Trouver les fichiers les plus récents
feature_files = glob.glob('data/processed/*_features_*.csv')

if not feature_files:
    print("❌ Aucun fichier de features trouvé.")
    print("   Lancez d'abord: python process_features.py")
    exit(1)

# Grouper par crypto
cryptos = {}
for file in feature_files:
    basename = os.path.basename(file)
    crypto = basename.split('_features_')[0].upper()
    if crypto not in cryptos or os.path.getctime(file) > os.path.getctime(cryptos[crypto]):
        cryptos[crypto] = file

print(f"\n📁 {len(cryptos)} cryptos avec features:\n")

for crypto, filepath in sorted(cryptos.items()):
    print(f"{'='*60}")
    print(f"💰 {crypto}")
    print(f"{'='*60}")
    
    df = pd.read_csv(filepath)
    
    print(f"\n📊 Shape: {df.shape[0]} lignes × {df.shape[1]} colonnes")
    
    # Colonnes principales
    print(f"\n📋 Colonnes créées ({len(df.columns)}) :")
    
    categories = {
        'Prix & Volume': [c for c in df.columns if any(x in c.lower() for x in ['price', 'volume', 'market'])],
        'Indicateurs Tech': [c for c in df.columns if any(x in c.lower() for x in ['sma', 'ema', 'rsi', 'macd', 'bb'])],
        'Temporel': [c for c in df.columns if any(x in c.lower() for x in ['year', 'month', 'day', 'hour', 'weekend'])],
        'Sentiment': [c for c in df.columns if any(x in c.lower() for x in ['fear', 'greed', 'fg'])],
        'Lag': [c for c in df.columns if 'lag' in c.lower()],
        'Autres': []
    }
    
    # Assigner les colonnes non catégorisées
    all_categorized = sum(categories.values(), [])
    categories['Autres'] = [c for c in df.columns if c not in all_categorized]
    
    for cat, cols in categories.items():
        if cols:
            print(f"\n  {cat} ({len(cols)}):")
            for col in cols[:5]:  # Max 5 par catégorie
                value = df[col].iloc[0]
                if pd.notna(value):
                    if isinstance(value, float):
                        print(f"    • {col:<30} = {value:.2f}")
                    else:
                        print(f"    • {col:<30} = {value}")
            if len(cols) > 5:
                print(f"    ... et {len(cols)-5} autres")
    
    # Quelques stats intéressantes
    print(f"\n🎯 Signaux Trading:")
    
    if 'rsi_14' in df.columns:
        rsi = df['rsi_14'].iloc[0]
        if rsi < 30:
            print(f"    📉 RSI = {rsi:.1f} → SUR-VENDU (signal d'achat potentiel)")
        elif rsi > 70:
            print(f"    📈 RSI = {rsi:.1f} → SUR-ACHETÉ (signal de vente potentiel)")
        else:
            print(f"    😐 RSI = {rsi:.1f} → Neutre")
    
    if 'sma_crossover' in df.columns:
        crossover = df['sma_crossover'].iloc[0]
        if crossover == 1:
            print(f"    ✅ SMA Crossover → Golden Cross (tendance haussière)")
        else:
            print(f"    ❌ SMA Crossover → Death Cross (tendance baissière)")
    
    if 'is_extreme_fear' in df.columns and df['is_extreme_fear'].iloc[0] == 1:
        fg_value = df['fear_greed_index'].iloc[0]
        print(f"    😱 Extreme Fear ({fg_value:.0f}) → Opportunité d'achat (contrarian)")
    
    if 'is_extreme_greed' in df.columns and df['is_extreme_greed'].iloc[0] == 1:
        fg_value = df['fear_greed_index'].iloc[0]
        print(f"    🤑 Extreme Greed ({fg_value:.0f}) → Prudence, correction possible")
    
    print()

print("=" * 60)
print("✅ Toutes les features sont prêtes pour le Machine Learning !")
print("=" * 60)
print("\n💡 Prochaine étape: Entraîner un modèle de prédiction")