# 🚀 Ultimate Crypto Stress Test - AI Power Version

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LogisticRegression
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
from pptx import Presentation
from pptx.util import Inches, Pt
import os
import io

# ==================== CONFIG ====================
st.set_page_config(page_title="Crypto Stress Test AI Ultimate", layout="wide")

if "mode" not in st.session_state:
    st.session_state.mode = "Light"
mode_choice = st.toggle("🌗 Dark / Light Mode", value=(st.session_state.mode == "Dark"))
st.session_state.mode = "Dark" if mode_choice else "Light"
template = "plotly_dark" if st.session_state.mode == "Dark" else "plotly_white"

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

def fit_lstm(series, steps, epochs=30, neurons=50):
    scaler = MinMaxScaler(feature_range=(0, 1))
    series_scaled = scaler.fit_transform(series.values.reshape(-1, 1))

    X, y = [], []
    look_back = 30
    for i in range(look_back, len(series_scaled)):
        X.append(series_scaled[i-look_back:i, 0])
        y.append(series_scaled[i, 0])
    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    model = Sequential()
    model.add(LSTM(neurons, input_shape=(X.shape[1], 1)))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit(X, y, epochs=epochs, batch_size=16, verbose=0)

    future_inputs = series_scaled[-look_back:]
    preds = []
    for _ in range(steps):
        input_reshaped = np.reshape(future_inputs, (1, look_back, 1))
        pred = model.predict(input_reshaped, verbose=0)
        preds.append(pred[0,0])
        future_inputs = np.append(future_inputs[1:], pred)

    preds_inverse = scaler.inverse_transform(np.array(preds).reshape(-1,1)).flatten()
    return preds_inverse

def predict_direction(series):
    series = series.pct_change().dropna()
    X = series.shift(1).dropna().values.reshape(-1, 1)
    y = (series[1:] > 0).astype(int).values

    model = LogisticRegression()
    model.fit(X, y)

    next_input = series.iloc[-1]
    prediction = model.predict([[next_input]])
    return "BUY" if prediction[0] == 1 else "SELL"

def generate_pptx(summary_text, signal):
    prs = Presentation()
    slide_layout = prs.slide_layouts[5]

    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    title.text = "Crypto Stress Test AI Results"

    content = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(8), Inches(4))
    tf = content.text_frame
    tf.text = f"Summary:\n{summary_text}\n\nSignal Recommendation: {signal}"

    pptx_io = io.BytesIO()
    prs.save(pptx_io)
    pptx_io.seek(0)
    return pptx_io

# ==================== INTERFACE ====================
st.title("📈 Ultimate Crypto Stress Test AI")
st.caption("Due Diligence AI | Intelligent Forecasting and Trading Signals 🚀")
st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    available_files = load_files(FOLDER_PATH)
    file_selected = st.selectbox("📁 Choisir Crypto:", available_files)
with col2:
    model_choice = st.radio("🧠 Modèle:", ["ARIMA", "Prophet", "LSTM"], horizontal=True)
with col3:
    lookback_days = st.slider("📅 Fenêtre (jours):", 60, 365, 180, step=30)

col4, col5, col6 = st.columns(3)
with col4:
    forecast_days = st.slider("🔮 Jours de prédiction:", 7, 60, 14)
with col5:
    shock_pct = st.slider("💥 Choc Simulé (%):", -90, 90, -30)
with col6:
    shock_day = st.slider("📆 Jour du stress:", 10, 350, 70)

# Load Data
filepath = os.path.join(FOLDER_PATH, file_selected)
df = load_crypto_data(filepath, lookback_days)
if df.empty:
    st.error("❌ Aucun fichier valide.")
    st.stop()

# Stress Test
st.subheader("💥 Simulation de Stress")
stress_df = df.copy()
stress_date = stress_df.index[min(shock_day, len(df)-1)]
stress_df.loc[stress_date:, 'CRYPTO'] *= (1 + shock_pct/100)

