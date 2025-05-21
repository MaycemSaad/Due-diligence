import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import norm, t
from statsmodels.tsa.arima.model import ARIMA
from copulae import GaussianCopula
from riskfolio import RiskFunctions
import json
import base64
from datetime import datetime, timedelta

# Configuration
st.set_page_config(layout="wide", page_title="Institutional Crypto Risk Platform")
st.title("🚀 Institutional Crypto Risk Platform")
st.markdown("""
**Advanced Portfolio Stress Testing & Monte Carlo Simulation**  
*Institutional-grade risk analytics for crypto assets*
""")

# ========== Portfolio Simulation ==========
st.sidebar.header("Portfolio Configuration")
assets = st.sidebar.multiselect(
    "Select Assets", 
    ["BTC", "ETH", "SOL", "AVAX", "BNB", "XRP", "ADA", "DOT"],
    default=["BTC", "ETH", "SOL"]
)

weights = []
for i, asset in enumerate(assets):
    w = st.sidebar.slider(f"Weight {asset}", 0.0, 1.0, 1.0/len(assets))
    weights.append(w)
weights = np.array(weights) / sum(weights)  # Normalize

# ========== Advanced Parameters ==========
expander = st.sidebar.expander("Advanced Parameters")
with expander:
    n_simulations = st.number_input("Number of Simulations", 100, 10000, 5000)
    time_horizon = st.number_input("Time Horizon (days)", 7, 365, 30)
    confidence_level = st.number_input("Confidence Level", 0.85, 0.99, 0.95)
    use_t_dist = st.checkbox("Use Student-t Distribution", True)
    include_jumps = st.checkbox("Include Jump Diffusion", False)
    copula_type = st.selectbox("Dependency Structure", ["Gaussian", "t-Copula", "Clayton"])

# ========== Historical Data Simulation ==========
@st.cache_data
def simulate_crypto_data(assets, days=365):
    """Generate realistic synthetic crypto data"""
    np.random.seed(42)
    dates = pd.date_range(end=datetime.today(), periods=days)
    
    # Base parameters for BTC
    params = {
        "BTC": {"mu": 0.001, "sigma": 0.04, "jump_prob": 0.05, "jump_size": 0.1},
        "ETH": {"mu": 0.0012, "sigma": 0.05, "jump_prob": 0.06, "jump_size": 0.12},
        "SOL": {"mu": 0.0015, "sigma": 0.07, "jump_prob": 0.08, "jump_size": 0.15},
        "AVAX": {"mu": 0.0018, "sigma": 0.08, "jump_prob": 0.1, "jump_size": 0.2},
        "BNB": {"mu": 0.001, "sigma": 0.06, "jump_prob": 0.07, "jump_size": 0.15},
        "XRP": {"mu": 0.0008, "sigma": 0.09, "jump_prob": 0.12, "jump_size": 0.25},
        "ADA": {"mu": 0.0007, "sigma": 0.1, "jump_prob": 0.15, "jump_size": 0.3},
        "DOT": {"mu": 0.0009, "sigma": 0.085, "jump_prob": 0.1, "jump_size": 0.22}
    }
    
    data = {}
    for asset in assets:
        p = params.get(asset, params["BTC"])
        returns = np.random.normal(p["mu"], p["sigma"], days)
        
        if include_jumps:
            jumps = np.random.binomial(1, p["jump_prob"], days) * \
                   np.random.normal(0, p["jump_size"], days)
            returns += jumps
        
        prices = 100 * np.exp(np.cumsum(returns))
        data[asset] = pd.Series(prices, index=dates)
    
    return pd.DataFrame(data)

# ========== Monte Carlo Simulation Engine ==========
def monte_carlo_sim(returns, weights, n_simulations, time_horizon):
    """Advanced Monte Carlo simulation with copulas"""
    # Calculate portfolio statistics
    cov_matrix = returns.cov()
    corr_matrix = returns.corr()
    mean_returns = returns.mean()
    
    # Generate correlated random numbers
    if copula_type == "Gaussian":
        copula = GaussianCopula(dim=len(assets))
        copula.fit(returns)
        sim_returns = copula.random(n_simulations * time_horizon)
    else:
        # Fallback to Cholesky decomposition
        L = np.linalg.cholesky(corr_matrix)
        uncorrelated = norm.rvs(size=(time_horizon * n_simulations, len(assets)))
        sim_returns = uncorrelated @ L.T
    
    # Reshape and apply statistics
    sim_returns = sim_returns.reshape(n_simulations, time_horizon, len(assets))
    sim_returns = sim_returns * returns.std().values + returns.mean().values
    
    # Calculate portfolio paths
    portfolio_paths = np.zeros((n_simulations, time_horizon + 1))
    portfolio_paths[:, 0] = 100  # Starting value
    
    for i in range(n_simulations):
        for t in range(1, time_horizon + 1):
            portfolio_return = np.dot(weights, sim_returns[i, t-1])
            portfolio_paths[i, t] = portfolio_paths[i, t-1] * (1 + portfolio_return)
    
    return portfolio_paths, sim_returns

