# stress_test_advanced.py

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

# ==================== FONCTIONS UTILES ====================

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

@st.cache_resource
def fit_arima(series, steps):
    model = ARIMA(series, order=(5, 1, 0))
    fitted = model.fit()
    forecast = fitted.get_forecast(steps=steps)
    return forecast.predicted_mean, forecast.conf_int()

@st.cache_resource
def fit_prophet(series, steps):
    prophet_df = series.reset_index().rename(columns={"Date": "ds", "CRYPTO": "y"})
    model = Prophet(daily_seasonality=True)
    model.fit(prophet_df)
    future = model.make_future_dataframe(periods=steps)
    forecast = model.predict(future)
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].set_index('ds').iloc[-steps:]

# ==================== MAIN APP ====================

st.set_page_config(page_title="Crypto Stress Test Advanced", layout="wide")

# ----- Dark/Light Mode -----
st.session_state.mode = st.session_state.get("mode", "Light")
if st.toggle("🌗 Dark / Light Mode", value=(st.session_state.mode=="Dark")):
    st.session_state.mode = "Dark"
else:
    st.session_state.mode = "Light"

if st.session_state.mode == "Dark":
    template = "plotly_dark"
else:
    template = "plotly_white"

# ----- Header -----
st.title("📊 Stress Test & Forecast - Crypto Advanced")
st.caption("Due Diligence AI | Resilient Risk Forecasting 🚀")
st.divider()

# ----- User Inputs -----
col1, col2, col3 = st.columns(3)
with col1:
    available_files = load_files(FOLDER_PATH)
    file_selected = st.selectbox("📁 Sélectionner une crypto:", available_files)

with col2:
    drop_pct_list = st.multiselect("💥 Choquer (%) :", [10, 20, 30, 40, 50, 60, 70, 80, 90], default=[30])

with col3:
    model_choice = st.radio("🧠 Modèle:", ["ARIMA", "Prophet"], horizontal=True)

col4, col5, col6 = st.columns(3)
with col4:
    forecast_days = st.slider("🔮 Jours de prédiction:", 1, 30, 7)

with col5:
    lookback_days = st.slider("📅 Fenêtre temporelle:", 30, 365, 90, step=30)

with col6:
    shock_day = st.slider("📆 Jour du stress:", 10, 350, 70)

# ----- Load Data -----
filepath = os.path.join(FOLDER_PATH, file_selected)
df = load_crypto_data(filepath, lookback_days)

if df.empty:
    st.error("❌ Pas de données valides.")
    st.stop()

if shock_day > len(df) - 10:
    shock_day = len(df) - 10

# ----- Fragility Score -----
st.subheader("📈 Analyse de Fragilité")
rolling_vol = df['CRYPTO'].rolling(window=30).std()
fragility_score = max(0, 100 - rolling_vol.mean() * 1000)
st.metric(label="Indice de Fragilité", value=f"{fragility_score:.2f}/100")

# ----- Stress Test -----
st.subheader("📉 Simulation de Stress Test")

stress_results = {}
for drop_pct in drop_pct_list:
    stressed_df = df.copy()
    stress_date = df.index[min(shock_day, len(df)-1)]
    stressed_df.loc[stress_date:, 'CRYPTO'] *= (1 - drop_pct / 100)
    stress_results[drop_pct] = stressed_df

# ----- Simulation Dynamique -----
stress_simulator = st.number_input("🚀 Ajouter un choc dynamique (%):", value=0, step=1)
if st.button("Appliquer choc dynamique"):
    stressed_dynamic = df.copy()
    stressed_dynamic.loc[df.index[shock_day]:, 'CRYPTO'] *= (1 + stress_simulator/100)
    stress_results[f"Dynamic {stress_simulator}%"] = stressed_dynamic

# ----- Forecasting -----
st.subheader("🔮 Prédiction avec Courbes de Confiance")

forecast_data = {}
with st.spinner("⏳ Entraînement modèle..."):
    if model_choice == "ARIMA":
        base_forecast, base_conf = fit_arima(df['CRYPTO'], forecast_days)
        forecast_data["Original"] = (base_forecast, base_conf)
        for label, stressed_df in stress_results.items():
            fcast, conf = fit_arima(stressed_df['CRYPTO'], forecast_days)
            forecast_data[f"Stressé {label}%"] = (fcast, conf)
    else:
        base_forecast = fit_prophet(df['CRYPTO'], forecast_days)
        forecast_data["Original"] = base_forecast
        for label, stressed_df in stress_results.items():
            fcast = fit_prophet(stressed_df['CRYPTO'], forecast_days)
            forecast_data[f"Stressé {label}%"] = fcast

# ----- Visualization -----
st.subheader("📊 Visualisation Avancée")

fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df['CRYPTO'], name="Original", mode='lines'))

for label, stressed_df in stress_results.items():
    fig.add_trace(go.Scatter(x=stressed_df.index, y=stressed_df['CRYPTO'], name=f"Stressé {label}%", mode='lines'))

for label, forecast in forecast_data.items():
    if model_choice == "ARIMA":
        mean_forecast, conf = forecast
        forecast_index = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=forecast_days, freq='D')
        fig.add_trace(go.Scatter(x=forecast_index, y=mean_forecast, name=f"Prévision {label}", mode='lines', line=dict(dash='dot')))
        fig.add_trace(go.Scatter(x=forecast_index, y=conf.iloc[:,0], mode='lines', name=f"{label} Lower", line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=forecast_index, y=conf.iloc[:,1], mode='lines', name=f"{label} Upper", fill='tonexty', line=dict(width=0), showlegend=False))
    else:
        fig.add_trace(go.Scatter(x=forecast.index, y=forecast['yhat'], name=f"Prévision {label}", mode='lines', line=dict(dash='dot')))
        fig.add_trace(go.Scatter(x=forecast.index, y=forecast['yhat_lower'], mode='lines', name=f"{label} Lower", line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=forecast.index, y=forecast['yhat_upper'], mode='lines', name=f"{label} Upper", fill='tonexty', line=dict(width=0), showlegend=False))

fig.update_layout(
    title="Stress Test & Forecast with Confidence Bands",
    template=template,
    height=750,
    hovermode="x unified",
    legend=dict(orientation="h", y=-0.3)
)

st.plotly_chart(fig, use_container_width=True)

# ----- Download Forecast -----
st.subheader("📥 Télécharger les Prévisions")
csv_buffer = io.StringIO()
pd.concat([pd.DataFrame({label: forecast[0] if model_choice=="ARIMA" else forecast['yhat']}) for label, forecast in forecast_data.items()], axis=1).to_csv(csv_buffer)

st.download_button(
    label="💾 Télécharger CSV",
    data=csv_buffer.getvalue(),
    file_name="forecast_advanced.csv",
    mime="text/csv"
)

# ----- Footer -----
st.caption("Made with ❤️ | Advanced Crypto Risk Forecasting Platform | Due Diligence AI")
