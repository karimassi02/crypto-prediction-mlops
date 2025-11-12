# src/data/collectors/coingecko_collector.py

import os
import requests
import pandas as pd
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

class CoinGeckoCollector:
    """Collecteur de données CoinGecko"""
    
    def __init__(self):
        self.api_key = os.getenv('COINGECKO_API_KEY')
        if not self.api_key:
            raise ValueError("COINGECKO_API_KEY manquante dans .env")
        
        self.base_url = "https://api.coingecko.com/api/v3"
        self.headers = {'x-cg-demo-api-key': self.api_key}
        
        logger.info("✅ CoinGecko Collector initialisé")
    
    def fetch_current_prices(self, symbols=None):
        """
        Récupère les prix actuels + market cap + volume
        
        Args:
            symbols: Liste de cryptos (ex: ['bitcoin', 'ethereum'])
                    Par défaut: BTC, ETH, BNB, SOL, ADA
        
        Returns:
            DataFrame avec les données
        """
        if symbols is None:
            symbols = ['bitcoin', 'ethereum', 'binancecoin', 'solana', 'cardano']
        
        logger.info(f"📥 Collecte CoinGecko pour {len(symbols)} cryptos...")
        
        try:
            url = f"{self.base_url}/simple/price"
            params = {
                'ids': ','.join(symbols),
                'vs_currencies': 'usd',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true',
                'include_24hr_change': 'true',
                'include_last_updated_at': 'true'
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Transformer en DataFrame
            rows = []
            timestamp = datetime.now()
            
            for symbol, info in data.items():
                rows.append({
                    'timestamp': timestamp,
                    'symbol': symbol.upper(),
                    'price_usd': info.get('usd', 0),
                    'market_cap_usd': info.get('usd_market_cap', 0),
                    'volume_24h_usd': info.get('usd_24h_vol', 0),
                    'price_change_24h_percent': info.get('usd_24h_change', 0),
                    'last_updated': datetime.fromtimestamp(info.get('last_updated_at', 0))
                })
            
            df = pd.DataFrame(rows)
            
            logger.success(f"✅ {len(df)} cryptos collectées")
            return df
            
        except Exception as e:
            logger.error(f"❌ Erreur collecte CoinGecko: {e}")
            return None
    
    def fetch_global_data(self):
        """
        Récupère les données globales du marché
        
        Returns:
            Dict avec market cap total, volume, dominance BTC
        """
        logger.info("📥 Collecte données globales...")
        
        try:
            url = f"{self.base_url}/global"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()['data']
            
            global_info = {
                'timestamp': datetime.now(),
                'total_market_cap_usd': data['total_market_cap'].get('usd', 0),
                'total_volume_24h_usd': data['total_volume'].get('usd', 0),
                'btc_dominance_percent': data['market_cap_percentage'].get('btc', 0),
                'eth_dominance_percent': data['market_cap_percentage'].get('eth', 0),
                'active_cryptocurrencies': data.get('active_cryptocurrencies', 0)
            }
            
            logger.success("✅ Données globales collectées")
            return global_info
            
        except Exception as e:
            logger.error(f"❌ Erreur collecte données globales: {e}")
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
            filename = f"coingecko_{date_str}.csv"
        
        filepath = os.path.join('data/raw', filename)
        
        # Sauvegarder
        df.to_csv(filepath, index=False)
        logger.success(f"💾 Données sauvegardées: {filepath}")
        
        return filepath


# Fonction pratique pour usage direct
def collect_coingecko_data(save=True):
    """
    Collecte et sauvegarde les données CoinGecko
    
    Args:
        save: Si True, sauvegarde en CSV
    
    Returns:
        DataFrame avec les données
    """
    collector = CoinGeckoCollector()
    
    # Collecter les prix
    df = collector.fetch_current_prices()
    
    # Collecter données globales
    global_data = collector.fetch_global_data()
    if global_data:
        logger.info(f"📊 Market Cap Total: ${global_data['total_market_cap_usd']:,.0f}")
        logger.info(f"📊 BTC Dominance: {global_data['btc_dominance_percent']:.2f}%")
    
    # Sauvegarder
    if save and df is not None:
        collector.save_to_csv(df)
    
    return df


# Test du collecteur
if __name__ == "__main__":
    logger.info("🧪 Test CoinGecko Collector\n")
    
    df = collect_coingecko_data(save=True)
    
    if df is not None:
        print("\n📊 Aperçu des données collectées:")
        print(df.to_string())
        print(f"\n✅ Shape: {df.shape}")