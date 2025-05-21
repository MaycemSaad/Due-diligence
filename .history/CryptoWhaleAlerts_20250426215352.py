# --- whale_alerts.py ---

import streamlit as st
import random
import time

def show_whale_alerts():
    st.title("🐋 Crypto Whale Transaction Alerts (Simulated)")

    st.subheader("Get notified about large simulated crypto movements!")
    st.markdown("---")

    # Simulated whale transaction database
    simulated_data = [
        {"amount": random.randint(500000, 2000000), "currency": "BTC", "from": "Unknown Wallet", "to": "Binance"},
        {"amount": random.randint(1000000, 3000000), "currency": "ETH", "from": "Coinbase", "to": "Private Wallet"},
        {"amount": random.randint(750000, 2500000), "currency": "USDT", "from": "Huobi", "to": "Bitfinex"},
        {"amount": random.randint(800000, 2800000), "currency": "BNB", "from": "Kraken", "to": "Cold Wallet"},
        {"amount": random.randint(900000, 4000000), "currency": "XRP", "from": "Unknown Wallet", "to": "OKX"},
    ]

    # Button to simulate whale alerts
    if st.button("🔄 Generate Whale Alerts"):
        with st.spinner("🚀 Scanning simulated blockchain movements..."):
            time.sleep(2)  # small delay to simulate 'live' feel

            for tx in simulated_data:
                amount_formatted = f"{tx['amount']:,}"
                st.warning(
                    f"🐋 Whale Alert: {amount_formatted} {tx['currency']} moved from **{tx['from']}** ➔ **{tx['to']}**"
                )

            st.success("✅ Simulated scan complete!")

