import streamlit as st
from Simulations import CryptoDashboard
import os
import glob
from datetime import datetime
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
import plotly.graph_objects as go  # Assuming your class is in crypto_dashboard.py

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
    
    # Add the PowerPoint report button (new addition)
    st.sidebar.markdown("---")  # Add a separator
    if st.sidebar.button("📊 Generate Full Report (PPTX)"):
        with st.spinner("Generating comprehensive PowerPoint report..."):
            try:
                report_path = dashboard.generate_pptx_report(analyzer=self.analyzer, ticker="BTC-USD", crypto_mapping=CRYPTO_MAPPING)
                st.success(f"Report generated successfully: {report_path}")
                with open(report_path, "rb") as f:
                    st.sidebar.download_button(
                        label="⬇️ Download Report",
                        data=f,
                        file_name=report_path.split("/")[-1],
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    )
                st.sidebar.success("Report generated successfully!")
            except Exception as e:
                st.sidebar.error(f"Failed to generate report: {str(e)}")

if __name__ == "__main__":
    main()