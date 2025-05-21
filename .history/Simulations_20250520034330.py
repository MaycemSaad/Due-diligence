import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import yfinance as yf
import os
import time
from datetime import datetime, timedelta
import pytz
import warnings
from typing import Dict, Tuple, Optional

# Advanced ML imports
from sklearn.preprocessing import MinMaxScaler, RobustScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Flatten, GlobalAveragePooling1D
from tensorflow.keras.layers import LSTM, Dense, Dropout, Attention, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.regularizers import l2
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import Layer, Permute, Multiply, Lambda
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
        LSTM, Dense, Dropout, Bidirectional,
        Multiply, Permute, Lambda, 
        TimeDistributed, Flatten, Activation,
        RepeatVector
    )
from tensorflow.keras.regularizers import l2
from tensorflow.keras.optimizers import Adam
from typing import Tuple
import tensorflow as tf
from keras_tuner import HyperModel, RandomSearch

# NLP and Sentiment Analysis
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from transformers import pipeline
from textblob import TextBlob
import praw

# Trading and Data
from binance.client import Client
from binance import ThreadedWebsocketManager
import ta  # Technical analysis library
import pandas_ta as pta  # Additional technical indicators

# Reporting
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import pdfkit

# System
import logging
from logging.handlers import RotatingFileHandler
import json
from pathlib import Path

# Configuration
warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8')
st.set_page_config(layout="wide", page_title="Crypto Intelligence Platform")

# Constants
CRYPTO_MAPPING = {
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "BNB-USD": "Binance Coin", 
    "SOL-USD": "Solana",
    "XRP-USD": "Ripple",
    "ADA-USD": "Cardano",
    "DOGE-USD": "Dogecoin",
    "DOT-USD": "Polkadot",
    "AVAX-USD": "Avalanche",
    "MATIC-USD": "Polygon"
}

