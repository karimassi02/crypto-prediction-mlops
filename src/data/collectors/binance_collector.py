# src/data/collectors/binance_collector.py

"""
Collecteur de données OHLCV (bougies) depuis Binance
Utilise CCXT pour une interface unifiée
"""

import os
import ccxt
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


class BinanceCollector:
    """
    Collecteur de données OHLCV depuis Binance
    
    OHLCV = Open, High, Low, Close, Volume
    """
    
    def __init__(self):
        """Initialise le collecteur avec les clés API Binance"""
        
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.secret_key = os.getenv('BINANCE_SECRET_KEY')
        
        if not self.api_key or not self.secret_key:
            logger.warning("⚠️ Clés Binance manquantes dans .env")
            logger.info("Ce collecteur nécessite BINANCE_API_KEY et BINANCE_SECRET_KEY")
            raise ValueError("Clés Binance non configurées")
        
        try:
            # Initialiser CCXT avec Binance
            self.exchange = ccxt.binance({
                'apiKey': self.api_key,
                'secret': self.secret_key,
                'enableRateLimit': True,  # Respect des limites API
                'options': {
                    'defaultType': 'spot',  # Trading spot (pas futures)
                    'adjustForTimeDifference': True  # Sync temps
                }
            })
            
            # Test de connexion
            self.exchange.load_markets()
            
            logger.success("✅ Binance Collector initialisé")
            logger.info(f"   Exchange: {self.exchange.id}")
            logger.info(f"   Markets disponibles: {len(self.exchange.markets)}")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation Binance: {e}")
            raise
    
    def fetch_ohlcv(self, symbol='BTC/USDT', timeframe='1d', limit=365, since=None):
        """
        Récupère les données OHLCV (bougies)
        
        Args:
            symbol (str): Paire de trading (ex: 'BTC/USDT', 'ETH/USDT')
            timeframe (str): Intervalle des bougies
                - '1m', '5m', '15m', '30m' (minutes)
                - '1h', '4h' (heures)
                - '1d' (jour)
                - '1w' (semaine)
            limit (int): Nombre de bougies à récupérer (max 1000 par requête)
            since (int): Timestamp de début (millisecondes), None = depuis limit périodes
        
        Returns:
            DataFrame: Colonnes [timestamp, open, high, low, close, volume]
        """
        
        logger.info(f"📥 Collecte OHLCV: {symbol} ({timeframe}, {limit} bougies)")
        
        try:
            # Vérifier que le symbole existe
            if symbol not in self.exchange.markets:
                available = [s for s in self.exchange.markets if 'USDT' in s][:10]
                logger.error(f"❌ Symbole {symbol} non trouvé")
                logger.info(f"   Exemples disponibles: {available}")
                return None
            
            # Récupérer les données
            ohlcv = self.exchange.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                limit=limit,
                since=since
            )
            
            if not ohlcv:
                logger.warning(f"⚠️ Aucune donnée reçue pour {symbol}")
                return None
            
            # Convertir en DataFrame
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            # Convertir timestamp (millisecondes) en datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Ajouter infos supplémentaires
            df['symbol'] = symbol.replace('/', '')  # BTC/USDT -> BTCUSDT
            df['timeframe'] = timeframe
            
            # Calculer quelques métriques utiles
            df['price_change'] = df['close'] - df['open']
            df['price_change_pct'] = (df['price_change'] / df['open']) * 100
            df['high_low_spread'] = df['high'] - df['low']
            df['volume_usd'] = df['volume'] * df['close']  # Approximation
            
            logger.success(f"✅ {len(df)} bougies collectées pour {symbol}")
            logger.info(f"   Période: {df['timestamp'].min()} → {df['timestamp'].max()}")
            logger.info(f"   Prix: ${df['close'].iloc[-1]:,.2f} (dernier)")
            
            return df
            
        except ccxt.NetworkError as e:
            logger.error(f"❌ Erreur réseau: {e}")
            return None
        except ccxt.ExchangeError as e:
            logger.error(f"❌ Erreur Binance: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur inattendue: {e}")
            return None
    
    def fetch_multiple_symbols(self, symbols=None, timeframe='1d', limit=365):
        """
        Collecte OHLCV pour plusieurs cryptos
        
        Args:
            symbols (list): Liste de paires (défaut: BTC, ETH, BNB, SOL, ADA)
            timeframe (str): Intervalle
            limit (int): Nombre de bougies
        
        Returns:
            dict: {symbol: DataFrame}
        """
        
        if symbols is None:
            symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'ADA/USDT']
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📥 COLLECTE MULTIPLE: {len(symbols)} cryptos")
        logger.info(f"{'='*60}\n")
        
        results = {}
        
        for i, symbol in enumerate(symbols, 1):
            logger.info(f"[{i}/{len(symbols)}] {symbol}")
            
            df = self.fetch_ohlcv(symbol, timeframe, limit)
            
            if df is not None:
                results[symbol] = df
                logger.info("")
            else:
                logger.warning(f"⚠️ {symbol} ignoré (erreur)\n")
        
        logger.info(f"{'='*60}")
        logger.success(f"✅ Collecte terminée: {len(results)}/{len(symbols)} cryptos")
        logger.info(f"{'='*60}")
        
        return results
    
    def fetch_historical_range(self, symbol='BTC/USDT', timeframe='1d', days_back=365):
        """
        Collecte historique complet (gère la limite de 1000 bougies)
        
        Args:
            symbol (str): Paire
            timeframe (str): Intervalle
            days_back (int): Nombre de jours d'historique
        
        Returns:
            DataFrame: Données complètes
        """
        
        logger.info(f"📅 Collecte historique: {symbol} ({days_back} jours)")
        
        # Binance limite à 1000 bougies par requête
        # Pour 1 an (365 jours) avec timeframe='1d', une requête suffit
        # Pour timeframes plus courts, faire plusieurs requêtes
        
        timeframe_to_ms = {
            '1m': 60 * 1000,
            '5m': 5 * 60 * 1000,
            '15m': 15 * 60 * 1000,
            '1h': 60 * 60 * 1000,
            '4h': 4 * 60 * 60 * 1000,
            '1d': 24 * 60 * 60 * 1000,
        }
        
        if timeframe not in timeframe_to_ms:
            logger.warning(f"⚠️ Timeframe {timeframe} non supporté, utilise fetch_ohlcv directement")
            return self.fetch_ohlcv(symbol, timeframe, limit=days_back)
        
        # Calculer nombre de bougies nécessaires
        ms_per_candle = timeframe_to_ms[timeframe]
        ms_back = days_back * 24 * 60 * 60 * 1000
        candles_needed = ms_back // ms_per_candle
        
        if candles_needed <= 1000:
            # Une seule requête suffit
            return self.fetch_ohlcv(symbol, timeframe, limit=int(candles_needed))
        
        # Plusieurs requêtes nécessaires
        logger.info(f"   {candles_needed} bougies nécessaires → plusieurs requêtes")
        
        all_data = []
        since = self.exchange.milliseconds() - ms_back
        
        while len(all_data) < candles_needed:
            df = self.fetch_ohlcv(symbol, timeframe, limit=1000, since=since)
            
            if df is None or df.empty:
                break
            
            all_data.append(df)
            
            # Prochaine requête commence après la dernière bougie
            since = int(df['timestamp'].iloc[-1].timestamp() * 1000) + ms_per_candle
            
            logger.info(f"   Collecté: {sum(len(d) for d in all_data)}/{candles_needed}")
            
            if len(df) < 1000:
                # Dernière requête
                break
        
        if not all_data:
            logger.error("❌ Aucune donnée collectée")
            return None
        
        # Fusionner tous les DataFrames
        df_complete = pd.concat(all_data, ignore_index=True)
        df_complete = df_complete.drop_duplicates(subset=['timestamp']).sort_values('timestamp')
        
        logger.success(f"✅ Historique complet: {len(df_complete)} bougies")
        
        return df_complete
    
    def save_to_csv(self, df, filename=None, output_dir='data/raw'):
        """
        Sauvegarde les données OHLCV en CSV
        
        Args:
            df (DataFrame): Données à sauvegarder
            filename (str): Nom du fichier (auto si None)
            output_dir (str): Dossier de sortie
        
        Returns:
            str: Chemin du fichier sauvegardé
        """
        
        if df is None or df.empty:
            logger.warning("⚠️ Pas de données à sauvegarder")
            return None
        
        # Créer le dossier si nécessaire
        os.makedirs(output_dir, exist_ok=True)
        
        # Générer nom de fichier si non fourni
        if filename is None:
            symbol = df['symbol'].iloc[0].lower()
            timeframe = df['timeframe'].iloc[0]
            date_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f"binance_{symbol}_{timeframe}_{date_str}.csv"
        
        filepath = os.path.join(output_dir, filename)
        
        # Sauvegarder
        df.to_csv(filepath, index=False)
        
        logger.success(f"💾 Données sauvegardées: {filepath}")
        logger.info(f"   Lignes: {len(df)}")
        logger.info(f"   Colonnes: {len(df.columns)}")
        logger.info(f"   Taille: {os.path.getsize(filepath) / 1024:.1f} KB")
        
        return filepath


