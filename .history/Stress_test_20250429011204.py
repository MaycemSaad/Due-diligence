# crypto_stress_test_ultimate_ai.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from prophet import Prophet
import os
import io

# ========== CONFIG ==========
FOLDER_PATH = "C:/Users/informasud/Desktop/Data-Preparation/LOT3"

# ========== FUNCTIONS ==========

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

def preprocess_crypto(df):
    df['Returns'] = df['CRYPTO'].pct_change()
    df['Volatility'] = df['Returns'].rolling(window=14).std()
    df = df.dropna()
    return df

def fit_prophet_with_volatility(df, steps):
    prophet_df = df.reset_index()[['Date', 'CRYPTO', 'Volatility']]
    prophet_df.columns = ['ds', 'y', 'volatility']

    model = Prophet(daily_seasonality=True, seasonality_mode='multiplicative')
    model.add_regressor('volatility')

    model.fit(prophet_df)

    future = model.make_future_dataframe(periods=steps)
    future['volatility'] = df['Volatility'].iloc[-1]  # Assume volatility stays constant for simplicity

    forecast = model.predict(future)
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].set_index('ds')

# ========== STREAMLIT APP ==========

st.set_page_config(page_title="Crypto Stress Test - Ultimate AI", layout="wide")

# Dark Mode Toggle
if "mode" not in st.session_state:
    st.session_state.mode = "Light"
mode_choice = st.toggle("🌗 Dark / Light Mode", value=(st.session_state.mode == "Dark"))
st.session_state.mode = "Dark" if mode_choice else "Light"
template = "plotly_dark" if st.session_state.mode == "Dark" else "plotly_white"

st.title("📈 Crypto Stress Test - Ultimate AI Version")
st.caption("Due Diligence AI | Volatility-Aware Precise Forecasting 🚀")
st.divider()

# Inputs
col1, col2, col3 = st.columns(3)
with col1:
    available_files = load_files(FOLDER_PATH)
    file_selected = st.selectbox("📁 Sélectionner un crypto:", available_files)

with col2:
    lookback_days = st.slider("⏳ Fenêtre historique (jours):", 30, 730, 180, step=30)

with col3:
    forecast_days = st.slider("🔮 Horizon de prédiction:", 7, 90, 30)

col4, col5, col6 = st.columns(3)
with col4:
    stress_pct = st.slider("💥 Stress Test (%) :", -80, 80, -20)

with col5:
    shock_day = st.slider("📆 Jour du stress (index):", 5, 350, 60)

with col6:
    extra_volatility = st.slider("📈 Stress Volatility Rise (%)", 0, 100, 20)

# Load and preprocess
filepath = os.path.join(FOLDER_PATH, file_selected)
df = load_crypto_data(filepath, lookback_days)

if df.empty:
    st.error("❌ Données invalides")
    st.stop()

df = preprocess_crypto(df)

# Fragility Score
st.subheader("📈 Indicateur de Fragilité")
avg_vol = df['Volatility'].mean()
fragility_score = max(0, 100 - avg_vol * 5000)
st.metric("Fragilité", f"{fragility_score:.2f} / 100")

# Stress Test Simulation
st.subheader("💥 Simulation Stress Test")

stressed_df = df.copy()
stress_date = stressed_df.index[min(shock_day, len(df)-1)]
stressed_df.loc[stress_date:, 'CRYPTO'] *= (1 + stress_pct/100)
stressed_df['Returns'] = stressed_df['CRYPTO'].pct_change()
stressed_df['Volatility'] = stressed_df['Returns'].rolling(window=14).std() * (1 + extra_volatility/100)
stressed_df = stressed_df.dropna()

# Forecast
st.subheader("🔮 Prédiction Post-Stress")

with st.spinner("Training Prophet models..."):
    forecast_original = fit_prophet_with_volatility(df, forecast_days)
    forecast_stressed = fit_prophet_with_volatility(stressed_df, forecast_days)

# Visualization
st.subheader("📊 Visualisation Résultats")

fig = go.Figure()

# Original
fig.add_trace(go.Scatter(x=df.index, y=df['CRYPTO'], name="Original", mode="lines"))

# Stressed
fig.add_trace(go.Scatter(x=stressed_df.index, y=stressed_df['CRYPTO'], name="Stressé", mode="lines"))

# Forecasts
fig.add_trace(go.Scatter(x=forecast_original.index, y=forecast_original['yhat'], name="Prévision Original", line=dict(dash='dot')))
fig.add_trace(go.Scatter(x=forecast_original.index, y=forecast_original['yhat_upper'], showlegend=False, mode='lines', line=dict(width=0)))
fig.add_trace(go.Scatter(x=forecast_original.index, y=forecast_original['yhat_lower'], showlegend=False, mode='lines', fill='tonexty', line=dict(width=0)))

fig.add_trace(go.Scatter(x=forecast_stressed.index, y=forecast_stressed['yhat'], name="Prévision Stressée", line=dict(dash='dot')))
fig.add_trace(go.Scatter(x=forecast_stressed.index, y=forecast_stressed['yhat_upper'], showlegend=False, mode='lines', line=dict(width=0)))
fig.add_trace(go.Scatter(x=forecast_stressed.index, y=forecast_stressed['yhat_lower'], showlegend=False, mode='lines', fill='tonexty', line=dict(width=0)))

fig.update_layout(
    title="Stress Test Crypto Multi-Scénarios + Forecasts",
    template=template,
    height=750,
    hovermode="x unified",
    legend=dict(orientation="h", y=-0.25)
)

st.plotly_chart(fig, use_container_width=True)

# ======= Correct Export Handling =======

st.subheader("📥 Télécharger les Résultats")
csv_buffer = io.StringIO()

# Use only the forecast part
future_forecast_index = forecast_original.index[-forecast_days:]

export_df = pd.DataFrame({
    "Forecast_Original": forecast_original['yhat'].iloc[-forecast_days:].values,
    "Forecast_Stressé": forecast_stressed['yhat'].iloc[-forecast_days:].values
}, index=future_forecast_index)

export_df.to_csv(csv_buffer)

st.download_button(
    label="💾 Télécharger CSV",
    data=csv_buffer.getvalue(),
    file_name="forecast_stress_test_ultimate.csv",
    mime="text/csv"
)


st.caption("Made with ❤️ | Due Diligence AI | Ultimate Crypto Stress Testing Platform 🚀")
