# src/features/technical_indicators.py

"""
Fonctions de calcul d'indicateurs techniques pour l'analyse crypto
"""

import pandas as pd
import numpy as np


def calculate_sma(df, column='price_usd', window=7):
    """
    Calcule la Simple Moving Average (Moyenne Mobile Simple)
    
    Args:
        df: DataFrame avec les données
        column: Colonne sur laquelle calculer (par défaut 'price_usd')
        window: Fenêtre temporelle (par défaut 7 jours)
    
    Returns:
        Series avec les valeurs SMA
    """
    return df[column].rolling(window=window, min_periods=1).mean()


def calculate_ema(df, column='price_usd', span=12):
    """
    Calcule l'Exponential Moving Average (Moyenne Mobile Exponentielle)
    
    Args:
        df: DataFrame avec les données
        column: Colonne sur laquelle calculer
        span: Période (par défaut 12)
    
    Returns:
        Series avec les valeurs EMA
    """
    return df[column].ewm(span=span, adjust=False).mean()


def calculate_rsi(df, column='price_usd', period=14):
    """
    Calcule le Relative Strength Index (RSI)
    
    RSI > 70 : Sur-acheté (potentiel de baisse)
    RSI < 30 : Sur-vendu (potentiel de hausse)
    
    Args:
        df: DataFrame avec les données
        column: Colonne sur laquelle calculer
        period: Période de calcul (par défaut 14)
    
    Returns:
        Series avec les valeurs RSI (0-100)
    """
    # Calculer les variations
    delta = df[column].diff()
    
    # Séparer gains et pertes
    gain = (delta.where(delta > 0, 0)).rolling(window=period, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=1).mean()
    
    # Calculer RS et RSI
    rs = gain / loss.replace(0, np.nan)  # Éviter division par 0
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.fillna(50)  # Valeur neutre par défaut


def calculate_macd(df, column='price_usd', fast=12, slow=26, signal=9):
    """
    Calcule le MACD (Moving Average Convergence Divergence)
    
    MACD > Signal : Signal haussier
    MACD < Signal : Signal baissier
    
    Args:
        df: DataFrame avec les données
        column: Colonne sur laquelle calculer
        fast: Période EMA rapide (défaut 12)
        slow: Période EMA lente (défaut 26)
        signal: Période signal (défaut 9)
    
    Returns:
        DataFrame avec colonnes macd, signal, histogram
    """
    # EMA rapide et lente
    ema_fast = calculate_ema(df, column, span=fast)
    ema_slow = calculate_ema(df, column, span=slow)
    
    # MACD line
    macd_line = ema_fast - ema_slow
    
    # Signal line
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    
    # Histogram
    histogram = macd_line - signal_line
    
    return pd.DataFrame({
        'macd': macd_line,
        'macd_signal': signal_line,
        'macd_histogram': histogram
    })


def calculate_bollinger_bands(df, column='price_usd', window=20, num_std=2):
    """
    Calcule les Bandes de Bollinger
    
    Prix > Upper Band : Sur-acheté
    Prix < Lower Band : Sur-vendu
    
    Args:
        df: DataFrame avec les données
        column: Colonne sur laquelle calculer
        window: Fenêtre temporelle (défaut 20)
        num_std: Nombre d'écarts-types (défaut 2)
    
    Returns:
        DataFrame avec upper, middle, lower bands
    """
    # Bande du milieu (SMA)
    middle_band = calculate_sma(df, column, window)
    
    # Écart-type
    std = df[column].rolling(window=window, min_periods=1).std()
    
    # Bandes supérieure et inférieure
    upper_band = middle_band + (std * num_std)
    lower_band = middle_band - (std * num_std)
    
    return pd.DataFrame({
        'bb_upper': upper_band,
        'bb_middle': middle_band,
        'bb_lower': lower_band,
        'bb_width': upper_band - lower_band
    })


def calculate_price_changes(df, column='price_usd', periods=[1, 7, 30]):
    """
    Calcule les variations de prix sur différentes périodes
    
    Args:
        df: DataFrame avec les données
        column: Colonne prix
        periods: Liste de périodes (jours)
    
    Returns:
        DataFrame avec les variations (%)
    """
    result = pd.DataFrame()
    
    for period in periods:
        result[f'price_change_{period}d'] = df[column].pct_change(periods=period) * 100
    
    return result


def calculate_volume_indicators(df, volume_col='volume_24h_usd'):
    """
    Calcule des indicateurs basés sur le volume
    
    Args:
        df: DataFrame avec les données
        volume_col: Colonne volume
    
    Returns:
        DataFrame avec indicateurs de volume
    """
    result = pd.DataFrame()
    
    # Moyenne mobile du volume
    result['volume_ma_7'] = df[volume_col].rolling(window=7, min_periods=1).mean()
    result['volume_ma_30'] = df[volume_col].rolling(window=30, min_periods=1).mean()
    
    # Ratio volume actuel / moyenne
    result['volume_ratio'] = df[volume_col] / result['volume_ma_7']
    
    # Variation de volume
    result['volume_change_1d'] = df[volume_col].pct_change(periods=1) * 100
    
    # Spike de volume (> 2x la moyenne)
    result['volume_spike'] = (result['volume_ratio'] > 2).astype(int)
    
    return result