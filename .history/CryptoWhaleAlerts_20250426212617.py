import streamlit as st
import random
import time

def show_simulated_whale_alerts():
    st.title("🐋 Simulated Whale Transaction Alerts")

    simulated_data = [
        {"amount": random.randint(500000, 5000000), "currency": "BTC", "from": "Unknown Wallet", "to": "Binance"},
        {"amount": random.randint(600000, 4000000), "currency": "ETH", "from": "Coinbase", "to": "Private Wallet"},
        {"amount": random.randint(800000, 7000000), "currency": "USDT", "from": "Huobi", "to": "Bitfinex"},
    ]

    if st.button("🔄 Generate Whale Alerts"):
        with st.spinner("Scanning blockchain..."):
            time.sleep(2)  # simulate network delay
            for tx in simulated_data:
                st.warning(f"Whale Alert: {tx['amount']} {tx['currency']} from {tx['from']} ➔ {tx['to']}")
            st.success("✅ Simulated scan complete!")
