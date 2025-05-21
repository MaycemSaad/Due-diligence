import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import norm, t
from statsmodels.tsa.arima.model import ARIMA
from copulae import GaussianCopula, StudentCopula
import riskfolio as rp
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
import logging
from enum import Enum

# ---------------------- Configuration ----------------------
class CopulaType(Enum):
    GAUSSIAN = "Gaussian"
    STUDENT = "Student-t"
    CHOLESKY = "Cholesky"

# ---------------------- Data Classes ----------------------
@dataclass
class AssetParameters:
    mu: float
    sigma: float
    jump_prob: float = 0.0
    jump_size: float = 0.0
    nu: float = 5.0  # Degrees of freedom for Student-t

@dataclass
class SimulationParameters:
    n_simulations: int = 5000
    time_horizon: int = 30
    confidence_level: float = 0.95
    include_jumps: bool = False
    copula_type: CopulaType = CopulaType.GAUSSIAN
    initial_portfolio_value: float = 100.0

# ---------------------- Setup ----------------------
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamlit configuration
st.set_page_config(
    layout="wide", 
    page_title="Institutional Crypto Risk Platform",
    page_icon="📊"
)

# ---------------------- Constants ----------------------
ASSET_PARAMS = {
    "BTC": AssetParameters(mu=0.001, sigma=0.04, jump_prob=0.05, jump_size=0.1),
    "ETH": AssetParameters(mu=0.0012, sigma=0.05, jump_prob=0.06, jump_size=0.12),
    "SOL": AssetParameters(mu=0.0015, sigma=0.07, jump_prob=0.08, jump_size=0.15),
    "AVAX": AssetParameters(mu=0.0018, sigma=0.08, jump_prob=0.10, jump_size=0.20),
    "BNB": AssetParameters(mu=0.001, sigma=0.06, jump_prob=0.07, jump_size=0.15),
    "XRP": AssetParameters(mu=0.0008, sigma=0.09, jump_prob=0.12, jump_size=0.25),
    "ADA": AssetParameters(mu=0.0007, sigma=0.10, jump_prob=0.15, jump_size=0.30),
    "DOT": AssetParameters(mu=0.0009, sigma=0.085, jump_prob=0.10, jump_size=0.22)
}

# ---------------------- Helper Functions ----------------------
def validate_weights(weights: np.ndarray) -> bool:
    """Validate portfolio weights."""
    if np.any(weights < 0):
        st.error("Negative weights are not allowed.")
        return False
    if np.sum(weights) == 0:
        st.error("Total weights cannot be zero.")
        return False
    return True

def normalize_weights(weights: np.ndarray) -> np.ndarray:
    """Normalize weights to sum to 1."""
    return weights / np.sum(weights)

# ---------------------- Data Simulation ----------------------
@st.cache_data(show_spinner=False)
def simulate_crypto_data(
    assets: list,
    days: int = 365,
    params: Dict[str, AssetParameters] = ASSET_PARAMS,
    include_jumps: bool = False,
    random_seed: int = 42
) -> pd.DataFrame:
    """
    Simulate crypto asset prices using geometric Brownian motion with optional jumps.
    
    Args:
        assets: List of asset symbols to simulate
        days: Number of days to simulate
        params: Dictionary of asset parameters
        include_jumps: Whether to include jump diffusion
        random_seed: Random seed for reproducibility
        
    Returns:
        DataFrame with simulated prices
    """
    np.random.seed(random_seed)
    dates = pd.date_range(end=datetime.today(), periods=days)
    
    data = {}
    for asset in assets:
        if asset not in params:
            logger.warning(f"Parameters not found for {asset}, using BTC defaults")
            p = params["BTC"]
        else:
            p = params[asset]
            
        # Base returns (GBM)
        returns = np.random.normal(p.mu, p.sigma, days)
        
        # Add jumps if enabled
        if include_jumps:
            jumps = np.random.binomial(1, p.jump_prob, days) * np.random.normal(0, p.jump_size, days)
            returns += jumps
        
        # Convert to prices
        prices = 100 * np.exp(np.cumsum(returns))
        data[asset] = pd.Series(prices, index=dates)
    
    return pd.DataFrame(data)

