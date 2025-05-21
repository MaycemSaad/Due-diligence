import streamlit as st
from  import CryptoDashboard  # Assuming your class is in crypto_dashboard.py

def main():
    # Initialize the dashboard
    dashboard = CryptoDashboard()
    
    # Render the header
    dashboard.render_header()
    
    # Get user selections from sidebar
    analysis_type, time_frame, show_raw = dashboard.render_sidebar()
    
    # Route to the appropriate analysis based on user selection
    if analysis_type == "Technical Analysis":
        dashboard.render_technical_analysis(dashboard.current_ticker, time_frame)
    elif analysis_type == "Price Forecast":
        dashboard.render_price_forecast(dashboard.current_ticker)
    elif analysis_type == "Sentiment Analysis":
        dashboard.render_sentiment_analysis(dashboard.current_ticker)
    elif analysis_type == "Trading Signals":
        dashboard.render_trading_signals(dashboard.current_ticker)

if __name__ == "__main__":
    main()