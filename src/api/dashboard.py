# src/api/dashboard.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import glob
import os

# Configuration de la page
st.set_page_config(
    page_title="Crypto Prediction Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre principal
st.title("📈 Crypto Prediction Dashboard")
st.markdown("---")

# ============================================
# FONCTIONS UTILITAIRES
# ============================================

@st.cache_data(ttl=60)
def load_latest_data():
    """Charge les dernières données collectées"""
    
    coingecko_files = glob.glob('data/raw/coingecko_*.csv')
    fear_greed_files = glob.glob('data/raw/fear_greed_*.csv')
    
    if not coingecko_files or not fear_greed_files:
        return None, None
    
    latest_coingecko = max(coingecko_files, key=os.path.getctime)
    latest_fear_greed = max(fear_greed_files, key=os.path.getctime)
    
    df_cg = pd.read_csv(latest_coingecko)
    df_fg = pd.read_csv(latest_fear_greed)
    
    df_cg['timestamp'] = pd.to_datetime(df_cg['timestamp'])
    df_fg['timestamp'] = pd.to_datetime(df_fg['timestamp'])
    
    return df_cg, df_fg

@st.cache_data(ttl=60)
def load_features_data():
    """Charge les données avec features techniques"""
    
    feature_files = glob.glob('data/processed/*_features_*.csv')
    
    if not feature_files:
        return None
    
    # Grouper par crypto et prendre le plus récent
    cryptos_data = {}
    for file in feature_files:
        basename = os.path.basename(file)
        crypto = basename.split('_features_')[0].upper()
        if crypto not in cryptos_data or os.path.getctime(file) > os.path.getctime(cryptos_data[crypto]['file']):
            cryptos_data[crypto] = {
                'file': file,
                'df': pd.read_csv(file)
            }
    
    # Convertir en dict de DataFrames
    result = {crypto: data['df'] for crypto, data in cryptos_data.items()}
    
    return result

def get_emoji_for_fear_greed(value):
    """Retourne l'emoji correspondant à la valeur Fear & Greed"""
    if value <= 25:
        return "😱"
    elif value <= 45:
        return "😰"
    elif value <= 55:
        return "😐"
    elif value <= 75:
        return "😃"
    else:
        return "🤑"

def get_rsi_signal(rsi):
    """Retourne le signal basé sur RSI"""
    if rsi < 30:
        return "🟢 SUR-VENDU (Achat)", "green"
    elif rsi > 70:
        return "🔴 SUR-ACHETÉ (Vente)", "red"
    else:
        return "🟡 NEUTRE", "orange"

# ============================================
# CHARGEMENT DES DONNÉES
# ============================================

df_coingecko, df_fear_greed = load_latest_data()
df_features = load_features_data()

if df_coingecko is None or df_fear_greed is None:
    st.error("❌ Aucune donnée trouvée. Lancez d'abord : `python collect_data.py`")
    st.stop()

# ============================================
# SIDEBAR - INFORMATIONS
# ============================================

st.sidebar.header("ℹ️ Informations")

last_update = df_coingecko['timestamp'].max()
st.sidebar.metric("📅 Dernière mise à jour", last_update.strftime('%Y-%m-%d %H:%M'))

nb_cryptos = len(df_coingecko)
st.sidebar.metric("💰 Cryptos suivies", nb_cryptos)

nb_days = len(df_fear_greed)
st.sidebar.metric("📊 Historique F&G", f"{nb_days} jours")

if df_features:
    st.sidebar.metric("🔧 Features disponibles", "✅ Oui")
else:
    st.sidebar.metric("🔧 Features disponibles", "❌ Non")
    st.sidebar.info("Lancez `python process_features.py` pour créer les features")

st.sidebar.markdown("---")

# Sélection crypto
st.sidebar.header("🎯 Sélection")
selected_crypto = st.sidebar.selectbox(
    "Choisir une crypto:",
    options=df_coingecko['symbol'].unique(),
    index=0
)

crypto_data = df_coingecko[df_coingecko['symbol'] == selected_crypto].iloc[0]

st.sidebar.markdown("---")
st.sidebar.markdown("**🔄 Actualisation automatique**")
auto_refresh = st.sidebar.checkbox("Activer (60s)", value=False)

if auto_refresh:
    import time
    time.sleep(60)
    st.rerun()

# ============================================
# SECTION 1 : MÉTRIQUES PRINCIPALES
# ============================================

st.header(f"💰 {selected_crypto} - Vue d'ensemble")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Prix USD",
        f"${crypto_data['price_usd']:,.2f}",
        delta=f"{crypto_data['price_change_24h_percent']:.2f}%"
    )