# ---------------------- Monte Carlo Simulation ----------------------
def simulate_returns_with_copula(
    returns: pd.DataFrame,
    copula_type: CopulaType,
    n_simulations: int,
    time_horizon: int
) -> np.ndarray:
    """
    Simulate correlated returns using specified copula method.
    
    Args:
        returns: Historical returns DataFrame (must be pandas DataFrame for correlation)
        copula_type: Type of copula to use
        n_simulations: Number of simulations
        time_horizon: Simulation horizon in days
        
    Returns:
        Array of simulated returns (n_simulations x time_horizon x n_assets)
    """
    # Ensure we have a DataFrame for correlation calculation
    if not isinstance(returns, pd.DataFrame):
        raise ValueError("Input returns must be a pandas DataFrame")
        
    n_assets = returns.shape[1]
    corr_matrix = returns.corr().values  # Convert correlation matrix to numpy array
    
    try:
        if copula_type == CopulaType.GAUSSIAN and n_assets >= 2:
            copula = GaussianCopula(dim=n_assets)
            copula.fit(returns.values)
            sim_returns = copula.random(n_simulations * time_horizon)
        elif copula_type == CopulaType.STUDENT and n_assets >= 2:
            copula = StudentCopula(dim=n_assets)
            copula.fit(returns.values)
            sim_returns = copula.random(n_simulations * time_horizon)
        else:
            if n_assets < 2:
                logger.warning(f"{copula_type.value} copula requires ≥2 assets. Using Cholesky fallback.")
            L = np.linalg.cholesky(corr_matrix)
            uncorrelated = norm.rvs(size=(time_horizon * n_simulations, n_assets))
            sim_returns = uncorrelated @ L.T
            
    except Exception as e:
        logger.error(f"Copula simulation failed: {str(e)}. Falling back to Cholesky.")
        L = np.linalg.cholesky(corr_matrix)
        uncorrelated = norm.rvs(size=(time_horizon * n_simulations, n_assets))
        sim_returns = uncorrelated @ L.T
    
    # Reshape and scale returns
    sim_returns = sim_returns.reshape(n_simulations, time_horizon, n_assets)
    return sim_returns * returns.std().values + returns.mean().values

