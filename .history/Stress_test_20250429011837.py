# 🚀 Ultimate Crypto Stress Test - Professional Version

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
import os
import io

# ==================== CONFIG ====================
st.set_page_config(page_title="Crypto Stress Test Pro", layout="wide")

# --- Light / Dark mode ---
if "mode" not in st.session_state:
    st.session_state.mode = "Light"
mode_choice = st.toggle("🌗 Dark / Light Mode", value=(st.session_state.mode == "Dark"))
st.session_state.mode = "Dark" if mode_choice else "Light"
template = "plotly_dark" if st.session_state.mode == "Dark" else "plotly_white"

# --- Folder path ---
FOLDER_PATH = "C:/Users/informasud/Desktop/Data-Preparation/LOT3"

# ==================== FUNCTIONS ====================
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
    model = ARIMA(series, order=(2,1,2))
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

# ==================== INTERFACE ====================
st.title("📈 Crypto Stress Test - Ultimate AI Version")
st.caption("Due Diligence AI | Ultimate Stress Testing and Forecasting")
st.divider()

# --- Inputs ---
col1, col2, col3 = st.columns(3)
with col1:
    available_files = load_files(FOLDER_PATH)
    file_selected = st.selectbox("📁 Choisir une crypto:", available_files)
with col2:
    model_choice = st.radio("🧠 Modèle:", ["ARIMA", "Prophet"], horizontal=True)
with col3:
    lookback_days = st.slider("📅 Fenêtre temporelle:", 30, 365, 180, step=30)

col4, col5, col6 = st.columns(3)
with col4:
    forecast_days = st.slider("🔮 Jours de prédiction:", 7, 90, 30)
with col5:
    shock_pct = st.slider("💥 Choc Simulé (%):", -90, 90, -30)
with col6:
    shock_day = st.slider("📆 Jour du stress:", 10, 350, 70)

# --- Load Data ---
filepath = os.path.join(FOLDER_PATH, file_selected)
df = load_crypto_data(filepath, lookback_days)
if df.empty:
    st.error("❌ Aucun fichier ou données valides.")
    st.stop()

# --- Stress Test ---
st.subheader("💥 Simulation de Stress")
stress_df = df.copy()
stress_date = stress_df.index[min(shock_day, len(df)-1)]
stress_df.loc[stress_date:, 'CRYPTO'] *= (1 + shock_pct / 100)

# --- Fragility Index ---
st.subheader("📊 Indicateur de Fragilité")
rolling_vol = df['CRYPTO'].rolling(window=30).std().mean()
fragility_score = max(0, 100 - rolling_vol * 1000)
st.metric("Indice de Fragilité", f"{fragility_score:.2f} / 100")

# --- Forecasting ---
st.subheader("🔮 Prédiction Post-Stress")
with st.spinner("Training model..."):
    if model_choice == "ARIMA":
        forecast_original, conf_original = fit_arima(df['CRYPTO'], forecast_days)
        forecast_stressed, conf_stressed = fit_arima(stress_df['CRYPTO'], forecast_days)
    else:
        forecast_original = fit_prophet(df['CRYPTO'], forecast_days)
        forecast_stressed = fit_prophet(stress_df['CRYPTO'], forecast_days)

# --- Visualization ---
st.subheader("📈 Visualisation Résultats")
fig = go.Figure()

# Original and Stressed curves
fig.add_trace(go.Scatter(x=df.index, y=df['CRYPTO'], name="Prix Original", line=dict(color="#00BFFF")))
fig.add_trace(go.Scatter(x=stress_df.index, y=stress_df['CRYPTO'], name="Prix Stressé", line=dict(color="#FF4500")))

# Forecasts
future_index = pd.date_range(start=df.index[-1]+pd.Timedelta(days=1), periods=forecast_days, freq="D")
if model_choice == "ARIMA":
    fig.add_trace(go.Scatter(x=future_index, y=forecast_original, name="Prévision Original", line=dict(color="#90EE90", dash='dot')))
    fig.add_trace(go.Scatter(x=future_index, y=conf_original.iloc[:,0], mode="lines", line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=future_index, y=conf_original.iloc[:,1], fill='tonexty', fillcolor='rgba(144,238,144,0.2)', line=dict(width=0), showlegend=False))

    fig.add_trace(go.Scatter(x=future_index, y=forecast_stressed, name="Prévision Stressé", line=dict(color="#FFA07A", dash='dot')))
    fig.add_trace(go.Scatter(x=future_index, y=conf_stressed.iloc[:,0], mode="lines", line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=future_index, y=conf_stressed.iloc[:,1], fill='tonexty', fillcolor='rgba(255,160,122,0.2)', line=dict(width=0), showlegend=False))
else:
    fig.add_trace(go.Scatter(x=forecast_original.index, y=forecast_original['yhat'], name="Prévision Original", line=dict(color="#90EE90", dash='dot')))
    fig.add_trace(go.Scatter(x=forecast_original.index, y=forecast_original['yhat_lower'], mode="lines", line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=forecast_original.index, y=forecast_original['yhat_upper'], fill='tonexty', fillcolor='rgba(144,238,144,0.2)', line=dict(width=0), showlegend=False))

    fig.add_trace(go.Scatter(x=forecast_stressed.index, y=forecast_stressed['yhat'], name="Prévision Stressé", line=dict(color="#FFA07A", dash='dot')))
    fig.add_trace(go.Scatter(x=forecast_stressed.index, y=forecast_stressed['yhat_lower'], mode="lines", line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=forecast_stressed.index, y=forecast_stressed['yhat_upper'], fill='tonexty', fillcolor='rgba(255,160,122,0.2)', line=dict(width=0), showlegend=False))

fig.update_layout(
    template=template,
    height=750,
    hovermode="x unified",
    legend=dict(orientation="h", y=-0.2),
    title="Stress Test Crypto Multi-Chocs + Forecast"
)

st.plotly_chart(fig, use_container_width=True)

# --- Exportation ---
st.subheader("📥 Télécharger Résultats")
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
    file_name="forecast_crypto_stress.csv",
    mime="text/csv"
)

st.caption("Made with ❤️ | Due Diligence AI | Professional Forecasting")