# --- whale_alert.py ---

import streamlit as st
import requests

# Free Whale Alert API (or simulate)
API_URL = "https://api.whale-alert.io/v1/transactions?api_key=YOUR_API_KEY&min_value=500000&currency=usd"

def show_whale_alerts():
    st.title("🐋 Crypto Whale Transaction Alerts")

    st.info("Tracking movements over **$500,000+** in real-time...")

    if st.button("🔄 Refresh Alerts"):
        try:
            response = requests.get(API_URL)
            if response.status_code == 200:
                data = response.json()
                transactions = data.get("transactions", [])
                if transactions:
                    for tx in transactions:
                        st.warning(f"Whale Move: {tx['amount']} {tx['currency']} from {tx['from']['owner_type']} ➔ {tx['to']['owner_type']}")
                else:
                    st.success("No recent whale transactions detected.")
            else:
                st.error("Error fetching whale alerts (Check API Key or try later)")
        except Exception as e:
            st.error(f"Error: {e}")