# ========== Risk Metrics ==========
def calculate_risk_metrics(paths):
    """Calculate advanced risk metrics"""
    final_values = paths[:, -1]
    returns = (final_values / 100) - 1  # Percentage returns
    
    metrics = {
        "Expected Return": np.mean(returns),
        "Volatility": np.std(returns),
        "Sharpe Ratio": np.mean(returns) / np.std(returns),
        "Sortino Ratio": RiskFunctions.SortinoRatio(returns),
        "Max Drawdown": RiskFunctions.MaxDrawDown(returns),
        "VaR 95%": RiskFunctions.VaR_Hist(returns, alpha=0.05),
        "CVaR 95%": RiskFunctions.CVaR_Hist(returns, alpha=0.05),
        "Best Case": np.max(returns),
        "Worst Case": np.min(returns),
        "Probability of Loss": len(returns[returns < 0]) / len(returns)
    }
    
    return metrics

# ========== Run Simulation ==========
if st.sidebar.button("Run Advanced Simulation"):
    with st.spinner("Running institutional-grade simulation..."):
        # Get historical data
        df = simulate_crypto_data(assets)
        returns = df.pct_change().dropna()
        
        # Run Monte Carlo
        portfolio_paths, asset_sims = monte_carlo_sim(
            returns, weights, n_simulations, time_horizon
        )
        
        # Calculate metrics
        metrics = calculate_risk_metrics(portfolio_paths)
        
        # ========== Visualization ==========
        st.success("Simulation Completed!")
        
        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Portfolio Simulation", 
            "📈 Asset Correlations", 
            "🛡️ Risk Metrics", 
            "📄 Full Report"
        ])
        
        with tab1:
            # Portfolio paths visualization
            fig = go.Figure()
            
            # Add percentiles
            percentiles = np.percentile(portfolio_paths, [5, 25, 50, 75, 95], axis=0)
            dates = pd.date_range(start=datetime.today(), periods=time_horizon+1)
            
            fig.add_trace(go.Scatter(
                x=dates, y=percentiles[2],
                mode='lines',
                name='Median',
                line=dict(color='blue', width=3)
            ))
            
            fig.add_trace(go.Scatter(
                x=dates, y=percentiles[0],
                fill=None,
                mode='lines',
                line=dict(color='red', width=1),
                name='5th Percentile'
            ))
            
            fig.add_trace(go.Scatter(
                x=dates, y=percentiles[4],
                fill='tonexty',
                mode='lines',
                line=dict(color='green', width=1),
                name='95th Percentile'
            ))
            
            fig.update_layout(
                title='Portfolio Monte Carlo Simulation',
                xaxis_title='Date',
                yaxis_title='Portfolio Value',
                hovermode="x unified",
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show sample paths
            st.subheader("Sample Paths")
            sample_paths = pd.DataFrame(
                portfolio_paths[:10].T,
                index=dates
            )
            st.line_chart(sample_paths)
        
        with tab2:
            # Correlation matrix
            st.subheader("Asset Correlation Matrix")
            corr = returns.corr()
            
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.heatmap(corr, annot=True, cmap='coolwarm', center=0, ax=ax)
            st.pyplot(fig)
            
            # Dependency structure
            st.subheader("Dependency Structure")
            if copula_type == "Gaussian":
                st.write("Using Gaussian Copula for:")
                st.write("- Flexible dependency modeling")
                st.write("- Captures non-linear relationships")
            else:
                st.write("Using Cholesky Decomposition for:")
                st.write("- Linear correlation structure")
        
        with tab3:
            # Display metrics
            st.subheader("Portfolio Risk Metrics")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Expected Return", f"{metrics['Expected Return']:.2%}")
                st.metric("Annualized Volatility", f"{metrics['Volatility']*np.sqrt(365):.2%}")
                st.metric("Sharpe Ratio", f"{metrics['Sharpe Ratio']:.2f}")
                st.metric("Sortino Ratio", f"{metrics['Sortino Ratio']:.2f}")
            
            with col2:
                st.metric("VaR 95%", f"{metrics['VaR 95%']:.2%}")
                st.metric("CVaR 95%", f"{metrics['CVaR 95%']:.2%}")
                st.metric("Max Drawdown", f"{metrics['Max Drawdown']:.2%}")
                st.metric("Probability of Loss", f"{metrics['Probability of Loss']:.2%}")
            
            # Distribution plot
            st.subheader("Final Value Distribution")
            fig = go.Figure()
            final_values = portfolio_paths[:, -1]
            fig.add_trace(go.Histogram(
                x=final_values,
                nbinsx=50,
                name='Portfolio Value',
                marker_color='#1f77b4'
            ))
            fig.update_layout(
                xaxis_title='Portfolio Value',
                yaxis_title='Frequency',
                bargap=0.1
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab4:
            # Generate professional report
            st.subheader("Full Risk Report")
            
            # Create download button
            def create_report():
                report = {
                    "metadata": {
                        "date": str(datetime.now()),
                        "assets": assets,
                        "weights": list(weights),
                        "parameters": {
                            "simulations": n_simulations,
                            "horizon": time_horizon,
                            "confidence": confidence_level,
                            "copula": copula_type
                        }
                    },
                    "metrics": metrics,
                    "correlation_matrix": corr.values.tolist()
                }
                return json.dumps(report, indent=2)
            
            report_json = create_report()
            b64 = base64.b64encode(report_json.encode()).decode()
            href = f'<a href="data:application/json;base64,{b64}" download="crypto_risk_report.json">Download Full Report (JSON)</a>'
            st.markdown(href, unsafe_allow_html=True)
            
            # Display report preview
            with st.expander("Report Preview"):
                st.json(report_json)

# ========== API Documentation ==========
st.sidebar.markdown("---")
st.sidebar.header("API Access")
st.sidebar.markdown("---")
st.sidebar.header("API Access")
st.sidebar.markdown("""
### API Documentation

#### Authentication
```python
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}