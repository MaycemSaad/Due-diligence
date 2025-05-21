import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from statsmodels.tsa.arima.model import ARIMA
import os

# === 1. Config ===
st.set_page_config(page_title="📊 Stress Test + Prédiction - Crypto", layout="wide")

FOLDER_PATH = "C:/Users/omarb/OneDrive/Bureau/PI/DATA/LOT3"
available_files = [f for f in os.listdir(FOLDER_PATH) if f.endswith(".csv")]

st.title("📊 Stress Test + Prédiction - Crypto Due Diligence")

# === 2. Sidebar selection ===
st.sidebar.header("Paramètres")

file_selected = st.sidebar.selectbox(
    "📁 Sélectionner une crypto (CSV) :", 
    available_files
)

drop_pct = st.sidebar.slider(
    "💥 Choc simulé (% de baisse) :", 
    min_value=10, 
    max_value=90, 
    step=5, 
    value=30
)

# Placeholder, we will update it after loading the file
shock_day_slider_placeholder = st.sidebar.empty()

forecast_days = st.sidebar.slider(
    "🔮 Prédire les prochains jours :", 
    min_value=1, 
    max_value=30, 
    step=1, 
    value=7
)

lookback_days = st.sidebar.slider(
    "📅 Afficher les X derniers jours :", 
    min_value=30, 
    max_value=365, 
    step=30, 
    value=90
)

st.sidebar.markdown("---")

# === 3. Load and preprocess data ===
filepath = os.path.join(FOLDER_PATH, file_selected)
df = pd.read_csv(filepath)
df.columns = [col.strip().replace('"', '') for col in df.columns]
df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
df = df.dropna(subset=['Date'])
df['Price'] = df['Price'].astype(str).str.replace(',', '').astype(float)
df = df.sort_values('Date')
df.set_index('Date', inplace=True)
df = df[['Price']].rename(columns={"Price": "CRYPTO"})

# Apply lookback
df = df.last(f'{lookback_days}D')

# Now we can update shock day max dynamically
shock_day = shock_day_slider_placeholder.slider(
    "📆 Jour du stress (index temporel) :", 
    min_value=10, 
    max_value=max(10, len(df)-10), 
    step=1, 
    value=min(70, len(df)-10)
)

# === 4. Stress Testing ===
stressed_df = df.copy()
if shock_day < len(df):
    stress_date = df.index[shock_day]
    stressed_df.loc[stress_date:, 'CRYPTO'] *= (1 - drop_pct / 100)
else:
    stress_date = df.index[-1]

drop = 1 - stressed_df['CRYPTO'].iloc[-1] / df['CRYPTO'].iloc[-1]
score = max(0, 100 - 100 * drop)
score_text = f"🛡️ Score de Résilience : {round(score, 2)} / 100"

if score > 75:
    analysis = "✅ Résilience forte face aux chocs."
elif score > 50:
    analysis = "⚠️ Résilience modérée. Couverture conseillée."
else:
    analysis = "🚨 Faible résilience. Risque élevé."

# === 5. Forecasting with ARIMA ===
model = ARIMA(df['CRYPTO'], order=(5, 1, 0))
fitted = model.fit()
forecast = fitted.forecast(steps=forecast_days)
forecast_index = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=forecast_days, freq='D')
forecast_df = pd.DataFrame({"Prévision": forecast.values}, index=forecast_index)

stressed_model = ARIMA(stressed_df['CRYPTO'], order=(5, 1, 0))
stressed_fit = stressed_model.fit()
stressed_forecast = stressed_fit.forecast(steps=forecast_days)
stressed_forecast_df = pd.DataFrame({"Prévision Stressée": stressed_forecast.values}, index=forecast_index)

# === 6. Graph ===
full_index = df.index.union(forecast_index)

fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df['CRYPTO'], mode='lines', name='Original'))
fig.add_trace(go.Scatter(x=stressed_df.index, y=stressed_df['CRYPTO'], mode='lines', name='Stressé'))
fig.add_trace(go.Scatter(x=forecast_df.index, y=forecast_df['Prévision'], mode='lines', name='Prévision', line=dict(dash='dot')))
fig.add_trace(go.Scatter(x=stressed_forecast_df.index, y=stressed_forecast_df['Prévision Stressée'], mode='lines', name='Prévision Stressée', line=dict(dash='dot', color='red')))
fig.add_shape(type='line', x0=stress_date, x1=stress_date,
              y0=stressed_df['CRYPTO'].min(), y1=stressed_df['CRYPTO'].max(),
              line=dict(color="red", dash="dash"))
fig.add_annotation(x=stress_date, y=df['CRYPTO'].max(), text="Choc", showarrow=True)
fig.update_layout(title="Impact + Prévision", xaxis_title="Date", yaxis_title="Prix", height=600,
                  xaxis=dict(range=[full_index.min(), full_index.max()]))

# === 7. Display Results ===
st.plotly_chart(fig, use_container_width=True)

st.markdown(f"### {score_text}")
st.markdown(f"### {analysis}")