with col2:
    st.metric(
        "Market Cap",
        f"${crypto_data['market_cap_usd']/1e9:.2f}B",
    )

with col3:
    st.metric(
        "Volume 24h",
        f"${crypto_data['volume_24h_usd']/1e9:.2f}B",
    )

with col4:
    current_fg = df_fear_greed.iloc[-1]
    emoji = get_emoji_for_fear_greed(current_fg['value'])
    st.metric(
        f"{emoji} Fear & Greed",
        f"{current_fg['value']}/100",
        delta=current_fg['classification']
    )

st.markdown("---")

# ============================================
# ONGLETS PRINCIPAUX
# ============================================

tab1, tab2, tab3, tab4 = st.tabs(["📊 Vue d'ensemble", "🔧 Indicateurs Techniques", "😱 Fear & Greed", "📋 Données Brutes"])

# ============================================
# TAB 1 : VUE D'ENSEMBLE
# ============================================

with tab1:
    st.header("📊 Comparaison des Prix")
    
    fig_prices = px.bar(
        df_coingecko,
        x='symbol',
        y='price_usd',
        color='price_change_24h_percent',
        color_continuous_scale=['red', 'yellow', 'green'],
        title="Prix et Variation 24h",
        labels={'price_usd': 'Prix (USD)', 'symbol': 'Crypto'},
        text='price_usd'
    )
    
    fig_prices.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
    fig_prices.update_layout(height=400)
    
    st.plotly_chart(fig_prices, use_container_width=True)

# ============================================
# TAB 2 : INDICATEURS TECHNIQUES
# ============================================

