# app/dashboard.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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

@st.cache_data(ttl=60)  # Cache pendant 60 secondes
def load_latest_data():
    """Charge les dernières données collectées"""
    
    # Trouver les fichiers les plus récents
    coingecko_files = glob.glob('data/raw/coingecko_*.csv')
    fear_greed_files = glob.glob('data/raw/fear_greed_*.csv')
    
    if not coingecko_files or not fear_greed_files:
        return None, None
    
    latest_coingecko = max(coingecko_files, key=os.path.getctime)
    latest_fear_greed = max(fear_greed_files, key=os.path.getctime)
    
    df_cg = pd.read_csv(latest_coingecko)
    df_fg = pd.read_csv(latest_fear_greed)
    
    # Convertir timestamps
    df_cg['timestamp'] = pd.to_datetime(df_cg['timestamp'])
    df_fg['timestamp'] = pd.to_datetime(df_fg['timestamp'])
    
    return df_cg, df_fg

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

# ============================================
# CHARGEMENT DES DONNÉES
# ============================================

df_coingecko, df_fear_greed = load_latest_data()

if df_coingecko is None or df_fear_greed is None:
    st.error("❌ Aucune donnée trouvée. Lancez d'abord : `python collect_data.py`")
    st.stop()

# ============================================
# SIDEBAR - INFORMATIONS
# ============================================

st.sidebar.header("ℹ️ Informations")

# Dernière mise à jour
last_update = df_coingecko['timestamp'].max()
st.sidebar.metric("📅 Dernière mise à jour", last_update.strftime('%Y-%m-%d %H:%M'))

# Nombre de cryptos
nb_cryptos = len(df_coingecko)
st.sidebar.metric("💰 Cryptos suivies", nb_cryptos)

# Historique Fear & Greed
nb_days = len(df_fear_greed)
st.sidebar.metric("📊 Historique F&G", f"{nb_days} jours")

st.sidebar.markdown("---")

# Sélection crypto
st.sidebar.header("🎯 Sélection")
selected_crypto = st.sidebar.selectbox(
    "Choisir une crypto:",
    options=df_coingecko['symbol'].unique(),
    index=0
)

# Filtrer sur la crypto sélectionnée
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
    # Fear & Greed actuel
    current_fg = df_fear_greed.iloc[-1]
    emoji = get_emoji_for_fear_greed(current_fg['value'])
    st.metric(
        f"{emoji} Fear & Greed",
        f"{current_fg['value']}/100",
        delta=current_fg['classification']
    )

st.markdown("---")

# ============================================
# SECTION 2 : PRIX DES CRYPTOS (Bar Chart)
# ============================================

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
# SECTION 3 : FEAR & GREED HISTORIQUE
# ============================================

st.header("😱 Fear & Greed Index - Historique")

# Ajouter une colonne de couleur basée sur la valeur
def get_color(value):
    if value <= 25:
        return 'darkred'
    elif value <= 45:
        return 'orange'
    elif value <= 55:
        return 'gray'
    elif value <= 75:
        return 'lightgreen'
    else:
        return 'darkgreen'

df_fear_greed['color'] = df_fear_greed['value'].apply(get_color)

# Graphique Fear & Greed
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

# Ajouter des zones de référence
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

# ============================================
# SECTION 4 : STATISTIQUES FEAR & GREED
# ============================================

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
    
    # Distribution par zone
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
# SECTION 5 : DONNÉES BRUTES
# ============================================

st.markdown("---")
st.header("📋 Données Brutes")

tab1, tab2 = st.tabs(["💰 CoinGecko", "😱 Fear & Greed"])

with tab1:
    st.subheader("Dernières données CoinGecko")
    st.dataframe(df_coingecko, use_container_width=True)
    
    # Bouton download
    csv_cg = df_coingecko.to_csv(index=False)
    st.download_button(
        label="📥 Télécharger CSV",
        data=csv_cg,
        file_name=f"coingecko_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

with tab2:
    st.subheader("Historique Fear & Greed (30 derniers jours)")
    st.dataframe(df_fear_greed.tail(30), use_container_width=True)
    
    # Bouton download
    csv_fg = df_fear_greed.to_csv(index=False)
    st.download_button(
        label="📥 Télécharger CSV",
        data=csv_fg,
        file_name=f"fear_greed_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <p>📊 Crypto Prediction MLOps Dashboard | Dernière mise à jour: {}</p>
        <p>Données: CoinGecko API + Fear & Greed Index</p>
    </div>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
    unsafe_allow_html=True
)