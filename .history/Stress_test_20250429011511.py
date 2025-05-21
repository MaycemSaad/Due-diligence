# stress_test_pro_ultimate.py

# ==================== 📚 Imports ====================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
import os
import io

# ==================== ⚙️ Configuration ====================
FOLDER_PATH = "C:/Users/informasud/Desktop/Data-Preparation/LOT3"

st.set_page_config(page_title="Crypto Stress Test - Ultimate Version", layout="wide")

# ==================== 🔥 Utility Functions ====================
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
    model = ARIMA(series, order=(2, 1, 2))
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

# ==================== 🌗 Theme Control ====================
if "mode" not in st.session_state:
    st.session_state.mode = "Light"
mode_choice = st.toggle("🌗 Dark / Light Mode", value=(st.session_state.mode == "Dark"))
st.session_state.mode = "Dark" if mode_choice else "Light"
template = "plotly_dark" if st.session_state.mode == "Dark" else "plotly_white"

# ==================== 🏠 Title ====================
st.title("📊 Crypto Stress Test - Ultimate AI Version")
st.caption("Due Diligence AI | Ultimate Stress Testing & Forecasting")
st.divider()

# ==================== 🎯 User Inputs ====================
col1, col2, col3 = st.columns(3)
with col1:
    available_files = load_files(FOLDER_PATH)
    file_selected = st.selectbox("📁 Sélectionner une crypto :", available_files)

with col2:
    model_choice = st.radio("🔮 Modèle de Prédiction :", ["ARIMA", "Prophet"], horizontal=True)

with col3:
    lookback_days = st.slider("🕰️ Fenêtre historique :", 30, 365, 180, step=30)

col4, col5, col6 = st.columns(3)
with col4:
    forecast_days = st.slider("🔮 Horizon de prévision :", 7, 90, 30)

with col5:
    shock_pct = st.slider("💥 Choc Simulé (%) :", -90, 90, -30)

with col6:
    shock_day = st.slider("📆 Jour d'application du choc :", 10, 350, 70)

# ==================== 📥 Load Data ====================
filepath = os.path.join(FOLDER_PATH, file_selected)
df = load_crypto_data(filepath, lookback_days)

if df.empty:
    st.error("❌ Aucun fichier ou données valides.")
    st.stop()

# ==================== 📉 Stress Test ====================
st.subheader("💥 Simulation Stress Test")

stress_df = df.copy()
stress_date = stress_df.index[min(shock_day, len(df)-1)]
stress_df.loc[stress_date:, 'CRYPTO'] *= (1 + shock_pct / 100)

# ==================== 📈 Fragility Index ====================
st.subheader("📈 Indicateurs de Fragilité")
rolling_vol = df['CRYPTO'].rolling(window=30).std().mean()
fragility_score = max(0, 100 - rolling_vol * 1000)
st.metric("Indice de Fragilité", f"{fragility_score:.2f} / 100")

# ==================== 🔮 Forecasting ====================
st.subheader("🔮 Prédiction Post-Stress")

with st.spinner("Training predictive model..."):
    if model_choice == "ARIMA":
        forecast_original, conf_original = fit_arima(df['CRYPTO'], forecast_days)
        forecast_stressed, conf_stressed = fit_arima(stress_df['CRYPTO'], forecast_days)
    else:
        forecast_original = fit_prophet(df['CRYPTO'], forecast_days)
        forecast_stressed = fit_prophet(stress_df['CRYPTO'], forecast_days)

# ==================== 📊 Visualization ====================
st.subheader("📊 Visualisation Résultats")

fig = go.Figure()

# --- Original and Stress Lines
fig.add_trace(go.Scatter(
    x=df.index, y=df['CRYPTO'], name="Original", mode='lines', line=dict(color="lime", width=3)
))
fig.add_trace(go.Scatter(
    x=stress_df.index, y=stress_df['CRYPTO'], name="Stressé", mode='lines', line=dict(color="red", width=3, dash='dash')
))

# --- Forecast
future_index = pd.date_range(start=df.index[-1]+pd.Timedelta(days=1), periods=forecast_days, freq="D")

if model_choice == "ARIMA":
    fig.add_trace(go.Scatter(
        x=future_index, y=forecast_original, name="Prévision Originale",
        mode='lines', line=dict(color="lime", dash='dot', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=future_index, y=forecast_stressed, name="Prévision Stressée",
        mode='lines', line=dict(color="red", dash='dot', width=2)
    ))
else:
    fig.add_trace(go.Scatter(
        x=forecast_original.index, y=forecast_original['yhat'], name="Prévision Originale",
        mode='lines', line=dict(color="lime", dash='dot', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=forecast_stressed.index, y=forecast_stressed['yhat'], name="Prévision Stressée",
        mode='lines', line=dict(color="red", dash='dot', width=2)
    ))

# --- Confidence Intervals
if model_choice == "Prophet":
    # Original Confidence
    fig.add_trace(go.Scatter(
        x=forecast_original.index, y=forecast_original['yhat_upper'],
        mode='lines', line=dict(width=0), showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=forecast_original.index, y=forecast_original['yhat_lower'],
        mode='lines', fill='tonexty', fillcolor='rgba(0,255,0,0.2)', line=dict(width=0), showlegend=False
    ))

    # Stressé Confidence
    fig.add_trace(go.Scatter(
        x=forecast_stressed.index, y=forecast_stressed['yhat_upper'],
        mode='lines', line=dict(width=0), showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=forecast_stressed.index, y=forecast_stressed['yhat_lower'],
        mode='lines', fill='tonexty', fillcolor='rgba(255,0,0,0.2)', line=dict(width=0), showlegend=False
    ))

fig.update_layout(
    template=template,
    hovermode="x unified",
    height=750,
    xaxis_title="Date",
    yaxis_title="Prix",
    title="Stress Test Crypto Multi-Scénarios + Forecast",
    legend=dict(orientation="h", y=-0.25, font=dict(size=14))
)

st.plotly_chart(fig, use_container_width=True)

# ==================== 📥 Download Forecast ====================
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
    file_name="forecast_results.csv",
    mime="text/csv"
)

# ==================== 📢 Footer ====================
st.caption("Made with ❤️ | Ultimate AI Stress Test Forecasting Platform")

