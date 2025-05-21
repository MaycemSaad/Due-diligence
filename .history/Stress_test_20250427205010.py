# 🚀 Stress Test & Crypto Forecast - Advanced Streamlit App

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from statsmodels.tsa.arima.model import ARIMA
import os

# ========== CONFIGURATION ==========
st.set_page_config(page_title="📊 Stress Test + Prédiction - Crypto", layout="wide")

# Constants
FOLDER_PATH = "C:\Users\informasud\Desktop\Data-PreparationLOT3"

# ========== HELPER FUNCTIONS ==========

@st.cache_data
def load_files(folder_path):
    """Load available CSV files."""
    return [f for f in os.listdir(folder_path) if f.endswith(".csv")]

@st.cache_data
def load_crypto_data(filepath, lookback_days):
    """Load and preprocess crypto data."""
    try:
        df = pd.read_csv(filepath)
        df.columns = [col.strip().replace('"', '') for col in df.columns]
        df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
        df = df.dropna(subset=['Date'])
        df['Price'] = df['Price'].astype(str).str.replace(',', '').astype(float)
        df = df.sort_values('Date').set_index('Date')
        df = df[['Price']].rename(columns={"Price": "CRYPTO"})
        df = df.last(f'{lookback_days}D')
        return df
    except Exception as e:
        st.error(f"❌ Erreur de chargement : {e}")
        return pd.DataFrame()

@st.cache_data
def fit_arima(series, steps):
    """Fit an ARIMA model and forecast."""
    model = ARIMA(series, order=(5, 1, 0))
    fitted = model.fit()
    forecast = fitted.forecast(steps=steps)
    return forecast

# ========== MAIN INTERFACE ==========

# Header
st.title("📊 Stress Test + Prédiction - Crypto Due Diligence")
st.markdown("Visualisez l'impact d'un choc simulé et prédisez l'évolution de vos actifs cryptographiques.")

# Sidebar
st.sidebar.title("🔧 Paramètres")

# File selection
available_files = load_files(FOLDER_PATH)
if not available_files:
    st.error("🚨 Aucun fichier CSV disponible dans le dossier spécifié.")
    st.stop()

file_selected = st.sidebar.selectbox("📁 Sélectionner une crypto :", available_files)

# Stress and forecast parameters
drop_pct = st.sidebar.slider("💥 Choc simulé (% de baisse) :", 10, 90, 30, step=5)
forecast_days = st.sidebar.slider("🔮 Jours de prédiction :", 1, 30, 7)
lookback_days = st.sidebar.slider("📅 Fenêtre temporelle :", 30, 365, 90, step=30)
st.sidebar.divider()

# Load data
filepath = os.path.join(FOLDER_PATH, file_selected)
df = load_crypto_data(filepath, lookback_days)

if df.empty:
    st.warning("Aucune donnée valide pour l'affichage.")
    st.stop()

# Dynamic shock day slider
shock_day_slider_placeholder = st.sidebar.empty()
shock_day = shock_day_slider_placeholder.slider(
    "📆 Jour du stress :", 
    10, max(10, len(df) - 10), 
    value=min(70, len(df) - 10)
)

# ========== STRESS TESTING ==========
st.subheader("📉 Simulation de Stress Test")

stressed_df = df.copy()
stress_date = df.index[min(shock_day, len(df) - 1)]
stressed_df.loc[stress_date:, 'CRYPTO'] *= (1 - drop_pct / 100)

# Resilience Score
drop = 1 - stressed_df['CRYPTO'].iloc[-1] / df['CRYPTO'].iloc[-1]
score = max(0, 100 - 100 * drop)
score_text = f"🛡️ Score de Résilience : **{round(score, 2)} / 100**"

if score > 75:
    analysis = "✅ Résilience forte face aux chocs."
elif score > 50:
    analysis = "⚠️ Résilience modérée. Couverture conseillée."
else:
    analysis = "🚨 Faible résilience. Risque élevé."

st.success(score_text)
st.info(analysis)

# ========== FORECASTING ==========
st.subheader("🔮 Prédiction ARIMA")

with st.spinner("Entraînement du modèle..."):
    forecast = fit_arima(df['CRYPTO'], forecast_days)
    forecast_index = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=forecast_days, freq='D')
    forecast_df = pd.DataFrame({"Prévision": forecast.values}, index=forecast_index)

    stressed_forecast = fit_arima(stressed_df['CRYPTO'], forecast_days)
    stressed_forecast_df = pd.DataFrame({"Prévision Stressée": stressed_forecast.values}, index=forecast_index)

# ========== VISUALIZATION ==========
st.subheader("📈 Visualisation des Résultats")

full_index = df.index.union(forecast_index)

fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df['CRYPTO'], mode='lines', name='Prix Original', line=dict(color='blue')))
fig.add_trace(go.Scatter(x=stressed_df.index, y=stressed_df['CRYPTO'], mode='lines', name='Prix Stressé', line=dict(color='orange')))
fig.add_trace(go.Scatter(x=forecast_df.index, y=forecast_df['Prévision'], mode='lines', name='Prévision', line=dict(dash='dot', color='green')))
fig.add_trace(go.Scatter(x=stressed_forecast_df.index, y=stressed_forecast_df['Prévision Stressée'], mode='lines', name='Prévision Stressée', line=dict(dash='dot', color='red')))

fig.add_shape(type='line', x0=stress_date, x1=stress_date,
              y0=stressed_df['CRYPTO'].min(), y1=stressed_df['CRYPTO'].max(),
              line=dict(color="red", dash="dash"))
fig.add_annotation(x=stress_date, y=df['CRYPTO'].max(), text="Choc Simulé", showarrow=True)

fig.update_layout(
    title="Impact du Choc & Prévision",
    xaxis_title="Date",
    yaxis_title="Prix Crypto",
    height=650,
    template="plotly_white",
    xaxis=dict(range=[full_index.min(), full_index.max()])
)

st.plotly_chart(fig, use_container_width=True)

st.caption("Powered by Due Diligence AI 🚀 | Streamlit & ARIMA modeling")

