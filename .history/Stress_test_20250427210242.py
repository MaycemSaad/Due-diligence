# 🚀 Stress Test & Crypto Forecast - Advanced Streamlit App (No Sidebar Version)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
import os
import io

# ========== CONFIGURATION ==========
st.set_page_config(page_title="📊 Stress Test + Prédiction - Crypto", layout="wide")

# Constants
FOLDER_PATH = "C:/Users/informasud/Desktop/Data-Preparation/LOT3"

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

@st.cache_resource
def fit_arima(series, steps):
    """Fit an ARIMA model and forecast."""
    model = ARIMA(series, order=(5, 1, 0))
    fitted = model.fit()
    forecast = fitted.forecast(steps=steps)
    return forecast

@st.cache_resource
def fit_prophet(series, steps):
    """Fit a Prophet model and forecast."""
    prophet_df = series.reset_index().rename(columns={"Date": "ds", "CRYPTO": "y"})
    model = Prophet(daily_seasonality=True)
    model.fit(prophet_df)
    future = model.make_future_dataframe(periods=steps)
    forecast = model.predict(future)
    return forecast[['ds', 'yhat']].set_index('ds').iloc[-steps:]

# ========== MAIN INTERFACE ==========

# Header
st.title("📊 Stress Test + Prédiction - Crypto Due Diligence")
st.markdown("Visualisez l'impact d'un choc simulé et prédisez l'évolution de vos actifs cryptographiques.")
st.divider()

# ========== USER INPUTS (NO SIDEBAR) ==========

st.subheader("⚙️ Paramètres")

col1, col2, col3 = st.columns(3)

with col1:
    available_files = load_files(FOLDER_PATH)
    if not available_files:
        st.error("🚨 Aucun fichier CSV disponible dans le dossier spécifié.")
        st.stop()

    file_selected = st.selectbox("📁 Sélectionner une crypto :", available_files)

with col2:
    drop_pct_list = st.multiselect(
        "💥 Choquer (%) :", 
        [10, 20, 30, 40, 50, 60, 70, 80, 90], 
        default=[30]
    )

with col3:
    model_choice = st.radio("🧠 Modèle :", ["ARIMA", "Prophet"], horizontal=True)

col4, col5, col6 = st.columns(3)

with col4:
    forecast_days = st.slider("🔮 Jours de prédiction :", 1, 30, 7)

with col5:
    lookback_days = st.slider("📅 Fenêtre temporelle :", 30, 365, 90, step=30)

with col6:
    shock_day = st.slider("📆 Jour du stress :", 10, 350, 70)

st.divider()

# Load data
filepath = os.path.join(FOLDER_PATH, file_selected)
df = load_crypto_data(filepath, lookback_days)

if df.empty:
    st.warning("Aucune donnée valide pour l'affichage.")
    st.stop()

if shock_day > len(df) - 10:
    shock_day = len(df) - 10  # Safety limit

# ========== STRESS TESTING ==========
st.subheader("📉 Simulation de Stress Test")

stress_results = {}

for drop_pct in drop_pct_list:
    stressed_df = df.copy()
    stress_date = df.index[min(shock_day, len(df) - 1)]
    stressed_df.loc[stress_date:, 'CRYPTO'] *= (1 - drop_pct / 100)

    # Resilience Score
    drop = 1 - stressed_df['CRYPTO'].iloc[-1] / df['CRYPTO'].iloc[-1]
    score = max(0, 100 - 100 * drop)

    stress_results[drop_pct] = {
        "stressed_df": stressed_df,
        "score": score,
        "stress_date": stress_date
    }

# Display Resilience Metrics
col1, col2, col3 = st.columns(3)
for drop_pct, result in stress_results.items():
    with col1 if drop_pct <= 40 else col2 if drop_pct <= 70 else col3:
        st.metric(label=f"Choc -{drop_pct}%", value=f"{round(result['score'],2)} /100")

# ========== FORECASTING ==========
st.subheader("🔮 Prédiction")

forecast_data = {}

with st.spinner("Entraînement du modèle..."):
    if model_choice == "ARIMA":
        forecast = fit_arima(df['CRYPTO'], forecast_days)
        forecast_index = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=forecast_days, freq='D')
        forecast_data["Original"] = pd.Series(forecast.values, index=forecast_index)
        for drop_pct, result in stress_results.items():
            fcast = fit_arima(result['stressed_df']['CRYPTO'], forecast_days)
            forecast_data[f"Stressé {drop_pct}%"] = pd.Series(fcast.values, index=forecast_index)
    else:
        forecast = fit_prophet(df['CRYPTO'], forecast_days)
        forecast_data["Original"] = forecast['yhat']
        for drop_pct, result in stress_results.items():
            fcast = fit_prophet(result['stressed_df']['CRYPTO'], forecast_days)
            forecast_data[f"Stressé {drop_pct}%"] = fcast['yhat']

# ========== VISUALIZATION ==========
st.subheader("📈 Visualisation Avancée")

fig = go.Figure()

fig.add_trace(go.Scatter(x=df.index, y=df['CRYPTO'], mode='lines', name='Prix Original'))

for drop_pct, result in stress_results.items():
    fig.add_trace(go.Scatter(
        x=result['stressed_df'].index, 
        y=result['stressed_df']['CRYPTO'], 
        mode='lines', 
        name=f'Prix Stressé {drop_pct}%'
    ))

for label, series in forecast_data.items():
    fig.add_trace(go.Scatter(
        x=series.index,
        y=series.values,
        mode='lines',
        name=f"Prévision {label}",
        line=dict(dash='dot')
    ))

fig.update_layout(
    title="Stress Test Multi-Scénarios + Prédiction",
    xaxis_title="Date",
    yaxis_title="Prix Crypto",
    height=700,
    template="plotly_white",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# ========== DOWNLOAD FORECAST ==========
st.subheader("📥 Télécharger les Prévisions")

csv_buffer = io.StringIO()
pd.DataFrame(forecast_data).to_csv(csv_buffer)
st.download_button(
    label="💾 Télécharger les données CSV",
    data=csv_buffer.getvalue(),
    file_name="forecast_stress_test.csv",
    mime="text/csv"
)

# ========== FOOTER ==========
st.caption("Powered by Due Diligence AI 🚀 | ARIMA / Prophet | Advanced Forecasting App")
