# 🚀 Ultimate Crypto Stress Test AI - Professional Full Version

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
import io
import os

# ========== CONFIGURATION ========== #
st.set_page_config(page_title="Crypto Stress Test AI - Full Pro", layout="wide")

if "mode" not in st.session_state:
    st.session_state.mode = "Light"
mode_choice = st.toggle("🌗 Dark / Light Mode", value=(st.session_state.mode == "Dark"))
st.session_state.mode = "Dark" if mode_choice else "Light"
template = "plotly_dark" if st.session_state.mode == "Dark" else "plotly_white"

FOLDER_PATH = "C:/Users/informasud/Desktop/Data-Preparation/LOT3"

# ========== FUNCTIONS ========== #

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

def fit_lstm(series, steps, epochs=40, neurons=64):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(series.values.reshape(-1, 1))
    X, y = [], []
    look_back = 30
    for i in range(look_back, len(scaled)):
        X.append(scaled[i-look_back:i, 0])
        y.append(scaled[i, 0])
    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    model = Sequential()
    model.add(LSTM(neurons, input_shape=(X.shape[1], 1)))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X, y, epochs=epochs, batch_size=16, verbose=0)

    inputs = scaled[-look_back:]
    preds = []
    for _ in range(steps):
        input_reshaped = np.reshape(inputs, (1, look_back, 1))
        pred = model.predict(input_reshaped, verbose=0)
        preds.append(pred[0,0])
        inputs = np.append(inputs[1:], pred)

    preds = scaler.inverse_transform(np.array(preds).reshape(-1,1)).flatten()
    return preds

def predict_signal(series):
    returns = series.pct_change().dropna()
    X = returns.shift(1).dropna().values.reshape(-1,1)
    y = (returns[1:] > 0).astype(int).values
    model = LogisticRegression()
    model.fit(X, y)
    last_return = returns.iloc[-1]
    prediction = model.predict([[last_return]])
    return "BUY" if prediction[0]==1 else "SELL"

def generate_pptx(summary, signal, risk_score):
    prs = Presentation()
    slide_layout = prs.slide_layouts[5]

    # Cover Slide
    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    title.text = "Crypto Stress Test AI - Results"

    # Summary Slide
    slide = prs.slides.add_slide(slide_layout)
    tf = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(8), Inches(5)).text_frame
    tf.text = f"Summary:\n{summary}\n\nRisk Score: {risk_score:.2f}/100"

    # Signal Slide
    slide = prs.slides.add_slide(slide_layout)
    tf = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(8), Inches(5)).text_frame
    tf.text = f"AI Trading Signal:\n{signal}"

    pptx_io = io.BytesIO()
    prs.save(pptx_io)
    pptx_io.seek(0)
    return pptx_io

# ========== INTERFACE ========== #

st.title("📈 Crypto Stress Test AI - Professional Edition")
st.caption("Due Diligence AI | Advanced Risk Analysis Platform 🚀")
st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    available_files = load_files(FOLDER_PATH)
    file_selected = st.selectbox("📁 Crypto Asset:", available_files)
with col2:
    model_choice = st.radio("🧠 Model:", ["ARIMA", "Prophet", "LSTM"], horizontal=True)
with col3:
    lookback_days = st.slider("📅 Lookback Days:", 60, 365, 180, step=30)

col4, col5, col6 = st.columns(3)
with col4:
    forecast_days = st.slider("🔮 Forecast Horizon (days):", 7, 90, 30)
with col5:
    shock_pct = st.slider("💥 Simulated Shock (%):", -90, 90, -30)
with col6:
    shock_day = st.slider("📆 Shock Day:", 10, 350, 70)

filepath = os.path.join(FOLDER_PATH, file_selected)
df = load_crypto_data(filepath, lookback_days)
if df.empty:
    st.error("❌ No valid data found.")
    st.stop()

# Stress Test
stress_df = df.copy()
stress_date = stress_df.index[min(shock_day, len(df)-1)]
stress_df.loc[stress_date:, 'CRYPTO'] *= (1 + shock_pct/100)

# Fragility
volatility = df['CRYPTO'].pct_change().std()
fragility_score = max(0, 100 - volatility * 1000)

# Forecast
with st.spinner("Training model..."):
    if model_choice == "ARIMA":
        forecast_orig, _ = fit_arima(df['CRYPTO'], forecast_days)
        forecast_stress, _ = fit_arima(stress_df['CRYPTO'], forecast_days)
    elif model_choice == "Prophet":
        forecast_orig = fit_prophet(df['CRYPTO'], forecast_days)
        forecast_stress = fit_prophet(stress_df['CRYPTO'], forecast_days)
    else:
        forecast_orig = fit_lstm(df['CRYPTO'], forecast_days)
        forecast_stress = fit_lstm(stress_df['CRYPTO'], forecast_days)

# AI Signal
signal = predict_signal(df['CRYPTO'])
st.success(f"✅ AI Trading Signal: {signal}")

# Visualization
future_idx = pd.date_range(start=df.index[-1]+pd.Timedelta(days=1), periods=forecast_days, freq='D')
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df['CRYPTO'], name="Original", line=dict(color="#00BFFF")))
fig.add_trace(go.Scatter(x=stress_df.index, y=stress_df['CRYPTO'], name="Stress", line=dict(color="#FF4500")))

if model_choice == "ARIMA":
    fig.add_trace(go.Scatter(x=future_idx, y=forecast_orig, name="Forecast Original", line=dict(dash='dot')))
    fig.add_trace(go.Scatter(x=future_idx, y=forecast_stress, name="Forecast Stress", line=dict(dash='dot')))
elif model_choice == "Prophet":
    fig.add_trace(go.Scatter(x=forecast_orig.index, y=forecast_orig['yhat'], name="Forecast Original", line=dict(dash='dot')))
    fig.add_trace(go.Scatter(x=forecast_stress.index, y=forecast_stress['yhat'], name="Forecast Stress", line=dict(dash='dot')))
else:
    fig.add_trace(go.Scatter(x=future_idx, y=forecast_orig, name="Forecast LSTM Original", line=dict(dash='dot')))
    fig.add_trace(go.Scatter(x=future_idx, y=forecast_stress, name="Forecast LSTM Stress", line=dict(dash='dot')))

fig.update_layout(template=template, hovermode="x unified", height=750, legend=dict(orientation="h", y=-0.2))
st.plotly_chart(fig, use_container_width=True)

# Export
csv_buffer = io.StringIO()
if model_choice in ["ARIMA", "LSTM"]:
    export_df = pd.DataFrame({
        "Forecast_Original": forecast_orig if isinstance(forecast_orig, np.ndarray) else forecast_orig.values,
        "Forecast_Stress": forecast_stress if isinstance(forecast_stress, np.ndarray) else forecast_stress.values
    }, index=future_idx)
else:
    export_df = pd.DataFrame({
        "Forecast_Original": forecast_orig['yhat'].values,
        "Forecast_Stress": forecast_stress['yhat'].values
    }, index=forecast_orig.index)

st.download_button("💾 Download CSV", data=csv_buffer.getvalue(), file_name="forecast_crypto_ai.csv", mime="text/csv")

pptx_file = generate_pptx(f"{forecast_days} day forecast, fragility {fragility_score:.2f} /100", signal, fragility_score)
st.download_button("📑 Download PPTX Report", data=pptx_file, file_name="crypto_stress_report.pptx", mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")

st.caption("Built with ❤️ | Advanced Crypto Forecasting Platform | Due Diligence AI")
