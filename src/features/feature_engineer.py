# src/features/feature_engineer.py

"""
Feature Engineering pour les données crypto
Transforme les données brutes en features ML-ready
"""

import pandas as pd
import numpy as np
from datetime import datetime
from loguru import logger

from .technical_indicators import (
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_price_changes,
    calculate_volume_indicators
)


class CryptoFeatureEngineer:
    """
    Classe principale pour le feature engineering des données crypto
    """
    
    def __init__(self):
        logger.info("✅ CryptoFeatureEngineer initialisé")
    
    def add_technical_indicators(self, df, price_col='price_usd', volume_col='volume_24h_usd'):
        """
        Ajoute tous les indicateurs techniques au DataFrame
        
        Args:
            df: DataFrame avec prix et volume
            price_col: Nom colonne prix
            volume_col: Nom colonne volume
        
        Returns:
            DataFrame enrichi avec indicateurs techniques
        """
        logger.info("📊 Calcul des indicateurs techniques...")
        
        df = df.copy()
        
        # Moving Averages
        df['sma_7'] = calculate_sma(df, price_col, window=7)
        df['sma_30'] = calculate_sma(df, price_col, window=30)
        df['ema_12'] = calculate_ema(df, price_col, span=12)
        df['ema_26'] = calculate_ema(df, price_col, span=26)
        
        # RSI
        df['rsi_14'] = calculate_rsi(df, price_col, period=14)
        
        # MACD
        macd_df = calculate_macd(df, price_col)
        df = pd.concat([df, macd_df], axis=1)
        
        # Bollinger Bands
        bb_df = calculate_bollinger_bands(df, price_col)
        df = pd.concat([df, bb_df], axis=1)
        
        # Price Changes
        changes_df = calculate_price_changes(df, price_col, periods=[1, 7, 30])
        df = pd.concat([df, changes_df], axis=1)
        
        # Volume Indicators
        if volume_col in df.columns:
            volume_df = calculate_volume_indicators(df, volume_col)
            df = pd.concat([df, volume_df], axis=1)
        
        # Price to SMA ratio (signal de tendance)
        df['price_to_sma7_ratio'] = df[price_col] / df['sma_7']
        df['price_to_sma30_ratio'] = df[price_col] / df['sma_30']
        
        # SMA Crossover (signal d'achat/vente)
        df['sma_crossover'] = (df['sma_7'] > df['sma_30']).astype(int)
        
        logger.success(f"✅ {len(df.columns)} features créées (indicateurs techniques)")
        
        return df
    
    def add_temporal_features(self, df, timestamp_col='timestamp'):
        """
        Ajoute des features temporelles
        
        Args:
            df: DataFrame avec colonne timestamp
            timestamp_col: Nom colonne timestamp
        
        Returns:
            DataFrame avec features temporelles
        """
        logger.info("📅 Ajout des features temporelles...")
        
        df = df.copy()
        
        # Convertir en datetime si nécessaire
        if not pd.api.types.is_datetime64_any_dtype(df[timestamp_col]):
            df[timestamp_col] = pd.to_datetime(df[timestamp_col])
        
        # Extraire composantes temporelles
        df['year'] = df[timestamp_col].dt.year
        df['month'] = df[timestamp_col].dt.month
        df['day'] = df[timestamp_col].dt.day
        df['day_of_week'] = df[timestamp_col].dt.dayofweek  # 0=Lundi, 6=Dimanche
        df['hour'] = df[timestamp_col].dt.hour
        df['quarter'] = df[timestamp_col].dt.quarter
        
        # Features binaires
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)  # Samedi/Dimanche
        df['is_month_start'] = df[timestamp_col].dt.is_month_start.astype(int)
        df['is_month_end'] = df[timestamp_col].dt.is_month_end.astype(int)
        
        logger.success("✅ Features temporelles ajoutées")
        
        return df
    
    def add_sentiment_features(self, df_price, df_fear_greed):
        """
        Fusionne et enrichit avec les données Fear & Greed
        
        Args:
            df_price: DataFrame avec prix
            df_fear_greed: DataFrame Fear & Greed
        
        Returns:
            DataFrame fusionné avec features sentiment
        """
        logger.info("😱 Ajout des features de sentiment...")
        
        df_price = df_price.copy()
        df_fear_greed = df_fear_greed.copy()
        
        # Convertir timestamps
        df_price['date'] = pd.to_datetime(df_price['timestamp']).dt.date
        df_fear_greed['date'] = pd.to_datetime(df_fear_greed['timestamp']).dt.date
        
        # Préparer Fear & Greed
        df_fg = df_fear_greed[['date', 'value']].rename(columns={'value': 'fear_greed_index'})
        
        # Fusionner
        df = df_price.merge(df_fg, on='date', how='left')
        
        # Forward fill pour remplir les valeurs manquantes
        df['fear_greed_index'] = df['fear_greed_index'].ffill()
        
        # Features Fear & Greed
        df['fg_ma_7'] = df['fear_greed_index'].rolling(window=7, min_periods=1).mean()
        df['fg_ma_30'] = df['fear_greed_index'].rolling(window=30, min_periods=1).mean()
        df['fg_change_7d'] = df['fear_greed_index'].diff(periods=7)
        
        # Catégories binaires
        df['is_extreme_fear'] = (df['fear_greed_index'] <= 25).astype(int)
        df['is_fear'] = ((df['fear_greed_index'] > 25) & (df['fear_greed_index'] <= 45)).astype(int)
        df['is_neutral'] = ((df['fear_greed_index'] > 45) & (df['fear_greed_index'] <= 55)).astype(int)
        df['is_greed'] = ((df['fear_greed_index'] > 55) & (df['fear_greed_index'] <= 75)).astype(int)
        df['is_extreme_greed'] = (df['fear_greed_index'] > 75).astype(int)
        
        # Nettoyer
        df = df.drop('date', axis=1)
        
        logger.success("✅ Features sentiment ajoutées")
        
        return df
    
    def add_lag_features(self, df, columns=['price_usd'], lags=[1, 7, 30]):
        """
        Ajoute des features retardées (valeurs passées)
        
        Args:
            df: DataFrame
            columns: Colonnes à décaler
            lags: Périodes de décalage
        
        Returns:
            DataFrame avec features lag
        """
        logger.info("⏮️ Ajout des features lag...")
        
        df = df.copy()
        
        for col in columns:
            if col in df.columns:
                for lag in lags:
                    df[f'{col}_lag_{lag}d'] = df[col].shift(lag)
        
        logger.success(f"✅ Features lag ajoutées ({len(columns)} colonnes × {len(lags)} lags)")
        
        return df
    
    def create_all_features(self, df_price, df_fear_greed=None, add_lags=True):
        """
        Pipeline complet : crée toutes les features
        
        Args:
            df_price: DataFrame prix/volume
            df_fear_greed: DataFrame Fear & Greed (optionnel)
            add_lags: Ajouter features lag (défaut True)
        
        Returns:
            DataFrame complet avec toutes les features
        """
        logger.info("🚀 Début du pipeline de feature engineering...")
        
        # 1. Indicateurs techniques
        df = self.add_technical_indicators(df_price)
        
        # 2. Features temporelles
        df = self.add_temporal_features(df)
        
        # 3. Features sentiment (si disponible)
        if df_fear_greed is not None:
            df = self.add_sentiment_features(df, df_fear_greed)
        
        # 4. Features lag
        if add_lags:
            df = self.add_lag_features(df, columns=['price_usd', 'volume_24h_usd'])
        
        # Supprimer lignes avec trop de NaN (début de série)
        initial_rows = len(df)
        df = df.dropna(subset=['price_usd', 'sma_7', 'rsi_14'])
        removed_rows = initial_rows - len(df)
        
        if removed_rows > 0:
            logger.warning(f"⚠️ {removed_rows} lignes supprimées (valeurs manquantes)")
        
        logger.success(f"🎉 Feature engineering terminé ! {len(df)} lignes × {len(df.columns)} colonnes")
        
        return df


# Fonction pratique pour usage direct
def engineer_features(df_price, df_fear_greed=None, save_path=None):
    """
    Fonction simple pour créer toutes les features
    
    Args:
        df_price: DataFrame prix
        df_fear_greed: DataFrame Fear & Greed (optionnel)
        save_path: Chemin sauvegarde CSV (optionnel)
    
    Returns:
        DataFrame avec features
    """
    engineer = CryptoFeatureEngineer()
    df_features = engineer.create_all_features(df_price, df_fear_greed)
    
    if save_path:
        df_features.to_csv(save_path, index=False)
        logger.success(f"💾 Features sauvegardées : {save_path}")
    
    return df_features