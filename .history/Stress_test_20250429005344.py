# stress_test_ultimate.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import io
from prophet import Prophet
from pmdarima import auto_arima
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split

# ==================== CONFIGURATION ====================
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

def auto_arima_forecast(series, steps):
    model = auto_arima(series, seasonal=False, trace=False, error_action='ignore', suppress_warnings=True)
    forecast = model.predict(n_periods=steps, return_conf_int=True)
    return forecast

def prophet_forecast(series, steps):
    prophet_df = series.reset_index().rename(columns={"Date": "ds", "CRYPTO": "y"})
    model = Prophet(daily_seasonality=True)
    model.add_seasonality(name='monthly', period=30.5, fourier_order=5)
    model.fit(prophet_df)
    future = model.make_future_dataframe(periods=steps)
    forecast = model.predict(future)
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].set_index('ds').iloc[-steps:]

def xgboost_forecast(series, steps):
    X = np.arange(len(series)).reshape(-1,1)
    y = series.values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    model = XGBRegressor(n_estimators=100, objective='reg:squarederror')
    model.fit(X_train, y_train)
    future_X = np.arange(len(series), len(series)+steps).reshape(-1,1)
    preds = model.predict(future_X)
    return preds

# ==================== MAIN APP ====================

st.set_page_config(page_title="Crypto Stress Test Ultimate", layout="wide")

# Dark / Light mode
if "mode" not in st.session_state:
    st.session_state.mode = "Light"
mode_choice = st.toggle("🌗 Dark / Light Mode", value=(st.session_state.mode=="Dark"))
st.session_state.mode = "Dark" if mode_choice else "Light"
template = "plotly_dark" if st.session_state.mode == "Dark" else "plotly_white"

# Title
st.title("📊 Crypto Stress Test Ultimate AI")
st.caption("🔬 Due Diligence AI | Machine Learning Driven Forecasting")
st.divider()

# Inputs
col1, col2, col3 = st.columns(3)
with col1:
    available_files = load_files(FOLDER_PATH)
    file_selected = st.selectbox("📁 Sélectionner une crypto:", available_files)

with col2:
    drop_pct_list = st.multiselect("💥 Chocs simulés (%) :", [10, 20, 30, 40, 50, 60, 70, 80, 90], default=[30])

with col3:
    model_choice = st.selectbox("🧠 Modèle prédictif:", ["Auto ARIMA", "Prophet", "XGBoost"])

col4, col5, col6 = st.columns(3)
with col4:
    forecast_days = st.slider("🔮 Jours de prédiction:", 1, 90, 14)

with col5:
    lookback_days = st.slider("📅 Fenêtre temporelle:", 30, 365, 180, step=30)

with col6:
    shock_day = st.slider("📆 Jour du stress:", 10, 350, 70)

# Load data
filepath = os.path.join(FOLDER_PATH, file_selected)
df = load_crypto_data(filepath, lookback_days)

if df.empty:
    st.error("❌ Pas de données valides pour cette sélection.")
    st.stop()

# Fragility Score
st.subheader("📈 Indice de Fragilité")
vol = df['CRYPTO'].rolling(window=30).std().mean()
fragility_score = max(0, 100 - vol * 1000)
st.metric("Indice de Fragilité", f"{fragility_score:.2f} / 100")

# Stress Simulation
st.subheader("💥 Stress Test Dynamique")
stress_results = {}
for drop_pct in drop_pct_list:
    stressed_df = df.copy()
    stress_date = df.index[min(shock_day, len(df)-1)]
    stressed_df.loc[stress_date:, 'CRYPTO'] *= (1 - drop_pct/100)
    stress_results[drop_pct] = stressed_df

dynamic_shock = st.number_input("🚀 Ajouter un choc manuel (%) :", value=0, step=1)
if st.button("Appliquer choc dynamique"):
    stressed_dynamic = df.copy()
    stressed_dynamic.loc[df.index[shock_day]:, 'CRYPTO'] *= (1 + dynamic_shock/100)
    stress_results[f"Dynamic {dynamic_shock}%"] = stressed_dynamic

# Forecast
st.subheader("🔮 Prédiction Multi-Modèles")

forecast_data = {}
for label, stressed_df in stress_results.items():
    if model_choice == "Auto ARIMA":
        fcast, conf = auto_arima_forecast(stressed_df['CRYPTO'], forecast_days)
        forecast_data[label] = {"forecast": fcast[0], "lower": fcast[1][:,0], "upper": fcast[1][:,1]}
    elif model_choice == "Prophet":
        forecast = prophet_forecast(stressed_df['CRYPTO'], forecast_days)
        forecast_data[label] = forecast
    else:
        preds = xgboost_forecast(stressed_df['CRYPTO'], forecast_days)
        forecast_data[label] = preds

# Visualization
st.subheader("📊 Visualisation des scénarios")

fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df['CRYPTO'], name="Original", mode="lines"))

for label, stressed_df in stress_results.items():
    fig.add_trace(go.Scatter(x=stressed_df.index, y=stressed_df['CRYPTO'], name=f"Stressé {label}%", mode="lines"))

future_index = pd.date_range(start=df.index[-1]+pd.Timedelta(days=1), periods=forecast_days, freq="D")

for label, result in forecast_data.items():
    if model_choice == "Auto ARIMA":
        fig.add_trace(go.Scatter(x=future_index, y=result["forecast"], name=f"Forecast Stressé {label}%", line=dict(dash='dot')))
        fig.add_trace(go.Scatter(x=future_index, y=result["lower"], mode="lines", showlegend=False, line=dict(width=0)))
        fig.add_trace(go.Scatter(x=future_index, y=result["upper"], mode="lines", fill="tonexty", showlegend=False, line=dict(width=0)))
    elif model_choice == "Prophet":
        fig.add_trace(go.Scatter(x=result.index, y=result["yhat"], name=f"Forecast Stressé {label}%", line=dict(dash='dot')))
        fig.add_trace(go.Scatter(x=result.index, y=result["yhat_lower"], mode="lines", showlegend=False, line=dict(width=0)))
        fig.add_trace(go.Scatter(x=result.index, y=result["yhat_upper"], mode="lines", fill="tonexty", showlegend=False, line=dict(width=0)))
    else:
        fig.add_trace(go.Scatter(x=future_index, y=result, name=f"XGBoost Stressé {label}%", line=dict(dash='dot')))

fig.update_layout(
    title="Crypto Stress Test | Machine Learning Forecast",
    template=template,
    height=750,
    hovermode="x unified",
    legend=dict(orientation="h", y=-0.3)
)

st.plotly_chart(fig, use_container_width=True)

# Export
st.subheader("📥 Télécharger les résultats")
csv_buffer = io.StringIO()
if model_choice in ["Auto ARIMA", "Prophet"]:
    df_export = pd.concat([pd.Series(result["forecast"] if model_choice=="Auto ARIMA" else result["yhat"], name=str(label)) for label, result in forecast_data.items()], axis=1)
else:
    df_export = pd.concat([pd.Series(result, name=str(label)) for label, result in forecast_data.items()], axis=1)

df_export.to_csv(csv_buffer)
st.download_button(
    label="💾 Télécharger CSV",
    data=csv_buffer.getvalue(),
    file_name="forecast_ultimate.csv",
    mime="text/csv"
)

st.caption("Made with ❤️ | Powered by Due Diligence AI")