with tab2:
    if df_features and selected_crypto in df_features:
        df_feat = df_features[selected_crypto]
        
        st.header(f"🔧 Indicateurs Techniques - {selected_crypto}")
        
        # Métriques RSI, MACD, etc.
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'rsi_14' in df_feat.columns:
                rsi_value = df_feat['rsi_14'].iloc[0]
                rsi_signal, rsi_color = get_rsi_signal(rsi_value)
                st.metric("RSI (14)", f"{rsi_value:.1f}", delta=rsi_signal)
        
        with col2:
            if 'sma_crossover' in df_feat.columns:
                crossover = df_feat['sma_crossover'].iloc[0]
                if crossover == 1:
                    st.metric("SMA Crossover", "✅ Golden Cross", delta="Tendance haussière")
                else:
                    st.metric("SMA Crossover", "❌ Death Cross", delta="Tendance baissière")
        
        with col3:
            if 'macd_histogram' in df_feat.columns:
                macd_hist = df_feat['macd_histogram'].iloc[0]
                if macd_hist > 0:
                    st.metric("MACD", f"{macd_hist:.2f}", delta="Signal haussier")
                else:
                    st.metric("MACD", f"{macd_hist:.2f}", delta="Signal baissier")
        
        with col4:
            if 'volume_spike' in df_feat.columns:
                spike = df_feat['volume_spike'].iloc[0]
                if spike == 1:
                    st.metric("Volume", "🚀 SPIKE", delta="Volume anormal")
                else:
                    st.metric("Volume", "📊 Normal", delta="Pas de spike")
        
        st.markdown("---")
        
        # Graphiques des indicateurs
        
        # Note : Pour avoir de vrais graphiques, il faut des données historiques
        # Pour l'instant on affiche les valeurs actuelles
        
        st.subheader("📈 Moyennes Mobiles (SMA)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if all(c in df_feat.columns for c in ['price_usd', 'sma_7', 'sma_30']):
                data_sma = {
                    'Indicateur': ['Prix Actuel', 'SMA 7j', 'SMA 30j'],
                    'Valeur': [
                        df_feat['price_usd'].iloc[0],
                        df_feat['sma_7'].iloc[0],
                        df_feat['sma_30'].iloc[0]
                    ]
                }
                df_sma = pd.DataFrame(data_sma)
                
                fig_sma = px.bar(
                    df_sma,
                    x='Indicateur',
                    y='Valeur',
                    title="Comparaison Prix vs SMA",
                    text='Valeur'
                )
                fig_sma.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
                st.plotly_chart(fig_sma, use_container_width=True)
        
        with col2:
            if all(c in df_feat.columns for c in ['price_to_sma7_ratio', 'price_to_sma30_ratio']):
                ratio_7 = df_feat['price_to_sma7_ratio'].iloc[0]
                ratio_30 = df_feat['price_to_sma30_ratio'].iloc[0]
                
                st.metric("Prix / SMA 7j", f"{ratio_7:.3f}", 
                         delta="Au-dessus" if ratio_7 > 1 else "En-dessous")
                st.metric("Prix / SMA 30j", f"{ratio_30:.3f}",
                         delta="Au-dessus" if ratio_30 > 1 else "En-dessous")
                
                if ratio_7 > 1 and ratio_30 > 1:
                    st.success("✅ Prix au-dessus des moyennes mobiles (signal haussier)")
                elif ratio_7 < 1 and ratio_30 < 1:
                    st.error("❌ Prix en-dessous des moyennes mobiles (signal baissier)")
                else:
                    st.warning("⚠️ Prix entre SMA 7j et SMA 30j (indécis)")
        
        st.markdown("---")
        
        # Bollinger Bands
        st.subheader("📊 Bandes de Bollinger")
        
        if all(c in df_feat.columns for c in ['bb_upper', 'bb_middle', 'bb_lower', 'price_usd']):
            col1, col2 = st.columns(2)
            
            with col1:
                data_bb = {
                    'Bande': ['Supérieure', 'Milieu (SMA 20)', 'Inférieure', 'Prix Actuel'],
                    'Valeur': [
                        df_feat['bb_upper'].iloc[0],
                        df_feat['bb_middle'].iloc[0],
                        df_feat['bb_lower'].iloc[0],
                        df_feat['price_usd'].iloc[0]
                    ]
                }
                df_bb = pd.DataFrame(data_bb)
                
                fig_bb = px.bar(
                    df_bb,
                    x='Bande',
                    y='Valeur',
                    title="Bandes de Bollinger",
                    text='Valeur'
                )
                fig_bb.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
                st.plotly_chart(fig_bb, use_container_width=True)
            
            with col2:
                price = df_feat['price_usd'].iloc[0]
                bb_upper = df_feat['bb_upper'].iloc[0]
                bb_lower = df_feat['bb_lower'].iloc[0]
                
                if price > bb_upper:
                    st.error("🔴 Prix au-dessus de la bande supérieure (sur-acheté)")
                elif price < bb_lower:
                    st.success("🟢 Prix en-dessous de la bande inférieure (sur-vendu)")
                else:
                    st.info("🔵 Prix dans les bandes (normal)")
                
                st.metric("Largeur des bandes", f"${df_feat['bb_width'].iloc[0]:,.2f}",
                         delta="Volatilité actuelle")
        
        st.markdown("---")
        
        # Tableau récapitulatif
        st.subheader("📋 Récapitulatif des Indicateurs")
        
        indicators_data = []
        
        if 'rsi_14' in df_feat.columns:
            rsi = df_feat['rsi_14'].iloc[0]
            signal, _ = get_rsi_signal(rsi)
            indicators_data.append({
                'Indicateur': 'RSI (14)',
                'Valeur': f"{rsi:.1f}",
                'Signal': signal
            })
        
        if all(c in df_feat.columns for c in ['sma_7', 'sma_30']):
            sma7 = df_feat['sma_7'].iloc[0]
            sma30 = df_feat['sma_30'].iloc[0]
            indicators_data.append({
                'Indicateur': 'SMA 7j',
                'Valeur': f"${sma7:,.2f}",
                'Signal': '🟢 Support' if price > sma7 else '🔴 Résistance'
            })
            indicators_data.append({
                'Indicateur': 'SMA 30j',
                'Valeur': f"${sma30:,.2f}",
                'Signal': '🟢 Support' if price > sma30 else '🔴 Résistance'
            })
        
        if 'macd' in df_feat.columns:
            macd = df_feat['macd'].iloc[0]
            indicators_data.append({
                'Indicateur': 'MACD',
                'Valeur': f"{macd:.2f}",
                'Signal': '🟢 Haussier' if macd > 0 else '🔴 Baissier'
            })
        
        if indicators_data:
            df_indicators = pd.DataFrame(indicators_data)
            st.dataframe(df_indicators, use_container_width=True, hide_index=True)
        
    else:
        st.warning("⚠️ Pas de features techniques disponibles pour cette crypto.")
        st.info("💡 Lancez `python process_features.py` pour générer les indicateurs techniques.")

# ============================================
# TAB 3 : FEAR & GREED
# ============================================

with tab3:
    st.header("😱 Fear & Greed Index - Historique")
    
    df_fear_greed['color'] = df_fear_greed['value'].apply(
        lambda x: 'darkred' if x <= 25 else 'orange' if x <= 45 else 'gray' if x <= 55 else 'lightgreen' if x <= 75 else 'darkgreen'
    )
    
    fig_fg = go.Figure()
    
    fig_fg.add_trace(go.Scatter(
        x=df_fear_greed['timestamp'],
        y=df_fear_greed['value'],
        mode='lines+markers',
        name='Fear & Greed Index',
        line=dict(color='blue', width=2),
        marker=dict(size=4),
        fill='tozeroy',
        fillcolor='rgba(0,100,255,0.1)'
    ))
    
    fig_fg.add_hline(y=25, line_dash="dash", line_color="red", annotation_text="Extreme Fear")
    fig_fg.add_hline(y=75, line_dash="dash", line_color="green", annotation_text="Extreme Greed")
    
    fig_fg.update_layout(
        title="Fear & Greed Index sur 365 jours",
        xaxis_title="Date",
        yaxis_title="Index (0-100)",
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_fg, use_container_width=True)
    
    # Statistiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Statistiques Fear & Greed")
        
        stats_df = pd.DataFrame({
            'Métrique': ['Moyenne', 'Médiane', 'Min', 'Max', 'Écart-type'],
            'Valeur': [
                f"{df_fear_greed['value'].mean():.1f}",
                f"{df_fear_greed['value'].median():.1f}",
                f"{df_fear_greed['value'].min()}",
                f"{df_fear_greed['value'].max()}",
                f"{df_fear_greed['value'].std():.1f}"
            ]
        })
        
        st.dataframe(stats_df, hide_index=True, use_container_width=True)
    
    with col2:
        st.subheader("🎨 Distribution")
        
        extreme_fear = len(df_fear_greed[df_fear_greed['value'] <= 25])
        fear = len(df_fear_greed[(df_fear_greed['value'] > 25) & (df_fear_greed['value'] <= 45)])
        neutral = len(df_fear_greed[(df_fear_greed['value'] > 45) & (df_fear_greed['value'] <= 55)])
        greed = len(df_fear_greed[(df_fear_greed['value'] > 55) & (df_fear_greed['value'] <= 75)])
        extreme_greed = len(df_fear_greed[df_fear_greed['value'] > 75])
        
        distribution_df = pd.DataFrame({
            'Zone': ['😱 Extreme Fear', '😰 Fear', '😐 Neutral', '😃 Greed', '🤑 Extreme Greed'],
            'Jours': [extreme_fear, fear, neutral, greed, extreme_greed],
            'Pourcentage': [
                f"{extreme_fear/len(df_fear_greed)*100:.1f}%",
                f"{fear/len(df_fear_greed)*100:.1f}%",
                f"{neutral/len(df_fear_greed)*100:.1f}%",
                f"{greed/len(df_fear_greed)*100:.1f}%",
                f"{extreme_greed/len(df_fear_greed)*100:.1f}%"
            ]
        })
        
        st.dataframe(distribution_df, hide_index=True, use_container_width=True)

# ============================================
# TAB 4 : DONNÉES BRUTES
# ============================================

with tab4:
    st.header("📋 Données Brutes")
    
    subtab1, subtab2, subtab3 = st.tabs(["💰 CoinGecko", "😱 Fear & Greed", "🔧 Features"])
    
    with subtab1:
        st.subheader("Dernières données CoinGecko")
        st.dataframe(df_coingecko, use_container_width=True)
        
        csv_cg = df_coingecko.to_csv(index=False)
        st.download_button(
            label="📥 Télécharger CSV",
            data=csv_cg,
            file_name=f"coingecko_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with subtab2:
        st.subheader("Historique Fear & Greed (30 derniers jours)")
        st.dataframe(df_fear_greed.tail(30), use_container_width=True)
        
        csv_fg = df_fear_greed.to_csv(index=False)
        st.download_button(
            label="📥 Télécharger CSV",
            data=csv_fg,
            file_name=f"fear_greed_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with subtab3:
        if df_features and selected_crypto in df_features:
            st.subheader(f"Features techniques - {selected_crypto}")
            st.dataframe(df_features[selected_crypto], use_container_width=True)
            
            csv_feat = df_features[selected_crypto].to_csv(index=False)
            st.download_button(
                label="📥 Télécharger CSV",
                data=csv_feat,
                file_name=f"{selected_crypto.lower()}_features_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("⚠️ Pas de features disponibles")
            st.info("Lancez `python process_features.py`")

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: gray;'>
        <p>📊 Crypto Prediction MLOps Dashboard | Dernière mise à jour: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Données: CoinGecko API + Fear & Greed Index + Features Techniques</p>
    </div>
    """,
    unsafe_allow_html=True
)