# stress_test_safe.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
import os
import io

# ==================== CONFIGURATION ====================
FOLDER_PATH = "C:/Users/informasud/Desktop/Data-Preparation/LOT3"

# ==================== UTILITY FUNCTIONS ====================
@st.cache_data
def load_files(folder_path):
    return [f for f in os.listdir(folder_path) if f.endswith(".csv")]

@st.cache_data
def load_crypto_data(filepath, lookback_days):
    df = pd.read_csv(filepath)
    df.columns = [col.strip().replace('"', '') for col in df.columns]
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
    df = df.dropna(subset=['Date'])
    df['Price'] = df['Price'].astype(str).str.replace(',', '').astype(float)
    df = df.sort_values('Date').set_index('Date')
    df = df[['Price']].rename(columns={"Price": "CRYPTO"})
    df = df.last(f'{lookback_days}D')
    return df

def fit_arima(series, steps):
    model = ARIMA(series, order=(2,1,2))  # simple stable ARIMA
    fitted = model.fit()
    forecast = fitted.get_forecast(steps=steps)
    return forecast.predicted_mean, forecast.conf_int()

def fit_prophet(series, steps):
    prophet_df = series.reset_index().rename(columns={"Date": "ds", "CRYPTO": "y"})
    model = Prophet(daily_seasonality=True)
    model.fit(prophet_df)
    future = model.make_future_dataframe(periods=steps)
    forecast = model.predict(future)
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].set_index('ds').iloc[-steps:]

# ==================== MAIN ====================
st.set_page_config(page_title="Crypto Stress Test PRO", layout="wide")

# Light/Dark Mode
if "mode" not in st.session_state:
    st.session_state.mode = "Light"
mode_choice = st.toggle("🌗 Dark / Light Mode", value=(st.session_state.mode == "Dark"))
st.session_state.mode = "Dark" if mode_choice else "Light"
template = "plotly_dark" if st.session_state.mode == "Dark" else "plotly_white"

st.title("📊 Crypto Stress Test - Safe Professional Version")
st.caption("Built for resilience and production stability 🚀")
st.divider()

# Inputs
col1, col2, col3 = st.columns(3)
with col1:
    available_files = load_files(FOLDER_PATH)
    file_selected = st.selectbox("📁 Sélectionner une crypto :", available_files)

with col2:
    model_choice = st.radio("🔮 Modèle :", ["ARIMA", "Prophet"], horizontal=True)

with col3:
    lookback_days = st.slider("🕰️ Fenêtre temporelle (jours) :", 30, 365, 180, step=30)

col4, col5, col6 = st.columns(3)
with col4:
    forecast_days = st.slider("⏳ Horizon de prédiction (jours) :", 7, 90, 30)

with col5:
    shock_pct = st.slider("💥 Choc Simulé (%) :", -90, 90, -30)

with col6:
    shock_day = st.slider("📆 Jour du stress (index) :", 10, 350, 70)

# Load Data
filepath = os.path.join(FOLDER_PATH, file_selected)
df = load_crypto_data(filepath, lookback_days)

if df.empty:
    st.error("❌ Aucun fichier ou données valides.")
    st.stop()

# Stress Test
st.subheader("📉 Stress Simulation")
stress_df = df.copy()
stress_date = stress_df.index[min(shock_day, len(df)-1)]
stress_df.loc[stress_date:, 'CRYPTO'] *= (1 + shock_pct / 100)

# Fragility Index
st.subheader("📈 Indice de Fragilité")
rolling_vol = df['CRYPTO'].rolling(window=30).std().mean()
fragility_score = max(0, 100 - rolling_vol * 1000)
st.metric("Indice de Fragilité", f"{fragility_score:.2f} / 100")

# Forecasting
st.subheader("🔮 Prédiction")

with st.spinner("Training model..."):
    if model_choice == "ARIMA":
        forecast_original, conf_original = fit_arima(df['CRYPTO'], forecast_days)
        forecast_stressed, conf_stressed = fit_arima(stress_df['CRYPTO'], forecast_days)
    else:
        forecast_original = fit_prophet(df['CRYPTO'], forecast_days)
        forecast_stressed = fit_prophet(stress_df['CRYPTO'], forecast_days)

# Visualization
st.subheader("📊 Résultats")

fig = go.Figure()

# Historical
fig.add_trace(go.Scatter(x=df.index, y=df['CRYPTO'], name="Original", mode='lines'))
fig.add_trace(go.Scatter(x=stress_df.index, y=stress_df['CRYPTO'], name="Stressé", mode='lines'))

# Forecast
future_index = pd.date_range(start=df.index[-1]+pd.Timedelta(days=1), periods=forecast_days, freq="D")

if model_choice == "ARIMA":
    fig.add_trace(go.Scatter(x=future_index, y=forecast_original, name="Forecast Original", line=dict(dash='dot')))
    fig.add_trace(go.Scatter(x=future_index, y=forecast_stressed, name="Forecast Stressé", line=dict(dash='dot')))
else:
    fig.add_trace(go.Scatter(x=forecast_original.index, y=forecast_original['yhat'], name="Forecast Original", line=dict(dash='dot')))
    fig.add_trace(go.Scatter(x=forecast_stressed.index, y=forecast_stressed['yhat'], name="Forecast Stressé", line=dict(dash='dot')))

fig.update_layout(
    template=template,
    hovermode="x unified",
    height=750,
    legend=dict(orientation="h", y=-0.2),
    title="Stress Test + Forecast (Safe Version)"
)

st.plotly_chart(fig, use_container_width=True)

# Download
st.subheader("📥 Télécharger les prévisions")
csv_buffer = io.StringIO()

if model_choice == "ARIMA":
    export_df = pd.DataFrame({
        "Forecast_Original": forecast_original.values,
        "Forecast_Stressé": forecast_stressed.values
    }, index=future_index)
else:
    export_df = pd.DataFrame({
        "Forecast_Original": forecast_original['yhat'].values,
        "Forecast_Stressé": forecast_stressed['yhat'].values
    }, index=forecast_original.index)

export_df.to_csv(csv_buffer)
st.download_button(
    label="💾 Télécharger CSV",
    data=csv_buffer.getvalue(),
    file_name="forecast_safe.csv",
    mime="text/csv"
)

st.caption("Made with ❤️ | No pmdarima | No XGBoost | 100% Stable Platform")
