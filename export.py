import streamlit as st
import pandas as pd

def export_csv(price_df, social_df):
    csv = price_df.to_csv(index=False)
    st.download_button("Download Price Data CSV", csv, file_name="price_data.csv", mime="text/csv")

def export_pdf(price_df, social_df):
    st.write("🚧 PDF export coming soon (requires ReportLab setup)")
    # I can implement if you want 📄