# Fonction utilitaire pour usage simple
def collect_binance_data(symbols=None, timeframe='1d', days_back=365, save=True):
    """
    Fonction simple pour collecter données Binance
    
    Args:
        symbols (list): Liste de cryptos (défaut: BTC, ETH, BNB, SOL, ADA)
        timeframe (str): Intervalle (défaut: 1 jour)
        days_back (int): Historique en jours (défaut: 365)
        save (bool): Sauvegarder en CSV (défaut: True)
    
    Returns:
        dict: {symbol: DataFrame}
    """
    
    try:
        collector = BinanceCollector()
        
        if symbols is None:
            symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'ADA/USDT']
        
        results = {}
        
        for symbol in symbols:
            df = collector.fetch_historical_range(symbol, timeframe, days_back)
            
            if df is not None:
                results[symbol] = df
                
                if save:
                    collector.save_to_csv(df)
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Erreur collecte Binance: {e}")
        return {}


# Pour tester (ne s'exécute que si lancé directement)
if __name__ == "__main__":
    
    logger.info("="*60)
    logger.info("🧪 TEST BINANCE COLLECTOR")
    logger.info("="*60)
    
    # Vérifier que les clés existent
    if not os.getenv('BINANCE_API_KEY'):
        logger.warning("\n⚠️ BINANCE_API_KEY non trouvée dans .env")
        logger.info("Ajoutez vos clés Binance après validation KYC:")
        logger.info("  BINANCE_API_KEY=votre_cle")
        logger.info("  BINANCE_SECRET_KEY=votre_secret\n")
        exit(0)
    
    # Test avec 30 derniers jours
    logger.info("\n🧪 Test collecte Bitcoin (30 derniers jours)...\n")
    
    results = collect_binance_data(
        symbols=['BTC/USDT'],
        timeframe='1d',
        days_back=30,
        save=False
    )
    
    if results:
        df = results['BTC/USDT']
        logger.info("\n📊 Aperçu des données:\n")
        print(df.head(10))
        print(f"\n... ({len(df)} lignes au total)")
        
        logger.info("\n📈 Statistiques:")
        logger.info(f"   Prix min: ${df['low'].min():,.2f}")
        logger.info(f"   Prix max: ${df['high'].max():,.2f}")
        logger.info(f"   Prix actuel: ${df['close'].iloc[-1]:,.2f}")
        logger.info(f"   Volume moyen: ${df['volume_usd'].mean()/1e9:.2f}B")
        
        logger.success("\n✅ Test réussi !")
    else:
        logger.error("\n❌ Test échoué")