# Setup logging
def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # File handler
    file_handler = RotatingFileHandler(
        log_dir / 'crypto_platform.log',
        maxBytes=1024*1024*5,  # 5MB
        backupCount=3
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    
    return logger

logger = setup_logging()

class AdvancedCryptoAnalyzer:
    def __init__(self):
        self.scalers = {}
        self.models = {}
        self.sentiment_analyzer = self._init_sentiment_analysis()
        self.binance_client = self._init_binance_client()
        
    def _init_sentiment_analysis(self):
        """Initialize multiple sentiment analysis tools"""
        try:
            nltk.data.find('sentiment/vader_lexicon')
        except:
            nltk.download('vader_lexicon')
        
        return {
            'vader': SentimentIntensityAnalyzer(),
            'transformers': pipeline('sentiment-analysis', device=0),
            'textblob': TextBlob
        }
    
    def _init_binance_client(self):
        """Initialize Binance client with config"""
        try:
            with open('config.json') as f:
                config = json.load(f)
            return Client(config['binance_api_key'], config['binance_api_secret'])
        except:
            return None
        
    def fetch_market_data(self, ticker: str, period: str = "3y") -> pd.DataFrame:
        """Load market data from local file"""
        try:
            file_path = f"C:/Users/informasud/Desktop/Data-Preparation/LOT3/{ticker}.csv"
            
            # Load the data
            df = pd.read_csv(file_path, parse_dates=['Date'], index_col='Date')
            
            # Ensure required columns are present
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in df.columns for col in required_cols):
                raise ValueError(f"Missing required columns in {ticker} data file.")
            
            # Optionally filter data based on the period (if needed)
            if period == "1Y":
                df = df.last('1Y')
            elif period == "3Y":
                df = df.last('3Y')
            
            return self._add_technical_indicators(df)
            
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    
    
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add multiple technical indicators to dataframe"""
        if df.empty:
            return df
            
        # Ensure we have required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_cols):
            logger.error("Missing required columns in dataframe")
            return df
            
        try:
            # Moving Averages
            df['MA_20'] = df['Close'].rolling(window=20, min_periods=1).mean()
            df['MA_50'] = df['Close'].rolling(window=50, min_periods=1).mean()
            df['MA_200'] = df['Close'].rolling(window=200, min_periods=1).mean()
            
            # Bollinger Bands with error handling
            try:
                bb_results = pta.bbands(df['Close'], length=20, std=2)
                if bb_results is not None and len(bb_results) == 3:
                    df['BB_upper'], df['BB_middle'], df['BB_lower'] = bb_results
                else:
                    logger.warning("Bollinger Bands returned unexpected format")
                    df['BB_upper'], df['BB_middle'], df['BB_lower'] = np.nan, np.nan, np.nan
            except Exception as e:
                logger.warning(f"Bollinger Bands failed: {str(e)}")
                df['BB_upper'], df['BB_middle'], df['BB_lower'] = np.nan, np.nan, np.nan
            
            # RSI
            df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
            
            # MACD
            macd = ta.trend.MACD(df['Close'])
            df['MACD'] = macd.macd()
            df['MACD_signal'] = macd.macd_signal()
            df['MACD_diff'] = df['MACD'] - df['MACD_signal']
            
            return df.dropna()
        except Exception as e:
            logger.error(f"Technical indicators failed: {str(e)}")
            return df  # Return original data if indicators fail
    
    
    
    def get_coin_metrics(self, ticker: str) -> Dict[str, float]:
        """Enhanced coin metrics with additional indicators"""
        try:
            df = self.fetch_market_data(ticker, period="3mo")
            btc_df = self.fetch_market_data("BTC-USD", period="3mo")
            
            if df.empty or btc_df.empty:
                return {}
                
            # Basic metrics
            returns = df['Close'].pct_change().dropna()
            vol = returns.std() * np.sqrt(252) * 100  # Annualized volatility
            mom = (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100
            
            # Risk-adjusted metrics
            sharpe = (returns.mean() / returns.std()) * np.sqrt(252)
            sortino = self._calculate_sortino_ratio(returns)
            
            # Drawdown
            cummax = df['Close'].cummax()
            maxdd = ((df['Close'] - cummax) / cummax).min() * 100
            
            # Correlation
            common_index = df.index.intersection(btc_df.index)
            corr = df.loc[common_index, 'Close'].pct_change().corr(
                btc_df.loc[common_index, 'Close'].pct_change()
            )
            
            # Liquidity (average volume last 30 days)
            liquidity = df['Volume'].tail(30).mean()
            
            # Market regime (bull/bear)
            regime = "Bull" if mom > 0 else "Bear"
            
            return {
                'volatility': vol,
                'momentum': mom,
                'sharpe': sharpe,
                'sortino': sortino,
                'max_drawdown': maxdd,
                'btc_correlation': corr,
                'liquidity': liquidity,
                'market_regime': regime,
                'rsi': df['RSI'].iloc[-1],
                'macd_signal': "Bullish" if df['MACD_diff'].iloc[-1] > 0 else "Bearish",
                'bollinger_position': self._get_bollinger_position(df)
            }
        except Exception as e:
            logger.error(f"Error calculating metrics for {ticker}: {str(e)}")
            return {}
    
    def _calculate_sortino_ratio(self, returns: pd.Series) -> float:
        """Calculate Sortino ratio (risk-adjusted return)"""
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std()
        if downside_std == 0:
            return 0
        return (returns.mean() * 252) / (downside_std * np.sqrt(252))
    
    def _get_bollinger_position(self, df: pd.DataFrame) -> str:
        """Determine position within Bollinger Bands"""
        last_close = df['Close'].iloc[-1]
        upper = df['BB_upper'].iloc[-1]
        lower = df['BB_lower'].iloc[-1]
        
        if last_close > upper:
            return "Above Upper Band (Overbought)"
        elif last_close < lower:
            return "Below Lower Band (Oversold)"
        elif (upper - lower) / df['BB_middle'].iloc[-1] < 0.1:
            return "Low Volatility (Squeeze)"
        else:
            return "Within Bands"
        
    def preprocess_data(self, data: pd.Series, lookback: int = 60) -> Tuple[np.ndarray, np.ndarray]:
        """Enhanced data preprocessing with multiple scaling options"""
        # Robust scaling is better for financial data with outliers
        scaler = RobustScaler()
        
        # Convert to numpy array and reshape for scaling
        values = data.values.reshape(-1, 1)
        scaled = scaler.fit_transform(values)
        
        # Store the scaler using the ticker as key
        key = getattr(data, 'name', 'default_key')
        self.scalers[key] = scaler
        
        X, y = [], []
        for i in range(lookback, len(scaled)):
            X.append(scaled[i-lookback:i])
            y.append(scaled[i])
            
        # Ensure we return arrays with matching dimensions
        if len(X) != len(y):
            min_len = min(len(X), len(y))
            X = X[:min_len]
            y = y[:min_len]
            
        return np.array(X), np.array(y)
    
    

    from tensorflow.keras.layers import Layer
    import tensorflow as tf

    class AttentionLayer(Layer):
        """
        Implementation of attention mechanism for time series forecasting.
        This layer learns to focus on important time steps in the sequence.
        """
        def __init__(self, return_attention_scores=False, **kwargs):
            super(AttentionLayer, self).__init__(**kwargs)
            self.return_attention_scores = return_attention_scores

        def build(self, input_shape):
            self.W = self.add_weight(name='attention_weights',
                                shape=(input_shape[-1], 1),
                                initializer='glorot_uniform',
                                trainable=True)
            self.b = self.add_weight(name='attention_bias',
                                shape=(input_shape[1], 1),
                                initializer='zeros',
                                trainable=True)
            super(AttentionLayer, self).build(input_shape)

        def call(self, x):
            # Calculate attention scores
            e = tf.nn.tanh(tf.matmul(x, self.W) + self.b)
            
            # Get attention weights
            a = tf.nn.softmax(e, axis=1)
            
            # Apply attention weights
            output = x * a
            
            if self.return_attention_scores:
                return tf.reduce_sum(output, axis=1), a
            return tf.reduce_sum(output, axis=1)

        def compute_output_shape(self, input_shape):
            if self.return_attention_scores:
                return [(input_shape[0], input_shape[-1]), (input_shape[0], input_shape[1], 1)]
            return (input_shape[0], input_shape[-1])
        


    # Then your build_advanced_model function
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import (
        LSTM, Dense, Dropout, Bidirectional,
        TimeDistributed, Flatten, Activation,
        RepeatVector, Permute, Lambda
    )
    from tensorflow.keras.regularizers import l2
    from tensorflow.keras.optimizers import Adam
    import tensorflow as tf
    from typing import Tuple

    def build_advanced_model(self, input_shape: Tuple[int, int]) -> tf.keras.Model:
        """Working LSTM model with properly implemented attention mechanism"""
        inputs = tf.keras.Input(shape=input_shape)
        
        # Bidirectional LSTM layers
        lstm1 = Bidirectional(LSTM(128, return_sequences=True, 
                                kernel_regularizer=l2(0.01)))(inputs)
        lstm1 = Dropout(0.4)(lstm1)
        lstm2 = Bidirectional(LSTM(64, return_sequences=True,
                            kernel_regularizer=l2(0.01)))(lstm1)
        
        # Attention mechanism with proper Keras layer wrapping
        attention = TimeDistributed(Dense(1, activation='tanh'))(lstm2)
        
        # Custom layer to handle tensor operations safely
        class AttentionReducer(tf.keras.layers.Layer):
            def call(self, inputs):
                x, attention = inputs
                attention = tf.squeeze(attention, axis=-1)
                attention = tf.nn.softmax(attention, axis=1)
                attention = tf.expand_dims(attention, axis=-1)
                return tf.reduce_sum(x * attention, axis=1)
        
        context = AttentionReducer()([lstm2, attention])
        
        # Final layers
        dense1 = Dense(64, activation='relu')(context)
        dense1 = Dropout(0.3)(dense1)
        dense2 = Dense(32, activation='relu')(dense1)
        output = Dense(1)(dense2)
        
        model = tf.keras.Model(inputs=inputs, outputs=output)
        
        optimizer = Adam(learning_rate=0.001, clipvalue=0.5)
        model.compile(optimizer=optimizer, loss=tf.keras.losses.Huber())
        return model




    def build_simpler_model(self, input_shape: Tuple[int, int]) -> Sequential:
        """Fallback model without attention mechanism"""
        model = Sequential([
            Bidirectional(LSTM(128,
                            return_sequences=False,
                            kernel_regularizer=l2(0.01),
                            input_shape=input_shape)),
            Dropout(0.4),
            Dense(64, activation='relu'),
            Dropout(0.3),
            Dense(32, activation='relu'),
            Dense(1)
        ])
        optimizer = Adam(learning_rate=0.001)
        model.compile(optimizer=optimizer, loss=tf.keras.losses.Huber())
        return model
    

    def train_model(self, X_train: np.ndarray, y_train: np.ndarray, 
                X_val: np.ndarray, y_val: np.ndarray, 
                ticker: str) -> tf.keras.Model:
        """Enhanced model training with callbacks"""
        # Ensure consistent dimensions
        if len(X_val) != len(y_val):
            min_val_len = min(len(X_val), len(y_val))
            X_val = X_val[:min_val_len]
            y_val = y_val[:min_val_len]
        
        # Ensure y values are properly shaped (n_samples, 1)
        y_train = np.reshape(y_train, (-1, 1))
        y_val = np.reshape(y_val, (-1, 1))
        
        # Clear any existing model for this ticker
        if ticker in self.models:
            del self.models[ticker]
        
        # Build model with correct input shape
        model = self.build_advanced_model((X_train.shape[1], X_train.shape[2]))
        
        # Define callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True,
                verbose=1
            ),
            ModelCheckpoint(
                f"models/best_{ticker.replace('-', '_')}.h5",
                monitor='val_loss',
                save_best_only=True,
                save_weights_only=False
            )
        ]
        
        # Train model with additional validation
        try:
            history = model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=200,
                batch_size=64,
                callbacks=callbacks,
                verbose=1  # Changed to 1 to see progress
            )
        except Exception as e:
            print(f"Error during training: {e}")
            # Fallback to simpler model if attention fails
            model = self.build_simpler_model((X_train.shape[1], X_train.shape[2]))
            history = model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=200,
                batch_size=64,
                callbacks=callbacks,
                verbose=1
            )
        
        self.models[ticker] = model
        return model, history

    def build_simpler_model(self, input_shape: Tuple[int, int]) -> Sequential:
        """Fallback model without attention if needed"""
        model = Sequential([
            Bidirectional(LSTM(128,
                            return_sequences=False,
                            kernel_regularizer=l2(0.01),
                            input_shape=input_shape)),
            Dropout(0.4),
            Dense(64, activation='relu'),
            Dropout(0.3),
            Dense(32, activation='relu'),
            Dense(1)
        ])
        optimizer = Adam(learning_rate=0.001)
        model.compile(optimizer=optimizer, loss=tf.keras.losses.Huber())
        return model
    def monte_carlo_prediction(self, model: Sequential, input_seq: np.ndarray, 
                            scaler: MinMaxScaler, n_simulations: int = 200) -> Tuple[float, float, float]:
        """Fixed prediction with proper dimension handling"""
        # Enable dropout at test time for MC Dropout
        preds = []
        for _ in range(n_simulations):
            # Get model prediction
            pred = model(input_seq, training=True)
            
            # Reshape to 2D for inverse transform
            pred_2d = pred.numpy().reshape(-1, 1)
            
            # Inverse transform and store
            preds.append(scaler.inverse_transform(pred_2d)[0][0])
        
        preds = np.array(preds)
        
        # Calculate prediction and confidence intervals
        mean_pred = np.mean(preds)
        std_pred = np.std(preds)
        lower = np.percentile(preds, 2.5)
        upper = np.percentile(preds, 97.5)
        
        return mean_pred, lower, upper, std_pred
    def generate_trading_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate comprehensive trading signals"""
        df = df.copy()
        
        # Trend signals
        df['MA_Crossover'] = np.where(
            df['MA_20'] > df['MA_50'], 1, -1
        )
        
        # Bollinger Band signals
        df['BB_Signal'] = np.select(
            [
                df['Close'] < df['BB_lower'],
                df['Close'] > df['BB_upper']
            ],
            [1, -1],
            default=0
        )
        
        # RSI signals
        df['RSI_Signal'] = np.select(
            [
                df['RSI'] < 30,
                df['RSI'] > 70
            ],
            [1, -1],
            default=0
        )
        
        # MACD signals
        df['MACD_Signal'] = np.where(
            df['MACD'] > df['MACD_signal'], 1, -1
        )
        
        # Composite signal (weighted)
        df['Composite_Signal'] = (
            0.4 * df['MA_Crossover'] + 
            0.3 * df['BB_Signal'] + 
            0.2 * df['RSI_Signal'] + 
            0.1 * df['MACD_Signal']
        )
        
        return df
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Multi-method sentiment analysis"""
        try:
            # VADER
            vader_scores = self.sentiment_analyzer['vader'].polarity_scores(text)
            
            # Transformers
            transformer_result = self.sentiment_analyzer['transformers'](text[:512])[0]
            
            # TextBlob
            blob = self.sentiment_analyzer['textblob'](text)
            
            return {
                'vader_compound': vader_scores['compound'],
                'vader_positive': vader_scores['pos'],
                'vader_negative': vader_scores['neg'],
                'transformer_label': transformer_result['label'],
                'transformer_score': transformer_result['score'],
                'textblob_polarity': blob.sentiment.polarity,
                'textblob_subjectivity': blob.sentiment.subjectivity
            }
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            return {}
    
    def fetch_news_sentiment(self, coin_name: str, limit: int = 50) -> pd.DataFrame:
        """Fetch and analyze news sentiment from multiple sources"""
        try:
            # Initialize Reddit client
            reddit = praw.Reddit(
                client_id='your_client_id',
                client_secret='your_client_secret',
                user_agent='CryptoAnalysis'
            )
            
            # Fetch Reddit posts
            posts = []
            subreddit = reddit.subreddit('CryptoCurrency')
            for post in subreddit.search(coin_name, sort='new', limit=limit):
                posts.append({
                    'source': 'Reddit',
                    'title': post.title,
                    'content': post.selftext,
                    'created': datetime.fromtimestamp(post.created_utc),
                    'score': post.score
                })
            
            # Analyze sentiment
            results = []
            for post in posts:
                analysis = self.analyze_sentiment(f"{post['title']}. {post['content']}")
                results.append({
                    'source': post['source'],
                    'date': post['created'],
                    'title': post['title'],
                    'vader_score': analysis.get('vader_compound', 0),
                    'transformer_score': analysis.get('transformer_score', 0),
                    'transformer_label': analysis.get('transformer_label', 'NEUTRAL'),
                    'textblob_polarity': analysis.get('textblob_polarity', 0),
                    'engagement': post['score']
                })
            
            return pd.DataFrame(results)
        except Exception as e:
            logger.error(f"News sentiment error for {coin_name}: {str(e)}")
            return pd.DataFrame()

class CryptoDashboard:
    def __init__(self):
        self.analyzer = AdvancedCryptoAnalyzer()
        self.current_ticker = None
        self.current_data = None
        
    def render_header(self):
        """Render the dashboard header"""
        st.title("🚀 Advanced Crypto Intelligence Platform")
        st.markdown("""
        <style>
        .big-font { font-size:18px !important; }
        </style>
        """, unsafe_allow_html=True)
        
        cols = st.columns([1, 3, 1])
        with cols[1]:
            st.markdown('<p class="big-font">Comprehensive cryptocurrency analysis, forecasting, and trading tools</p>', 
                      unsafe_allow_html=True)
        
    def render_sidebar(self):
        """Render the sidebar controls"""
        with st.sidebar:
            st.image("https://cryptologos.cc/logos/bitcoin-btc-logo.png", width=100)
            st.title("Navigation")
            
            self.current_ticker = st.selectbox(
                "Select Cryptocurrency",
                options=list(CRYPTO_MAPPING.keys()),
                format_func=lambda x: CRYPTO_MAPPING[x],
                index=0
            )
            
            analysis_type = st.radio(
                "Analysis Type",
                options=["Technical Analysis", "Price Forecast", "Sentiment Analysis", "Trading Signals"]
            )
            
            time_frame = st.selectbox(
                "Time Frame",
                options=["1D", "1W", "1M", "3M", "1Y", "3Y", "5Y"],
                index=4
            )
            
            st.markdown("---")
            st.markdown("**Advanced Options**")
            show_raw = st.checkbox("Show Raw Data", value=False)
            st.markdown("---")
            
            if st.button("🔄 Refresh Data"):
                st.rerun()
                
            st.markdown("""
            <div style="margin-top: 50px; font-size: 12px; color: #666;">
            <b>Disclaimer:</b> This is for educational purposes only. 
            Not financial advice.
            </div>
            """, unsafe_allow_html=True)
            
            return analysis_type, time_frame, show_raw
    
    def render_price_forecast(self, ticker: str):
        """Render the price forecasting section with improved dimension handling"""
        st.header(f"{CRYPTO_MAPPING[ticker]} Price Forecast")
        
        with st.expander("Forecasting Methodology"):
            st.markdown("""
            Our forecasting system utilizes:
            - **Bidirectional LSTM** neural networks with attention mechanisms
            - **Monte Carlo Dropout** for uncertainty estimation
            - **Robust Scaling** to manage market outliers
            - **Multiple Technical Indicators** as model features
            """)

        with st.spinner("Training forecasting model..."):
            data = self.analyzer.fetch_market_data(ticker, period="5y")
            
            if data.empty:
                st.error("Failed to fetch data for forecasting")
                return
                
            lookback = 90  # 3 months lookback
            close_prices = data['Close'].copy()
            close_prices.name = ticker
            
            # Preprocess data
            X, y = self.analyzer.preprocess_data(close_prices, lookback)
            min_length = min(len(X), len(y))
            X = X[:min_length]
            y = y[:min_length]
            
            # Train-test split
            split = int(len(X) * 0.8)
            X_train, y_train = X[:split], y[:split]
            X_test, y_test = X[split:], y[split:]

            # Ensure validation data has matching dimensions
            if len(X_test) != len(y_test):
                min_test_len = min(len(X_test), len(y_test))
                X_test = X_test[:min_test_len]
                y_test = y_test[:min_test_len]
            
            # Train model
            model, history = self.analyzer.train_model(
                X_train, y_train, X_test, y_test, ticker
            )
            
            # Make prediction
            last_seq = X[-1].reshape(1, lookback, 1)
            pred, lower, upper, std = self.analyzer.monte_carlo_prediction(
                model, last_seq, self.analyzer.scalers[ticker], n_simulations=200
            )
            
            # Display results
            last_price = float(data['Close'].iloc[-1])
            pred = float(pred)
            direction = "up" if pred > last_price else "down"
            change_pct = abs((pred / last_price - 1) * 100)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Price", f"${last_price:,.2f}")
            with col2:
                st.metric(
                    "Predicted Price", 
                    f"${pred:,.2f}", 
                    delta=f"{direction.capitalize()} {change_pct:.2f}%",
                    delta_color="normal"
                )
            with col3:
                st.metric("Confidence Interval", f"${lower:,.2f} - ${upper:,.2f}")

            # Plot forecast
            fig = go.Figure()
            
            # Historical data
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['Close'],
                name='Actual Price',
                line=dict(color='#1f77b4')
            ))
            
            # Training predictions
            train_pred = model.predict(X_train)
            train_pred = train_pred.squeeze()
            train_pred = self.analyzer.scalers[ticker].inverse_transform(train_pred.reshape(-1, 1)).flatten()
            
            train_dates = data.index[lookback:lookback+len(train_pred)]
            fig.add_trace(go.Scatter(
                x=train_dates,
                y=train_pred,
                name='Training Fit',
                line=dict(color='#ff7f0e', dash='dot')
            ))
            
            # Test predictions
            test_pred = model.predict(X_test)
            test_pred = test_pred.squeeze()
            test_pred = self.analyzer.scalers[ticker].inverse_transform(test_pred.reshape(-1, 1)).flatten()
            
            test_dates = data.index[lookback+split:lookback+split+len(test_pred)]
            fig.add_trace(go.Scatter(
                x=test_dates,
                y=test_pred,
                name='Test Prediction',
                line=dict(color='#2ca02c', dash='dot')
            ))
            
            # Future prediction
            next_date = data.index[-1] + timedelta(days=1)
            fig.add_trace(go.Scatter(
                x=[next_date],
                y=[pred],
                mode='markers',
                marker=dict(size=12, color='red'),
                name='Next Day Forecast'
            ))
            
            # Confidence interval
            fig.add_trace(go.Scatter(
                x=[next_date, next_date],
                y=[lower, upper],
                mode='lines',
                fill='tonexty',
                fillcolor='rgba(255,0,0,0.2)',
                line=dict(width=0),
                name='95% Confidence'
            ))
            
            fig.update_layout(
                title=f"{CRYPTO_MAPPING[ticker]} Price Forecast",
                xaxis_title='Date',
                yaxis_title='Price (USD)',
                hovermode='x unified',
                template='plotly_white',
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Model performance metrics
            y_true = y_test.reshape(-1, 1)
            y_pred = model.predict(X_test).reshape(-1, 1)
            
            # Inverse transform
            y_true = self.analyzer.scalers[ticker].inverse_transform(y_true)
            y_pred = self.analyzer.scalers[ticker].inverse_transform(y_pred)

            # Calculate metrics
            mae = mean_absolute_error(y_true, y_pred)
            rmse = np.sqrt(mean_squared_error(y_true, y_pred))
            mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-10))) * 100
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("MAE", f"${mae:,.2f}")
            with col2:
                st.metric("RMSE", f"${rmse:,.2f}")
            with col3:
                st.metric("MAPE", f"{mape:.2f}%")
            
            # Trading recommendation
            st.subheader("Trading Recommendation")
            
            if direction == "up":
                st.success(f"**Buy Signal** - Predicted price increase of {change_pct:.2f}%")
            else:
                st.error(f"**Sell Signal** - Predicted price decrease of {change_pct:.2f}%")
    
    
    
    
    
    
    
    
def render_technical_analysis(self, ticker: str, time_frame: str):
    """Render technical analysis charts"""
    st.header(f"{CRYPTO_MAPPING[ticker]} Technical Analysis")
    
    with st.spinner(f"Fetching {time_frame} data for {CRYPTO_MAPPING[ticker]}..."):
        data = self.analyzer.fetch_market_data(ticker)

        if data.empty:
            st.error("Failed to fetch technical analysis data. Possible reasons:")
            st.markdown("""
            - Ensure the cryptocurrency ticker is correct
            - Verify that the data files are present in the specified directory
            """)
            return
            
        self.current_data = data
        
    # Check for technical indicators
    if 'MA_20' not in data.columns:
        st.warning("Technical indicators could not be calculated. Showing raw price data.")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            name='Price',
            line=dict(color='gray')
        ))
        st.plotly_chart(fig, use_container_width=True)
        return
    
    # Proceed with rendering technical analysis...
        
        # Continue with your existing technical analysis rendering code...
        # Example: Plotting Moving Averages
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            name='Close Price',
            line=dict(color='blue')
        ))
        
        if 'MA_20' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['MA_20'],
                name='20-Day MA',
                line=dict(color='orange')
            ))
        
        if 'MA_50' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['MA_50'],
                name='50-Day MA',
                line=dict(color='red')
            ))

        fig.update_layout(
            title=f"{CRYPTO_MAPPING[ticker]} Technical Analysis",
            xaxis_title='Date',
            yaxis_title='Price (USD)',
            hovermode='x unified',
            template='plotly_white',
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    
    
    
    def render_sentiment_analysis(self, ticker: str):
        """Render sentiment analysis section"""
        coin_name = CRYPTO_MAPPING[ticker]
        st.header(f"{coin_name} Sentiment Analysis")
        
        with st.spinner("Fetching and analyzing sentiment data..."):
            sentiment_df = self.analyzer.fetch_news_sentiment(coin_name)
            
            if sentiment_df.empty:
                st.warning("No sentiment data available")
                return
                
            # Aggregate sentiment
            avg_sentiment = {
                'VADER': sentiment_df['vader_score'].mean(),
                'Transformer': sentiment_df[sentiment_df['transformer_label'] == 'POSITIVE']['transformer_score'].mean(),
                'TextBlob': sentiment_df['textblob_polarity'].mean()
            }
            
            # Display sentiment metrics
            st.subheader("Overall Sentiment")
            
            cols = st.columns(3)
            with cols[0]:
                st.metric(
                    "VADER Score",
                    f"{avg_sentiment['VADER']:.2f}",
                    delta="Positive" if avg_sentiment['VADER'] > 0 else "Negative"
                )
            with cols[1]:
                st.metric(
                    "Transformer Score",
                    f"{avg_sentiment['Transformer']:.2f}",
                    delta="Positive" if avg_sentiment['Transformer'] > 0.5 else "Negative"
                )
            with cols[2]:
                st.metric(
                    "TextBlob Polarity",
                    f"{avg_sentiment['TextBlob']:.2f}",
                    delta="Positive" if avg_sentiment['TextBlob'] > 0 else "Negative"
                )
            
            # Sentiment over time
            st.subheader("Sentiment Over Time")
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=sentiment_df['date'],
                y=sentiment_df['vader_score'].rolling(7).mean(),
                name='VADER (7-day MA)',
                line=dict(color='blue')
            ))
            
            fig.add_trace(go.Scatter(
                x=sentiment_df['date'],
                y=sentiment_df['textblob_polarity'].rolling(7).mean(),
                name='TextBlob (7-day MA)',
                line=dict(color='green')
            ))
            
            fig.update_layout(
                title="Sentiment Trend",
                xaxis_title='Date',
                yaxis_title='Sentiment Score',
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Most positive/negative posts
            st.subheader("Key Sentiment Highlights")
            
            pos_post = sentiment_df.loc[sentiment_df['vader_score'].idxmax()]
            neg_post = sentiment_df.loc[sentiment_df['vader_score'].idxmin()]
            
            cols = st.columns(2)
            with cols[0]:
                st.markdown("**Most Positive Post**")
                st.markdown(f"*{pos_post['title']}*")
                st.markdown(f"Score: {pos_post['vader_score']:.2f}")
                st.markdown(f"Date: {pos_post['date'].strftime('%Y-%m-%d')}")
                
            with cols[1]:
                st.markdown("**Most Negative Post**")
                st.markdown(f"*{neg_post['title']}*")
                st.markdown(f"Score: {neg_post['vader_score']:.2f}")
                st.markdown(f"Date: {neg_post['date'].strftime('%Y-%m-%d')}")
            
            # Raw sentiment data
            with st.expander("View Raw Sentiment Data"):
                st.dataframe(sentiment_df.sort_values('date', ascending=False))
    
    
    
    def render_trading_signals(self, ticker: str):
        """Render trading signals section"""
        if self.current_data is None:
            self.current_data = self.analyzer.fetch_market_data(ticker, period="1y")
            
        signals_df = self.analyzer.generate_trading_signals(self.current_data)
        
        st.header(f"{CRYPTO_MAPPING[ticker]} Trading Signals")
        
        # Current signals
        last_signals = signals_df.iloc[-1]
        
        st.subheader("Current Signals")
        
        cols = st.columns(4)
        with cols[0]:
            st.metric(
                "Moving Average Crossover",
                "Bullish" if last_signals['MA_Crossover'] > 0 else "Bearish"
            )
        with cols[1]:
            st.metric(
                "Bollinger Band",
                "Buy" if last_signals['BB_Signal'] > 0 else "Sell" if last_signals['BB_Signal'] < 0 else "Neutral"
            )
        with cols[2]:
            st.metric(
                "RSI",
                "Oversold" if last_signals['RSI_Signal'] > 0 else "Overbought" if last_signals['RSI_Signal'] < 0 else "Neutral"
            )
        with cols[3]:
            st.metric(
                "Composite Signal",
                "Strong Buy" if last_signals['Composite_Signal'] > 0.5 else "Buy" if last_signals['Composite_Signal'] > 0 else "Sell" if last_signals['Composite_Signal'] < -0.5 else "Neutral"
            )
        
        # Signal visualization
        st.subheader("Signal History")
        
        fig = go.Figure()
        
        # Price with signals
        fig.add_trace(go.Scatter(
            x=signals_df.index,
            y=signals_df['Close'],
            name='Price',
            line=dict(color='gray')
        ))
        
        # Buy signals
        buy_signals = signals_df[signals_df['Composite_Signal'] > 0.3]
        fig.add_trace(go.Scatter(
            x=buy_signals.index,
            y=buy_signals['Close'],
            mode='markers',
            marker=dict(color='green', size=10),
            name='Buy Signal'
        ))
        
        # Sell signals
        sell_signals = signals_df[signals_df['Composite_Signal'] < -0.3]
        fig.add_trace(go.Scatter(
            x=sell_signals.index,
            y=sell_signals['Close'],
            mode='markers',
            marker=dict(color='red', size=10),
            name='Sell Signal'
        ))
        
        fig.update_layout(
            title="Price with Trading Signals",
            xaxis_title='Date',
            yaxis_title='Price (USD)',
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Signal strength over time
        st.subheader("Signal Strength")
        
        fig2 = go.Figure()
        
        fig2.add_trace(go.Scatter(
            x=signals_df.index,
            y=signals_df['Composite_Signal'],
            name='Composite Signal',
            line=dict(color='purple')
        ))
        
        fig2.add_hline(y=0.5, line_dash="dash", line_color="green")
        fig2.add_hline(y=-0.5, line_dash="dash", line_color="red")
        fig2.add_hline(y=0, line_color="gray")
        
        fig2.update_layout(
            title="Composite Signal Strength Over Time",
            xaxis_title='Date',
            yaxis_title='Signal Strength',
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # Performance analysis
        st.subheader("Backtest Performance")
        
        # Calculate hypothetical returns
        signals_df['Daily_Return'] = signals_df['Close'].pct_change()
        signals_df['Strategy_Return'] = signals_df['Composite_Signal'].shift(1) * signals_df['Daily_Return']
        signals_df['Cumulative_Market'] = (1 + signals_df['Daily_Return']).cumprod()
        signals_df['Cumulative_Strategy'] = (1 + signals_df['Strategy_Return']).cumprod()
        
        # Performance metrics
        total_market_return = (signals_df['Cumulative_Market'].iloc[-1] - 1) * 100
        total_strategy_return = (signals_df['Cumulative_Strategy'].iloc[-1] - 1) * 100
        sharpe_ratio = np.sqrt(252) * signals_df['Strategy_Return'].mean() / signals_df['Strategy_Return'].std()
        
        cols = st.columns(3)
        with cols[0]:
            st.metric("Buy & Hold Return", f"{total_market_return:.1f}%")
        with cols[1]:
            st.metric("Strategy Return", f"{total_strategy_return:.1f}%")
        with cols[2]:
            st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")
        
        # Equity curve
        fig3 = go.Figure()
        
        fig3.add_trace(go.Scatter(
            x=signals_df.index,
            y=signals_df['Cumulative_Market'],
            name='Buy & Hold',
            line=dict(color='blue')
        ))
        
        fig3.add_trace(go.Scatter(
            x=signals_df.index,
            y=signals_df['Cumulative_Strategy'],
            name='Trading Strategy',
            line=dict(color='green')
        ))
        
        fig3.update_layout(
            title="Strategy vs Buy & Hold Performance",
            xaxis_title='Date',
            yaxis_title='Cumulative Return',
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig3, use_container_width=True)
        
        # Trade log
        st.subheader("Trade Simulation")
        
        # Generate trade log
        signals_df['Position'] = np.where(signals_df['Composite_Signal'] > 0.3, 1, 
                                        np.where(signals_df['Composite_Signal'] < -0.3, -1, 0))
        signals_df['Trade'] = signals_df['Position'].diff()
        
        trades = signals_df[signals_df['Trade'] != 0].copy()
        trades['Trade_Return'] = trades['Daily_Return'] * trades['Position'].shift(1)
        trades['Trade_Type'] = np.where(trades['Trade'] > 0, 'Buy', 'Sell')
        
        # Display trade log
        with st.expander("View Trade Log"):
            trade_display = trades[['Close', 'Trade_Type', 'Trade_Return']].copy()
            trade_display['Trade_Return'] = trade_display['Trade_Return'] * 100
            trade_display.columns = ['Price', 'Action', 'Return (%)']
            st.dataframe(
                trade_display.style.format({
                    'Price': '{:.2f}',
                    'Return (%)': '{:.2f}%'
                })
            )
        
        # Win rate and stats
        if not trades.empty:
            win_rate = (trades['Trade_Return'] > 0).mean() * 100
            avg_win = trades[trades['Trade_Return'] > 0]['Trade_Return'].mean() * 100
            avg_loss = trades[trades['Trade_Return'] < 0]['Trade_Return'].mean() * 100
            
            cols = st.columns(3)
            with cols[0]:
                st.metric("Win Rate", f"{win_rate:.1f}%")
            with cols[1]:
                st.metric("Avg Win", f"{avg_win:.2f}%")
            with cols[2]:
                st.metric("Avg Loss", f"{avg_loss:.2f}%")
            """Render trading signals section"""
            if self.current_data is None:
                self.current_data = self.analyzer.fetch_market_data(ticker, period="1y")
                
            signals_df = self.analyzer.generate_trading_signals(self.current_data)
            
            st.header(f"{CRYPTO_MAPPING[ticker]} Trading Signals")
            
            # Current signals
            last_signals = signals_df.iloc[-1]
            
            st.subheader("Current Signals")
            
            cols = st.columns(4)
            with cols[0]:
                st.metric(
                    "Moving Average Crossover",
                    "Bullish" if last_signals['MA_Crossover'] > 0 else "Bearish"
                )
            with cols[1]:
                st.metric(
                    "Bollinger Band",
                    "Buy" if last_signals['BB_Signal'] > 0 else "Sell" if last_signals['BB_Signal'] < 0 else "Neutral"
                )
            with cols[2]:
                st.metric(
                    "RSI",
                    "Oversold" if last_signals['RSI_Signal'] > 0 else "Overbought" if last_signals['RSI_Signal'] < 0 else "Neutral"
                )
            with cols[3]:
                st.metric(
                    "Composite Signal",
                    "Strong Buy" if last_signals['Composite_Signal'] > 0.5 else "Buy" if last_signals['Composite_Signal'] > 0 else "Sell" if last_signals['Composite_Signal'] < -0.5 else "Neutral"
                )
            
            # Signal visualization
            st.subheader("Signal History")
            
            fig = go.Figure()
            
            # Price with signals
            fig.add_trace(go.Scatter(
                x=signals_df.index,
                y=signals_df['Close'],
                name='Price',
                line=dict(color='gray')
            ))
            
            # Buy signals
            buy_signals = signals_df[signals_df['Composite_Signal'] > 0.3]

    def generate_pptx_report(self, ticker: str):
        """Generate a comprehensive PowerPoint report with all analysis"""
        try:
            from pptx.util import Inches, Pt
            from pptx.dml.color import RGBColor
            import glob
            import os

            # Create presentation
            prs = Presentation()
            
            # Add title slide
            slide = prs.slides.add_slide(prs.slide_layouts[0])
            title = slide.shapes.title
            subtitle = slide.placeholders[1]
            
            title.text = f"{CRYPTO_MAPPING[ticker]} Analysis Report"
            subtitle.text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}\nCrypto Intelligence Platform"

            # Initialize variables with defaults
            data = pd.DataFrame()
            signals_df = pd.DataFrame()
            metrics = {}
            sentiment_df = pd.DataFrame()

            # Get all data needed with proper error handling
            try:
                data = self.analyzer.fetch_market_data(ticker, period="5y")
                if data.empty:
                    raise ValueError("No data returned for the specified ticker")
                    
                signals_df = self.analyzer.generate_trading_signals(data.copy())
                metrics = self.analyzer.get_coin_metrics(ticker)
                sentiment_df = self.analyzer.fetch_news_sentiment(CRYPTO_MAPPING[ticker])
                
            except Exception as data_error:
                logger.error(f"Data preparation failed: {str(data_error)}")
                # Continue with empty DataFrames rather than failing completely

            # Add overview slide
            try:
                slide = prs.slides.add_slide(prs.slide_layouts[1])
                title = slide.shapes.title
                title.text = "Key Metrics Overview"
                
                rows = 8
                cols = 2
                table = slide.shapes.add_table(rows, cols, Inches(1), Inches(1.5), Inches(8), Inches(4)).table
                
                table.columns[0].width = Inches(3)
                table.columns[1].width = Inches(3)
                
                table.cell(0, 0).text = "Metric"
                table.cell(0, 1).text = "Value"
                
                current_price = data['Close'].iloc[-1] if not data.empty and 'Close' in data.columns else 0
                metrics_data = [
                    ("Current Price", f"${current_price:,.2f}" if current_price else "N/A"),
                    ("Volatility", f"{metrics.get('volatility', 'N/A')}"),
                    ("Momentum", f"{metrics.get('momentum', 'N/A')}"),
                    ("Sharpe Ratio", f"{metrics.get('sharpe', 'N/A')}"),
                    ("Max Drawdown", f"{metrics.get('max_drawdown', 'N/A')}"),
                    ("BTC Correlation", f"{metrics.get('btc_correlation', 'N/A')}"),
                    ("Market Regime", metrics.get('market_regime', 'N/A')),
                    ("RSI", f"{metrics.get('rsi', 'N/A')}")
                ]
                
                for i, (metric, value) in enumerate(metrics_data, start=1):
                    table.cell(i, 0).text = metric
                    table.cell(i, 1).text = str(value)
                    
                for cell in table.iter_cells():
                    for paragraph in cell.text_frame.paragraphs:
                        paragraph.font.size = Pt(12)
                        paragraph.font.name = 'Calibri'
                        
            except Exception as table_error:
                logger.error(f"Metrics table generation failed: {str(table_error)}")

            # Add price chart slide if we have price data
            if not data.empty and 'Close' in data.columns:
                try:
                    slide = prs.slides.add_slide(prs.slide_layouts[1])
                    title = slide.shapes.title
                    title.text = "Price History"
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=data.index, 
                        y=data['Close'], 
                        name='Price',
                        line=dict(color='#1f77b4')
                    ))
                    fig.update_layout(
                        title=f"{CRYPTO_MAPPING[ticker]} Price History",
                        xaxis_title='Date',
                        yaxis_title='Price (USD)',
                        template='plotly_white'
                    )
                    
                    img_path = f"temp_{ticker}_price.png"
                    fig.write_image(img_path, width=1000, height=600)
                    slide.shapes.add_picture(img_path, Inches(0.5), Inches(1.5), height=Inches(5))
                    
                except Exception as chart_error:
                    logger.error(f"Price chart generation failed: {str(chart_error)}")

            # Add technical indicators slide if we have the data
            if not data.empty and all(col in data.columns for col in ['Close', 'MA_20', 'MA_50']):
                try:
                    slide = prs.slides.add_slide(prs.slide_layouts[1])
                    title = slide.shapes.title
                    title.text = "Technical Indicators"
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Price'))
                    
                    # Only add indicators that exist
                    if 'MA_20' in data.columns:
                        fig.add_trace(go.Scatter(x=data.index, y=data['MA_20'], name='20-day MA'))
                    if 'MA_50' in data.columns:
                        fig.add_trace(go.Scatter(x=data.index, y=data['MA_50'], name='50-day MA'))
                    if all(col in data.columns for col in ['BB_upper', 'BB_lower']):
                        fig.add_trace(go.Scatter(
                            x=data.index, y=data['BB_upper'], 
                            name='BB Upper', line=dict(dash='dot')
                        ))
                        fig.add_trace(go.Scatter(
                            x=data.index, y=data['BB_lower'], 
                            name='BB Lower', line=dict(dash='dot')
                        ))
                    
                    fig.update_layout(
                        title=f"{CRYPTO_MAPPING[ticker]} Technical Indicators",
                        xaxis_title='Date',
                        yaxis_title='Price (USD)',
                        template='plotly_white'
                    )
                    
                    img_path = f"temp_{ticker}_indicators.png"
                    fig.write_image(img_path, width=1000, height=600)
                    slide.shapes.add_picture(img_path, Inches(0.5), Inches(1.5), height=Inches(5))
                    
                except Exception as indicators_error:
                    logger.error(f"Technical indicators slide failed: {str(indicators_error)}")

            # Add trading signals slide if we have signals data
            if not signals_df.empty and 'Close' in signals_df.columns:
                try:
                    slide = prs.slides.add_slide(prs.slide_layouts[1])
                    title = slide.shapes.title
                    title.text = "Trading Signals"
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=signals_df.index, 
                        y=signals_df['Close'], 
                        name='Price'
                    ))
                    
                    if 'Composite_Signal' in signals_df.columns:
                        buy_signals = signals_df[signals_df['Composite_Signal'] > 0.3]
                        sell_signals = signals_df[signals_df['Composite_Signal'] < -0.3]
                        
                        fig.add_trace(go.Scatter(
                            x=buy_signals.index,
                            y=buy_signals['Close'],
                            mode='markers',
                            marker=dict(color='green', size=10),
                            name='Buy Signal'
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=sell_signals.index,
                            y=sell_signals['Close'],
                            mode='markers',
                            marker=dict(color='red', size=10),
                            name='Sell Signal'
                        ))
                    
                    fig.update_layout(
                        title=f"{CRYPTO_MAPPING[ticker]} Trading Signals",
                        xaxis_title='Date',
                        yaxis_title='Price (USD)',
                        template='plotly_white'
                    )
                    
                    img_path = f"temp_{ticker}_signals.png"
                    fig.write_image(img_path, width=1000, height=600)
                    slide.shapes.add_picture(img_path, Inches(0.5), Inches(1.5), height=Inches(5))
                    
                except Exception as signals_error:
                    logger.error(f"Trading signals slide failed: {str(signals_error)}")

            # Add sentiment analysis slide if we have sentiment data
            if not sentiment_df.empty and 'vader_score' in sentiment_df.columns:
                try:
                    slide = prs.slides.add_slide(prs.slide_layouts[1])
                    title = slide.shapes.title
                    title.text = "Sentiment Analysis"
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=sentiment_df['date'],
                        y=sentiment_df['vader_score'].rolling(7).mean(),
                        name='VADER (7-day MA)'
                    ))
                    
                    if 'textblob_polarity' in sentiment_df.columns:
                        fig.add_trace(go.Scatter(
                            x=sentiment_df['date'],
                            y=sentiment_df['textblob_polarity'].rolling(7).mean(),
                            name='TextBlob (7-day MA)'
                        ))
                    
                    fig.update_layout(
                        title=f"{CRYPTO_MAPPING[ticker]} Sentiment Trend",
                        xaxis_title='Date',
                        yaxis_title='Sentiment Score',
                        template='plotly_white'
                    )
                    
                    img_path = f"temp_{ticker}_sentiment.png"
                    fig.write_image(img_path, width=1000, height=400)
                    slide.shapes.add_picture(img_path, Inches(0.5), Inches(1.5), height=Inches(4))
                    
                    # Add sentiment metrics
                    avg_sentiment = {
                        'VADER': sentiment_df['vader_score'].mean(),
                        'TextBlob': sentiment_df.get('textblob_polarity', pd.Series([0])).mean()
                    }
                    
                    textbox = slide.shapes.add_textbox(Inches(0.5), Inches(5), Inches(4), Inches(1.5))
                    tf = textbox.text_frame
                    
                    p = tf.add_paragraph()
                    p.text = "Average Sentiment Scores:"
                    p.font.bold = True
                    p.font.size = Pt(14)
                    
                    p = tf.add_paragraph()
                    p.text = f"VADER: {avg_sentiment['VADER']:.2f} (Positive)" if avg_sentiment['VADER'] > 0 else f"VADER: {avg_sentiment['VADER']:.2f} (Negative)"
                    
                    if 'textblob_polarity' in sentiment_df.columns:
                        p = tf.add_paragraph()
                        p.text = f"TextBlob: {avg_sentiment['TextBlob']:.2f} (Positive)" if avg_sentiment['TextBlob'] > 0 else f"TextBlob: {avg_sentiment['TextBlob']:.2f} (Negative)"
                        
                except Exception as sentiment_error:
                    logger.error(f"Sentiment analysis slide failed: {str(sentiment_error)}")

            # Add recommendation slide
            try:
                slide = prs.slides.add_slide(prs.slide_layouts[1])
                title = slide.shapes.title
                title.text = "Recommendations"
                
                # Initialize recommendation text
                textbox = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(9), Inches(5))
                tf = textbox.text_frame
                
                # Try to generate prediction if we have the model and data
                if (not data.empty and 'Close' in data.columns and 
                    ticker in self.analyzer.models and 
                    ticker in self.analyzer.scalers):
                    
                    try:
                        lookback = 90
                        close_prices = data['Close'].copy()
                        close_prices.name = ticker
                        X, y = self.analyzer.preprocess_data(close_prices, lookback)
                        last_seq = X[-1].reshape(1, lookback, 1)
                        
                        pred, lower, upper, std = self.analyzer.monte_carlo_prediction(
                            self.analyzer.models[ticker], 
                            last_seq, 
                            self.analyzer.scalers[ticker], 
                            200
                        )
                        
                        last_price = data['Close'].iloc[-1]
                        direction = "up" if pred > last_price else "down"
                        change_pct = abs(pred / last_price - 1) * 100
                        
                        p = tf.add_paragraph()
                        p.text = "Price Forecast:"
                        p.font.bold = True
                        p.font.size = Pt(16)
                        
                        p = tf.add_paragraph()
                        p.text = f"Current Price: ${last_price:,.2f}"
                        p.font.size = Pt(14)
                        
                        p = tf.add_paragraph()
                        p.text = f"Predicted Price: ${pred:,.2f} ({direction.capitalize()} {change_pct:.2f}%)"
                        p.font.size = Pt(14)
                        
                        p = tf.add_paragraph()
                        p.text = f"Confidence Interval: ${lower:,.2f} - ${upper:,.2f}"
                        p.font.size = Pt(14)
                        
                        p = tf.add_paragraph()
                        p.text = "\nTrading Recommendation:"
                        p.font.bold = True
                        p.font.size = Pt(16)
                        
                        if direction == "up":
                            p = tf.add_paragraph()
                            p.text = "BUY SIGNAL - Predicted price increase"
                            p.font.color.rgb = RGBColor(0, 128, 0)
                            p.font.size = Pt(18)
                            
                            for bullet in [
                                "• Consider accumulating positions",
                                f"• Entry point below ${lower:,.2f} provides favorable risk/reward",
                                f"• Recommended stop-loss at ${max(lower*0.95, last_price*0.97):,.2f}"
                            ]:
                                p = tf.add_paragraph()
                                p.text = bullet
                        else:
                            p = tf.add_paragraph()
                            p.text = "SELL SIGNAL - Predicted price decrease"
                            p.font.color.rgb = RGBColor(255, 0, 0)
                            p.font.size = Pt(18)
                            
                            for bullet in [
                                "• Consider reducing exposure",
                                f"• Exit point above ${upper:,.2f} may provide better prices",
                                f"• Set stop-loss at ${min(upper*1.05, last_price*1.03):,.2f}"
                            ]:
                                p = tf.add_paragraph()
                                p.text = bullet
                                
                    except Exception as prediction_error:
                        logger.error(f"Prediction failed: {str(prediction_error)}")
                        p = tf.add_paragraph()
                        p.text = "Could not generate price prediction"
                        p.font.color.rgb = RGBColor(255, 0, 0)
                else:
                    p = tf.add_paragraph()
                    p.text = "Insufficient data to generate recommendations"
                    p.font.size = Pt(14)
                    
            except Exception as recommendation_error:
                logger.error(f"Recommendation slide failed: {str(recommendation_error)}")

            # Add disclaimer slide
            try:
                slide = prs.slides.add_slide(prs.slide_layouts[1])
                title = slide.shapes.title
                title.text = "Disclaimer"
                
                textbox = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(8), Inches(4))
                tf = textbox.text_frame
                
                p = tf.add_paragraph()
                p.text = "Important Notice:"
                p.font.bold = True
                p.font.size = Pt(16)
                
                p = tf.add_paragraph()
                p.text = "This report is for informational purposes only and should not be considered as financial advice. Cryptocurrency markets are highly volatile and investing carries risks. Always conduct your own research before making any investment decisions."
                p.font.size = Pt(12)
                
                p = tf.add_paragraph()
                p.text = "\nData Sources:"
                p.font.bold = True
                p.font.size = Pt(14)
                
                p = tf.add_paragraph()
                p.text = "• Yahoo Finance\n• Binance API\n• Reddit (for sentiment analysis)\n• Various technical indicators"
                p.font.size = Pt(12)
                
            except Exception as disclaimer_error:
                logger.error(f"Disclaimer slide failed: {str(disclaimer_error)}")

            # Save presentation with unique filename
            report_dir = "reports"
            os.makedirs(report_dir, exist_ok=True)
            report_path = os.path.join(
                report_dir,
                f"{CRYPTO_MAPPING[ticker]}_Analysis_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
            )
            
            try:
                prs.save(report_path)
                logger.info(f"Successfully saved report to {report_path}")
            except Exception as save_error:
                logger.error(f"Failed to save presentation: {str(save_error)}")
                raise RuntimeError(f"Failed to save presentation: {str(save_error)}")
            
            # Clean up temp files
            for temp_file in glob.glob(f"temp_{ticker}_*.png"):
                try:
                    os.remove(temp_file)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to remove temp file {temp_file}: {str(cleanup_error)}")
            
            return report_path
            
        except Exception as main_error:
            logger.error(f"Failed to generate report: {str(main_error)}")
            raise RuntimeError(f"Report generation failed: {str(main_error)}")
            
            try:
                from pptx.util import Inches, Pt
                from pptx.dml.color import RGBColor
                import glob
                import os

                # Create presentation
                prs = Presentation()
                
                # Add title slide
                slide = prs.slides.add_slide(prs.slide_layouts[0])
                title = slide.shapes.title
                subtitle = slide.placeholders[1]
                
                title.text = f"{CRYPTO_MAPPING[ticker]} Analysis Report"
                subtitle.text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}\nCrypto Intelligence Platform"

                # Get all data needed with proper alignment handling
                try:
                    data = self.analyzer.fetch_market_data(ticker, period="5y")
                    if data.empty:
                        raise ValueError("No data returned for the specified ticker")
                        
                    # Ensure proper alignment of columns before calculations
                    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                    if not all(col in data.columns for col in required_cols):
                        missing = [col for col in required_cols if col not in data.columns]
                        raise ValueError(f"Missing required columns: {missing}")

                    # Align data before generating signals
                    signals_df = self.analyzer.generate_trading_signals(data.copy())
                    
                    # Check signal columns are aligned
                    if 'Composite_Signal' not in signals_df.columns:
                        raise ValueError("Failed to generate trading signals")

                    metrics = self.analyzer.get_coin_metrics(ticker)
                    sentiment_df = self.analyzer.fetch_news_sentiment(CRYPTO_MAPPING[ticker])
                    
                except Exception as e:
                    logger.error(f"Data preparation failed: {str(e)}")
                    raise

                # Add overview slide
                slide = prs.slides.add_slide(prs.slide_layouts[1])
                title = slide.shapes.title
                title.text = "Key Metrics Overview"
                
                # Create table for metrics with error handling
                try:
                    rows = 8
                    cols = 2
                    table = slide.shapes.add_table(rows, cols, Inches(1), Inches(1.5), Inches(8), Inches(4)).table
                    
                    # Format table
                    table.columns[0].width = Inches(3)
                    table.columns[1].width = Inches(3)
                    
                    # Add headers
                    table.cell(0, 0).text = "Metric"
                    table.cell(0, 1).text = "Value"
                    
                    # Fill metrics with fallbacks
                    metrics_data = [
                        ("Current Price", f"${data['Close'].iloc[-1]:,.2f}"),
                        ("Volatility", f"{metrics.get('volatility', 'N/A')}"),
                        ("Momentum", f"{metrics.get('momentum', 'N/A')}"),
                        ("Sharpe Ratio", f"{metrics.get('sharpe', 'N/A')}"),
                        ("Max Drawdown", f"{metrics.get('max_drawdown', 'N/A')}"),
                        ("BTC Correlation", f"{metrics.get('btc_correlation', 'N/A')}"),
                        ("Market Regime", metrics.get('market_regime', 'N/A')),
                        ("RSI", f"{metrics.get('rsi', 'N/A')}")
                    ]
                    
                    for i, (metric, value) in enumerate(metrics_data, start=1):
                        table.cell(i, 0).text = metric
                        table.cell(i, 1).text = str(value)  # Ensure string conversion
                        
                    # Style table
                    for cell in table.iter_cells():
                        for paragraph in cell.text_frame.paragraphs:
                            paragraph.font.size = Pt(12)
                            paragraph.font.name = 'Calibri'
                            
                except Exception as e:
                    logger.error(f"Metrics table generation failed: {str(e)}")
                    # Add error message slide if metrics fail
                    slide = prs.slides.add_slide(prs.slide_layouts[1])
                    title = slide.shapes.title
                    title.text = "Metrics Unavailable"
                    textbox = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(8), Inches(2))
                    tf = textbox.text_frame
                    p = tf.add_paragraph()
                    p.text = "Could not generate metrics table due to data issues"
                    p.font.color.rgb = RGBColor(255, 0, 0)

                # Add price chart slide
                try:
                    slide = prs.slides.add_slide(prs.slide_layouts[1])
                    title = slide.shapes.title
                    title.text = "Price History"
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=data.index, 
                        y=data['Close'], 
                        name='Price',
                        line=dict(color='#1f77b4')
                    ))
                    fig.update_layout(
                        title=f"{CRYPTO_MAPPING[ticker]} Price History",
                        xaxis_title='Date',
                        yaxis_title='Price (USD)',
                        template='plotly_white'
                    )
                    
                    img_path = f"temp_{ticker}_price.png"
                    fig.write_image(img_path, width=1000, height=600)
                    slide.shapes.add_picture(img_path, Inches(0.5), Inches(1.5), height=Inches(5))
                    
                except Exception as e:
                    logger.error(f"Price chart generation failed: {str(e)}")

                # Add technical indicators slide (only if indicators exist)
                try:
                    if all(col in data.columns for col in ['MA_20', 'MA_50', 'BB_upper', 'BB_lower']):
                        slide = prs.slides.add_slide(prs.slide_layouts[1])
                        title = slide.shapes.title
                        title.text = "Technical Indicators"
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Price'))
                        
                        # Only add indicators that exist
                        if 'MA_20' in data.columns:
                            fig.add_trace(go.Scatter(x=data.index, y=data['MA_20'], name='20-day MA'))
                        if 'MA_50' in data.columns:
                            fig.add_trace(go.Scatter(x=data.index, y=data['MA_50'], name='50-day MA'))
                        if all(col in data.columns for col in ['BB_upper', 'BB_lower']):
                            fig.add_trace(go.Scatter(
                                x=data.index, y=data['BB_upper'], 
                                name='BB Upper', line=dict(dash='dot')
                            ))
                            fig.add_trace(go.Scatter(
                                x=data.index, y=data['BB_lower'], 
                                name='BB Lower', line=dict(dash='dot')
                            ))
                        
                        fig.update_layout(
                            title=f"{CRYPTO_MAPPING[ticker]} Technical Indicators",
                            xaxis_title='Date',
                            yaxis_title='Price (USD)',
                            template='plotly_white'
                        )
                        
                        img_path = f"temp_{ticker}_indicators.png"
                        fig.write_image(img_path, width=1000, height=600)
                        slide.shapes.add_picture(img_path, Inches(0.5), Inches(1.5), height=Inches(5))
                        
                except Exception as e:
                    logger.error(f"Technical indicators slide failed: {str(e)}")

                # Add trading signals slide
                try:
                    slide = prs.slides.add_slide(prs.slide_layouts[1])
                    title = slide.shapes.title
                    title.text = "Trading Signals"
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=signals_df.index, 
                        y=signals_df['Close'], 
                        name='Price'
                    ))
                    
                    if 'Composite_Signal' in signals_df.columns:
                        buy_signals = signals_df[signals_df['Composite_Signal'] > 0.3]
                        sell_signals = signals_df[signals_df['Composite_Signal'] < -0.3]
                        
                        fig.add_trace(go.Scatter(
                            x=buy_signals.index,
                            y=buy_signals['Close'],
                            mode='markers',
                            marker=dict(color='green', size=10),
                            name='Buy Signal'
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=sell_signals.index,
                            y=sell_signals['Close'],
                            mode='markers',
                            marker=dict(color='red', size=10),
                            name='Sell Signal'
                        ))
                    
                    fig.update_layout(
                        title=f"{CRYPTO_MAPPING[ticker]} Trading Signals",
                        xaxis_title='Date',
                        yaxis_title='Price (USD)',
                        template='plotly_white'
                    )
                    
                    img_path = f"temp_{ticker}_signals.png"
                    fig.write_image(img_path, width=1000, height=600)
                    slide.shapes.add_picture(img_path, Inches(0.5), Inches(1.5), height=Inches(5))
                    
                except Exception as e:
                    logger.error(f"Trading signals slide failed: {str(e)}")

                # Add sentiment analysis slide if data exists
                try:
                    if not sentiment_df.empty and 'vader_score' in sentiment_df.columns:
                        slide = prs.slides.add_slide(prs.slide_layouts[1])
                        title = slide.shapes.title
                        title.text = "Sentiment Analysis"
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=sentiment_df['date'],
                            y=sentiment_df['vader_score'].rolling(7).mean(),
                            name='VADER (7-day MA)'
                        ))
                        
                        if 'textblob_polarity' in sentiment_df.columns:
                            fig.add_trace(go.Scatter(
                                x=sentiment_df['date'],
                                y=sentiment_df['textblob_polarity'].rolling(7).mean(),
                                name='TextBlob (7-day MA)'
                            ))
                        
                        fig.update_layout(
                            title=f"{CRYPTO_MAPPING[ticker]} Sentiment Trend",
                            xaxis_title='Date',
                            yaxis_title='Sentiment Score',
                            template='plotly_white'
                        )
                        
                        img_path = f"temp_{ticker}_sentiment.png"
                        fig.write_image(img_path, width=1000, height=400)
                        slide.shapes.add_picture(img_path, Inches(0.5), Inches(1.5), height=Inches(4))
                        
                        # Add sentiment metrics
                        avg_sentiment = {
                            'VADER': sentiment_df['vader_score'].mean(),
                            'TextBlob': sentiment_df.get('textblob_polarity', pd.Series([0])).mean()
                        }
                        
                        textbox = slide.shapes.add_textbox(Inches(0.5), Inches(5), Inches(4), Inches(1.5))
                        tf = textbox.text_frame
                        
                        p = tf.add_paragraph()
                        p.text = "Average Sentiment Scores:"
                        p.font.bold = True
                        p.font.size = Pt(14)
                        
                        p = tf.add_paragraph()
                        p.text = f"VADER: {avg_sentiment['VADER']:.2f} (Positive)" if avg_sentiment['VADER'] > 0 else f"VADER: {avg_sentiment['VADER']:.2f} (Negative)"
                        
                        if 'textblob_polarity' in sentiment_df.columns:
                            p = tf.add_paragraph()
                            p.text = f"TextBlob: {avg_sentiment['TextBlob']:.2f} (Positive)" if avg_sentiment['TextBlob'] > 0 else f"TextBlob: {avg_sentiment['TextBlob']:.2f} (Negative)"
                            
                except Exception as e:
                    logger.error(f"Sentiment analysis slide failed: {str(e)}")

                # Add recommendation slide
                try:
                    slide = prs.slides.add_slide(prs.slide_layouts[1])
                    title = slide.shapes.title
                    title.text = "Recommendations"
                    
                    # Get prediction with proper error handling
                    try:
                        lookback = 90
                        close_prices = data['Close'].copy()
                        close_prices.name = ticker
                        X, y = self.analyzer.preprocess_data(close_prices, lookback)
                        last_seq = X[-1].reshape(1, lookback, 1)
                        
                        pred, lower, upper, std = self.analyzer.monte_carlo_prediction(
                            self.analyzer.models.get(ticker), 
                            last_seq, 
                            self.analyzer.scalers[ticker], 
                            200
                        )
                        
                        last_price = data['Close'].iloc[-1]
                        direction = "up" if pred > last_price else "down"
                        change_pct = abs(pred / last_price - 1) * 100
                        
                        textbox = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(9), Inches(5))
                        tf = textbox.text_frame
                        
                        p = tf.add_paragraph()
                        p.text = "Price Forecast:"
                        p.font.bold = True
                        p.font.size = Pt(16)
                        
                        p = tf.add_paragraph()
                        p.text = f"Current Price: ${last_price:,.2f}"
                        p.font.size = Pt(14)
                        
                        p = tf.add_paragraph()
                        p.text = f"Predicted Price: ${pred:,.2f} ({direction.capitalize()} {change_pct:.2f}%)"
                        p.font.size = Pt(14)
                        
                        p = tf.add_paragraph()
                        p.text = f"Confidence Interval: ${lower:,.2f} - ${upper:,.2f}"
                        p.font.size = Pt(14)
                        
                        p = tf.add_paragraph()
                        p.text = "\nTrading Recommendation:"
                        p.font.bold = True
                        p.font.size = Pt(16)
                        
                        if direction == "up":
                            p = tf.add_paragraph()
                            p.text = "BUY SIGNAL - Predicted price increase"
                            p.font.color.rgb = RGBColor(0, 128, 0)
                            p.font.size = Pt(18)
                            
                            for bullet in [
                                "• Consider accumulating positions",
                                f"• Entry point below ${lower:,.2f} provides favorable risk/reward",
                                f"• Recommended stop-loss at ${max(lower*0.95, last_price*0.97):,.2f}"
                            ]:
                                p = tf.add_paragraph()
                                p.text = bullet
                        else:
                            p = tf.add_paragraph()
                            p.text = "SELL SIGNAL - Predicted price decrease"
                            p.font.color.rgb = RGBColor(255, 0, 0)
                            p.font.size = Pt(18)
                            
                            for bullet in [
                                "• Consider reducing exposure",
                                f"• Exit point above ${upper:,.2f} may provide better prices",
                                f"• Set stop-loss at ${min(upper*1.05, last_price*1.03):,.2f}"
                            ]:
                                p = tf.add_paragraph()
                                p.text = bullet
                                
                    except Exception as e:
                        logger.error(f"Prediction failed: {str(e)}")
                        textbox = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(8), Inches(2))
                        tf = textbox.text_frame
                        p = tf.add_paragraph()
                        p.text = "Could not generate price prediction"
                        p.font.color.rgb = RGBColor(255, 0, 0)
                        
                except Exception as e:
                    logger.error(f"Recommendation slide failed: {str(e)}")

                # Add disclaimer slide
                try:
                    slide = prs.slides.add_slide(prs.slide_layouts[1])
                    title = slide.shapes.title
                    title.text = "Disclaimer"
                    
                    textbox = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(8), Inches(4))
                    tf = textbox.text_frame
                    
                    p = tf.add_paragraph()
                    p.text = "Important Notice:"
                    p.font.bold = True
                    p.font.size = Pt(16)
                    
                    p = tf.add_paragraph()
                    p.text = "This report is for informational purposes only and should not be considered as financial advice. Cryptocurrency markets are highly volatile and investing carries risks. Always conduct your own research before making any investment decisions."
                    p.font.size = Pt(12)
                    
                    p = tf.add_paragraph()
                    p.text = "\nData Sources:"
                    p.font.bold = True
                    p.font.size = Pt(14)
                    
                    p = tf.add_paragraph()
                    p.text = "• Yahoo Finance\n• Binance API\n• Reddit (for sentiment analysis)\n• Various technical indicators"
                    p.font.size = Pt(12)
                    
                except Exception as e:
                    logger.error(f"Disclaimer slide failed: {str(e)}")

                # Save presentation with unique filename
                report_dir = "reports"
                os.makedirs(report_dir, exist_ok=True)
                report_path = os.path.join(
                    report_dir,
                    f"{CRYPTO_MAPPING[ticker]}_Analysis_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
                )
                
                prs.save(report_path)
                
                # Clean up temp files
                for temp_file in glob.glob(f"temp_{ticker}_*.png"):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                
                return report_path
                
            except Exception as e:
                logger.error(f"Failed to generate report: {str(e)}")
            raise RuntimeError(f"Report generation failed: {str(e)}")