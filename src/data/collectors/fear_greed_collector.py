# src/data/collectors/fear_greed_collector.py

import os
import requests
import pandas as pd
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

class FearGreedCollector:
    """Collecteur Fear & Greed Index"""
    
    def __init__(self):
        self.url = os.getenv('FEAR_GREED_URL', 'https://api.alternative.me/fng/')
        logger.info("✅ Fear & Greed Collector initialisé")
    
    def fetch_current_index(self):
        """
        Récupère l'index actuel
        
        Returns:
            Dict avec valeur et classification
        """
        logger.info("📥 Collecte Fear & Greed actuel...")
        
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            current = data['data'][0]
            
            result = {
                'timestamp': datetime.fromtimestamp(int(current['timestamp'])),
                'value': int(current['value']),
                'classification': current['value_classification']
            }
            
            logger.success(f"✅ Index: {result['value']} - {result['classification']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur collecte Fear & Greed: {e}")
            return None
    
    def fetch_historical(self, days=365):
        """
        Récupère l'historique
        
        Args:
            days: Nombre de jours (max 365)
        
        Returns:
            DataFrame avec l'historique
        """
        logger.info(f"📥 Collecte historique Fear & Greed ({days} jours)...")
        
        try:
            url = f"{self.url}?limit={days}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Transformer en DataFrame
            rows = []
            for entry in data['data']:
                rows.append({
                    'timestamp': datetime.fromtimestamp(int(entry['timestamp'])),
                    'value': int(entry['value']),
                    'classification': entry['value_classification']
                })
            
            df = pd.DataFrame(rows)
            df = df.sort_values('timestamp')  # Ordre chronologique
            
            logger.success(f"✅ {len(df)} jours collectés")
            return df
            
        except Exception as e:
            logger.error(f"❌ Erreur collecte historique: {e}")
            return None
    
    def save_to_csv(self, df, filename=None):
        """
        Sauvegarde le DataFrame en CSV
        
        Args:
            df: DataFrame à sauvegarder
            filename: Nom du fichier (optionnel)
        """
        if df is None or df.empty:
            logger.warning("⚠️ Pas de données à sauvegarder")
            return None
        
        # Créer le dossier data/raw si nécessaire
        os.makedirs('data/raw', exist_ok=True)
        
        # Générer le nom de fichier avec date
        if filename is None:
            date_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f"fear_greed_{date_str}.csv"
        
        filepath = os.path.join('data/raw', filename)
        
        # Sauvegarder
        df.to_csv(filepath, index=False)
        logger.success(f"💾 Données sauvegardées: {filepath}")
        
        return filepath


# Fonction pratique pour usage direct
def collect_fear_greed_data(days=365, save=True):
    """
    Collecte et sauvegarde Fear & Greed Index
    
    Args:
        days: Nombre de jours d'historique
        save: Si True, sauvegarde en CSV
    
    Returns:
        DataFrame avec les données
    """
    collector = FearGreedCollector()
    
    # Collecter l'historique
    df = collector.fetch_historical(days=days)
    
    # Statistiques
    if df is not None and not df.empty:
        logger.info(f"📊 Moyenne: {df['value'].mean():.1f}")
        logger.info(f"📊 Min: {df['value'].min()}")
        logger.info(f"📊 Max: {df['value'].max()}")
    
    # Sauvegarder
    if save and df is not None:
        collector.save_to_csv(df)
    
    return df


# Test du collecteur
if __name__ == "__main__":
    logger.info("🧪 Test Fear & Greed Collector\n")
    
    df = collect_fear_greed_data(days=30, save=True)
    
    if df is not None:
        print("\n📊 Aperçu des données collectées:")
        print(df.head(10).to_string())
        print(f"\n✅ Shape: {df.shape}")