def monte_carlo_sim(
    returns: pd.DataFrame,
    weights: np.ndarray,
    params: SimulationParameters
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Run full Monte Carlo simulation for portfolio.
    
    Args:
        returns: Historical returns DataFrame
        weights: Portfolio weights
        params: Simulation parameters
        
    Returns:
        Tuple of (portfolio_paths, asset_returns)
    """
    # Convert returns to numpy array if needed
    returns_array = returns.values if isinstance(returns, pd.DataFrame) else returns
    
    # Simulate asset returns
    asset_returns = simulate_returns_with_copula(
        returns_array,
        params.copula_type,
        params.n_simulations,
        params.time_horizon
    )
    
    # Calculate portfolio paths (vectorized implementation)
    portfolio_paths = np.zeros((params.n_simulations, params.time_horizon + 1))
    portfolio_paths[:, 0] = params.initial_portfolio_value
    
    # Vectorized calculation of cumulative returns
    cumulative_returns = np.cumprod(1 + np.einsum('ijk,k->ij', asset_returns, weights), axis=1)
    portfolio_paths[:, 1:] = params.initial_portfolio_value * cumulative_returns
    
    return portfolio_paths, asset_returns


# ---------------------- Risk Metrics ----------------------
def calculate_risk_metrics(
    paths: np.ndarray,
    confidence_level: float = 0.95
) -> Dict[str, float]:
    """
    Calculate comprehensive risk metrics for simulation results.
    
    Args:
        paths: Array of portfolio paths
        confidence_level: Confidence level for VaR/CVaR
        
    Returns:
        Dictionary of risk metrics
    """
    final_values = paths[:, -1]
    returns = (final_values / paths[:, 0]) - 1
    
    # Basic statistics
    mean_return = np.mean(returns)
    std_return = np.std(returns)
    
    # Risk-adjusted ratios
    sharpe = mean_return / std_return if std_return > 0 else 0
    sortino = rp.SortinoRatio(returns) if std_return > 0 else 0
    
    # Tail risk
    var = rp.VaR_Hist(returns, alpha=1-confidence_level)
    cvar = rp.CVaR_Hist(returns, alpha=1-confidence_level)
    
    # Drawdown analysis
    max_dd = rp.MaxDrawDown(returns)
    
    return {
        "Expected Return": mean_return,
        "Volatility": std_return,
        "Annualized Volatility": std_return * np.sqrt(365),
        "Sharpe Ratio": sharpe,
        "Sortino Ratio": sortino,
        f"VaR {confidence_level:.0%}": var,
        f"CVaR {confidence_level:.0%}": cvar,
        "Max Drawdown": max_dd,
        "Best Case": np.max(returns),
        "Worst Case": np.min(returns),
        "Probability of Loss": np.mean(returns < 0),
        "Skewness": float(pd.Series(returns).skew()),
        "Kurtosis": float(pd.Series(returns).kurtosis())
    }

# ---------------------- Visualization ----------------------
def plot_portfolio_paths(
    paths: np.ndarray,
    time_horizon: int,
    initial_value: float = 100.0
) -> go.Figure:
    """
    Create interactive plot of portfolio simulation paths.
    
    Args:
        paths: Array of portfolio paths
        time_horizon: Simulation horizon
        initial_value: Initial portfolio value
        
    Returns:
        Plotly Figure object
    """
    dates = pd.date_range(start=datetime.today(), periods=time_horizon + 1)
    percentiles = np.percentile(paths, [5, 25, 50, 75, 95], axis=0)
    
    fig = go.Figure()
    
    # Confidence bands
    fig.add_trace(go.Scatter(
        x=dates,
        y=percentiles[0],
        fill=None,
        mode='lines',
        line=dict(width=0),
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=dates,
        y=percentiles[4],
        fill='tonexty',
        mode='lines',
        line=dict(width=0),
        fillcolor='rgba(0,100,80,0.2)',
        name='90% Confidence'
    ))
    
    # Main percentiles
    fig.add_trace(go.Scatter(
        x=dates,
        y=percentiles[2],
        mode='lines',
        name='Median',
        line=dict(color='blue', width=3)
    ))
    fig.add_trace(go.Scatter(
        x=dates,
        y=percentiles[1],
        mode='lines',
        name='25th Percentile',
        line=dict(color='lightblue', width=1, dash='dot')
    ))
    fig.add_trace(go.Scatter(
        x=dates,
        y=percentiles[3],
        mode='lines',
        name='75th Percentile',
        line=dict(color='lightblue', width=1, dash='dot')
    ))
    
    # Initial value reference
    fig.add_hline(
        y=initial_value,
        line_dash="dash",
        line_color="red",
        annotation_text="Initial Value"
    )
    
    fig.update_layout(
        title='Portfolio Monte Carlo Simulation',
        xaxis_title='Date',
        yaxis_title='Portfolio Value',
        hovermode="x unified",
        height=600,
        template='plotly_white'
    )
    
    return fig

def plot_returns_distribution(returns: np.ndarray) -> go.Figure:
    """
    Plot distribution of final portfolio returns.
    """
    fig = px.histogram(
        x=returns,
        nbins=100,
        title='Portfolio Returns Distribution',
        labels={'x': 'Return'},
        marginal='box'
    )
    
    fig.update_layout(
        template='plotly_white',
        bargap=0.1
    )
    
    return fig

# ---------------------- Main Application ----------------------
def main():
    st.title("🚀 Institutional Crypto Risk Platform")
    st.markdown("""
    **Advanced Portfolio Stress Testing & Monte Carlo Simulation**  
    *Institutional-grade risk analytics for crypto assets*
    """)
    
    # ---------------------- Sidebar ----------------------
    st.sidebar.header("Portfolio Configuration")
    
    # Asset selection
    available_assets = list(ASSET_PARAMS.keys())
    assets = st.sidebar.multiselect(
        "Select Assets", 
        available_assets,
        default=["BTC", "ETH", "SOL"]
    )
    
    if not assets:
        st.warning("Please select at least one asset to run the simulation.")
        st.stop()
    
    # Weight allocation
    weights = []
    cols = st.sidebar.columns(len(assets))
    for i, asset in enumerate(assets):
        with cols[i]:
            w = st.number_input(
                f"{asset} Weight",
                min_value=0.0,
                max_value=1.0,
                value=1.0/len(assets),
                step=0.05,
                key=f"weight_{asset}"
            )
            weights.append(w)
    
    weights = np.array(weights)
    if not validate_weights(weights):
        st.stop()
    
    weights = normalize_weights(weights)
    
    # Advanced parameters
    with st.sidebar.expander("Advanced Parameters"):
        params = SimulationParameters(
            n_simulations=st.number_input(
                "Number of Simulations",
                min_value=100,
                max_value=100000,
                value=5000,
                step=1000
            ),
            time_horizon=st.number_input(
                "Time Horizon (days)",
                min_value=1,
                max_value=365*3,  # 3 years max
                value=30,
                step=1
            ),
            confidence_level=st.slider(
                "Confidence Level",
                min_value=0.85,
                max_value=0.99,
                value=0.95,
                step=0.01
            ),
            include_jumps=st.checkbox("Include Jump Diffusion", False),
            copula_type=CopulaType(st.selectbox(
                "Dependency Structure",
                options=[CopulaType.GAUSSIAN, CopulaType.STUDENT, CopulaType.CHOLESKY],
                format_func=lambda x: x.value
            ))
        )
    
    # ---------------------- Simulation Execution ----------------------
    if st.sidebar.button("Run Advanced Simulation", type="primary"):
        with st.spinner("Running institutional-grade simulation..."):
            try:
                # Data simulation
                df = simulate_crypto_data(
                    assets,
                    days=365*2,  # 2 years of history
                    include_jumps=params.include_jumps
                )
                returns = df.pct_change().dropna()
                
                # Portfolio simulation
                portfolio_paths, asset_sims = monte_carlo_sim(returns, weights, params)
                metrics = calculate_risk_metrics(portfolio_paths, params.confidence_level)
                
                st.success("Simulation Completed Successfully!")
                
                # ---------------------- Results Display ----------------------
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "📊 Portfolio Simulation", 
                    "📈 Asset Analysis", 
                    "🛡️ Risk Metrics", 
                    "📊 Returns Distribution",
                    "📄 Full Report"
                ])
                
                with tab1:
                    st.plotly_chart(
                        plot_portfolio_paths(
                            portfolio_paths,
                            params.time_horizon,
                            params.initial_portfolio_value
                        ),
                        use_container_width=True
                    )
                    
                    # Show sample paths
                    with st.expander("View Sample Paths"):
                        st.line_chart(
                            pd.DataFrame(
                                portfolio_paths[:100].T,
                                index=pd.date_range(
                                    start=datetime.today(),
                                    periods=params.time_horizon + 1
                                )
                            )
                        )
                
                with tab2:
                    # Correlation matrix
                    st.subheader("Asset Correlation Matrix")
                    fig, ax = plt.subplots(figsize=(8, 6))
                    sns.heatmap(
                        returns.corr(),
                        annot=True,
                        cmap='coolwarm',
                        center=0,
                        vmin=-1,
                        vmax=1,
                        ax=ax
                    )
                    st.pyplot(fig)
                    
                    # Historical performance
                    st.subheader("Historical Performance")
                    st.line_chart(df)
                
                with tab3:
                    # Key metrics display
                    st.subheader("Portfolio Risk Metrics")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Expected Return", f"{metrics['Expected Return']:.2%}")
                        st.metric("Annualized Volatility", f"{metrics['Annualized Volatility']:.2%}")
                        st.metric(f"VaR {params.confidence_level:.0%}", f"{metrics[f'VaR {params.confidence_level:.0%}']:.2%}")
                    
                    with col2:
                        st.metric("Sharpe Ratio", f"{metrics['Sharpe Ratio']:.2f}")
                        st.metric("Sortino Ratio", f"{metrics['Sortino Ratio']:.2f}")
                        st.metric(f"CVaR {params.confidence_level:.0%}", f"{metrics[f'CVaR {params.confidence_level:.0%}']:.2%}")
                    
                    with col3:
                        st.metric("Max Drawdown", f"{metrics['Max Drawdown']:.2%}")
                        st.metric("Probability of Loss", f"{metrics['Probability of Loss']:.2%}")
                        st.metric("Skewness", f"{metrics['Skewness']:.2f}")
                
                with tab4:
                    st.plotly_chart(
                        plot_returns_distribution((portfolio_paths[:, -1]/100) - 1),
                        use_container_width=True
                    )
                
                with tab5:
                    # Full report generation
                    st.subheader("Full Risk Report")
                    
                    report = {
                        "metadata": {
                            "date": datetime.now().isoformat(),
                            "assets": assets,
                            "weights": {a: w for a, w in zip(assets, weights)},
                            "parameters": {
                                "simulations": params.n_simulations,
                                "horizon": params.time_horizon,
                                "confidence": params.confidence_level,
                                "copula": params.copula_type.value,
                                "include_jumps": params.include_jumps
                            }
                        },
                        "metrics": metrics,
                        "correlation_matrix": returns.corr().to_dict()
                    }
                    
                    # Download link
                    report_json = json.dumps(report, indent=2)
                    b64 = base64.b64encode(report_json.encode()).decode()
                    href = f'<a href="data:application/json;base64,{b64}" download="crypto_risk_report.json">📥 Download Full Report (JSON)</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    
                    # Report preview
                    with st.expander("📄 Report Preview"):
                        st.json(report)
            
            except Exception as e:
                st.error(f"Simulation failed: {str(e)}")
                logger.exception("Simulation error")

if __name__ == "__main__":
    main()