# Fragility
st.subheader("📊 Fragilité du Marché")
volatility = df['CRYPTO'].pct_change().std()
fragility_score = max(0, 100 - volatility * 1000)
st.metric("Indice de Fragilité", f"{fragility_score:.2f} / 100")

# Forecast
st.subheader("🔮 Prédiction Post-Stress")
with st.spinner("Training model..."):
    if model_choice == "ARIMA":
        forecast_original, _ = fit_arima(df['CRYPTO'], forecast_days)
        forecast_stressed, _ = fit_arima(stress_df['CRYPTO'], forecast_days)
    elif model_choice == "Prophet":
        forecast_original = fit_prophet(df['CRYPTO'], forecast_days)
        forecast_stressed = fit_prophet(stress_df['CRYPTO'], forecast_days)
    else:
        forecast_original = fit_lstm(df['CRYPTO'], forecast_days)
        forecast_stressed = fit_lstm(stress_df['CRYPTO'], forecast_days)

# Direction Prediction
signal = predict_direction(df['CRYPTO'])
st.success(f"✅ Signal IA: {signal}")

# Visualization
st.subheader("📈 Visualisation Finale")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df['CRYPTO'], name="Original", line=dict(color="#00BFFF")))
fig.add_trace(go.Scatter(x=stress_df.index, y=stress_df['CRYPTO'], name="Stressé", line=dict(color="#FF4500")))

future_index = pd.date_range(start=df.index[-1]+pd.Timedelta(days=1), periods=forecast_days, freq="D")
if model_choice == "ARIMA":
    fig.add_trace(go.Scatter(x=future_index, y=forecast_original, name="Prévision Originale", line=dict(color="#90EE90", dash="dot")))
    fig.add_trace(go.Scatter(x=future_index, y=forecast_stressed, name="Prévision Stressée", line=dict(color="#FFA07A", dash="dot")))
elif model_choice == "Prophet":
    fig.add_trace(go.Scatter(x=forecast_original.index, y=forecast_original['yhat'], name="Prévision Originale", line=dict(color="#90EE90", dash="dot")))
    fig.add_trace(go.Scatter(x=forecast_stressed.index, y=forecast_stressed['yhat'], name="Prévision Stressée", line=dict(color="#FFA07A", dash="dot")))
else:
    fig.add_trace(go.Scatter(x=future_index, y=forecast_original, name="Prévision LSTM Original", line=dict(color="#90EE90", dash="dot")))
    fig.add_trace(go.Scatter(x=future_index, y=forecast_stressed, name="Prévision LSTM Stressée", line=dict(color="#FFA07A", dash="dot")))

fig.update_layout(template=template, hovermode="x unified", height=750, legend=dict(orientation="h", y=-0.2))
st.plotly_chart(fig, use_container_width=True)

# Export CSV and PPTX
st.subheader("📥 Exporter Résultats")
csv_buffer = io.StringIO()

if model_choice in ["ARIMA", "LSTM"]:
    export_df = pd.DataFrame({
        "Forecast_Original": forecast_original if isinstance(forecast_original, np.ndarray) else forecast_original.values,
        "Forecast_Stressé": forecast_stressed if isinstance(forecast_stressed, np.ndarray) else forecast_stressed.values
    }, index=future_index)
else:
    export_df = pd.DataFrame({
        "Forecast_Original": forecast_original['yhat'].values,
        "Forecast_Stressé": forecast_stressed['yhat'].values
    }, index=forecast_original.index)

export_df.to_csv(csv_buffer)
st.download_button("💾 Télécharger CSV", data=csv_buffer.getvalue(), file_name="forecast_ai_crypto.csv", mime="text/csv")

pptx_file = generate_pptx(f"Forecast horizon: {forecast_days} jours, Fragilité: {fragility_score:.2f} / 100", signal)
st.download_button("📑 Télécharger Résumé PPTX", data=pptx_file, file_name="forecast_ai_summary.pptx", mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")

st.caption("Built with ❤️ | Ultimate Crypto AI Forecast | Due Diligence AI Platform 🚀")
