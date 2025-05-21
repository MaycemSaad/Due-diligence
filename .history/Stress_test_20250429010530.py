# 🔥 Stress Test Ultimate AI - Pro Version

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import io
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet

# === CONFIGURATION ===
FOLDER_PATH = "C:/Users/informasud/Desktop/Data-Preparation/LOT3"

# === CACHING ===
@st.cache_data
def load_files(folder_path):
    return [f for f in os.listdir(folder_path) if f.endswith(".csv")]

@st.cache_data
def load_crypto_data(filepath, lookback_days):
    df = pd.read_csv(filepath)
    df.columns = [col.strip().replace('"', '') for col in df.columns]
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df['Price'] = df['Price'].astype(str).str.replace(',', '').astype(float)
    df = df.sort_values('Date').set_index('Date')
    df = df[['Price']].rename(columns={"Price": "CRYPTO"})
    return df.last(f'{lookback_days}D')

# === MODEL FUNCTIONS ===
def fit_arima(series, steps):
    model = ARIMA(series, order=(2,1,2))
    fitted = model.fit()
    forecast = fitted.get_forecast(steps=steps)
    return forecast.predicted_mean, forecast.conf_int()

def fit_prophet(series, steps):
    prophet_df = series.reset_index().rename(columns={"Date": "ds", "CRYPTO": "y"})
    model = Prophet(daily_seasonality=True, yearly_seasonality=True)
    model.add_seasonality(name='monthly', period=30.5, fourier_order=5)
    model.fit(prophet_df)
    future = model.make_future_dataframe(periods=steps)
    forecast = model.predict(future)
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].set_index('ds').iloc[-steps:]

# === STREAMLIT UI ===
st.set_page_config(page_title="Crypto Stress Test Ultimate AI", layout="wide")

# Mode Sombre / Clair
template = "plotly_dark" if st.toggle("🌗 Dark Mode", value=True) else "plotly_white"

st.title("📊 Crypto Stress Test - Ultimate AI Version")
st.caption("Due Diligence AI | Multi-Choc Stress Testing & AI Forecasting")
st.divider()

# === USER INPUTS ===
col1, col2, col3 = st.columns(3)
with col1:
    available_files = load_files(FOLDER_PATH)
    file_selected = st.selectbox("📂 Sélectionner une crypto:", available_files)
with col2:
    model_choice = st.radio("🧠 Choisir le modèle:", ["ARIMA", "Prophet"], horizontal=True)
with col3:
    forecast_days = st.slider("🔮 Horizon de prédiction (jours):", 7, 90, 30)

col4, col5, col6 = st.columns(3)
with col4:
    shocks = st.multiselect("💥 Chocs simulés (%):", [10,20,30,40,50,60,70,80,90], default=[30,50])
with col5:
    lookback_days = st.slider("📅 Fenêtre d'analyse (jours):", 30, 365, 180)
with col6:
    shock_day = st.slider("📆 Jour d'application du stress:", 10, 350, 70)

# === LOAD DATA ===
filepath = os.path.join(FOLDER_PATH, file_selected)
df = load_crypto_data(filepath, lookback_days)
if df.empty:
    st.error("❌ Aucun fichier valide.")
    st.stop()

# === FRAGILITY SCORE ===
st.subheader("📈 Indicateurs de Fragilité")
vol = df['CRYPTO'].rolling(window=30).std().mean()
drawdown = (df['CRYPTO'] / df['CRYPTO'].cummax() -1).min()
fragility = max(0, 100 - (vol*1000 + abs(drawdown)*100))
st.metric("Indice de Fragilité", f"{fragility:.2f} / 100")

# === STRESS TEST ===
st.subheader("💥 Simulation Stress Test")
stress_results = {}
stress_date = df.index[min(shock_day, len(df)-1)]
for shock in shocks:
    stressed = df.copy()
    stressed.loc[stress_date:, 'CRYPTO'] *= (1 - shock/100)
    stress_results[f"Stress {shock}%"] = stressed

# === FORECASTING ===
st.subheader("🔮 Prédiction Post-Stress")
forecast_results = {}
with st.spinner("⏳ Entraînement modèles..."):
    for label, stressed_df in stress_results.items():
        if model_choice == "ARIMA":
            mean_forecast, conf = fit_arima(stressed_df['CRYPTO'], forecast_days)
            forecast_results[label] = {"forecast": mean_forecast, "lower": conf.iloc[:,0], "upper": conf.iloc[:,1]}
        else:
            prophet_forecast_result = fit_prophet(stressed_df['CRYPTO'], forecast_days)
            forecast_results[label] = prophet_forecast_result

# === VISUALIZATION ===
st.subheader("📊 Visualisation Résultats")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df['CRYPTO'], name="Original", mode='lines'))

for label, stressed_df in stress_results.items():
    fig.add_trace(go.Scatter(x=stressed_df.index, y=stressed_df['CRYPTO'], name=label, mode='lines'))

future_dates = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=forecast_days)

for label, forecast in forecast_results.items():
    if model_choice == "ARIMA":
        fig.add_trace(go.Scatter(x=future_dates, y=forecast['forecast'], name=f"Forecast {label}", line=dict(dash='dot')))
        fig.add_trace(go.Scatter(x=future_dates, y=forecast['lower'], mode='lines', line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=future_dates, y=forecast['upper'], mode='lines', fill='tonexty', line=dict(width=0), showlegend=False))
    else:
        fig.add_trace(go.Scatter(x=forecast.index, y=forecast['yhat'], name=f"Forecast {label}", line=dict(dash='dot')))
        fig.add_trace(go.Scatter(x=forecast.index, y=forecast['yhat_lower'], mode='lines', line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=forecast.index, y=forecast['yhat_upper'], mode='lines', fill='tonexty', line=dict(width=0), showlegend=False))

fig.update_layout(
    template=template,
    height=750,
    hovermode="x unified",
    legend=dict(orientation="h", y=-0.25),
    title="Stress Test Crypto Multi-Chocs + Forecasts"
)

st.plotly_chart(fig, use_container_width=True)

# === EXPORT RESULTS ===
st.subheader("📥 Télécharger les Prévisions")
csv_buffer = io.StringIO()
if model_choice == "ARIMA":
    df_export = pd.concat([pd.Series(forecast['forecast'], name=label) for label, forecast in forecast_results.items()], axis=1)
else:
    df_export = pd.concat([forecast['yhat'].rename(label) for label, forecast in forecast_results.items()], axis=1)

df_export.to_csv(csv_buffer)
st.download_button("💾 Télécharger CSV", data=csv_buffer.getvalue(), file_name="forecast_results.csv", mime="text/csv")

st.caption("Made with ❤️ | Ultimate Due Diligence AI Platform")
