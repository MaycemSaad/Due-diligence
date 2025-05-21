# Add these imports at the top
import time
from threading import Thread
from queue import Queue

# ---------------------- Real-Time Simulation Class ----------------------
class RealTimeSimulation:
    def __init__(self):
        self.running = False
        self.queue = Queue()
        self.thread = None
        self.latest_results = None
        
    def start(self, assets, weights, params):
        if self.running:
            self.stop()
            
        self.running = True
        self.thread = Thread(target=self._run_simulation, args=(assets, weights, params))
        self.thread.start()
        
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
            
    def _run_simulation(self, assets, weights, params):
        """Background thread for continuous simulation"""
        df = simulate_crypto_data(assets, include_jumps=params.include_jumps)
        returns = df.pct_change().dropna()
        
        while self.running:
            try:
                portfolio_paths, asset_returns = monte_carlo_sim(
                    returns=returns,
                    weights=weights,
                    params=params
                )
                metrics = calculate_risk_metrics(portfolio_paths, params.confidence_level)
                
                self.latest_results = {
                    "portfolio_paths": portfolio_paths,
                    "metrics": metrics,
                    "correlation_matrix": returns.corr(),
                    "historical_data": df,
                    "timestamp": datetime.now()
                }
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Simulation error: {str(e)}")
                time.sleep(10)  # Wait longer if error occurs

# ---------------------- Updated Main Application ----------------------
def main():
    st.title("🚀 Institutional Crypto Risk Platform")
    st.markdown("""
    **Advanced Portfolio Stress Testing & Monte Carlo Simulation**  
    *Institutional-grade risk analytics for crypto assets*
    """)
    
    # Initialize real-time simulation
    if 'simulation' not in st.session_state:
        st.session_state.simulation = RealTimeSimulation()
    
    # ---------------------- Sidebar ----------------------
    st.sidebar.header("Portfolio Configuration")
    
    # Asset selection
    available_assets = list(ASSET_PARAMS.keys())
    assets = st.sidebar.multiselect(
        "Select Assets", 
        available_assets,
        default=["BTC", "ETH", "SOL"],
        key='assets'
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
                step=1000,
                key='n_simulations'
            ),
            time_horizon=st.number_input(
                "Time Horizon (days)",
                min_value=1,
                max_value=365*3,
                value=30,
                step=1,
                key='time_horizon'
            ),
            confidence_level=st.slider(
                "Confidence Level",
                min_value=0.85,
                max_value=0.99,
                value=0.95,
                step=0.01,
                key='confidence_level'
            ),
            include_jumps=st.checkbox("Include Jump Diffusion", False, key='include_jumps'),
            copula_type=CopulaType(st.selectbox(
                "Dependency Structure",
                options=[CopulaType.GAUSSIAN, CopulaType.STUDENT, CopulaType.CHOLESKY],
                format_func=lambda x: x.value,
                key='copula_type'
            ))
        )
    
    # Control buttons
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("▶️ Start Real-time", key='start_btn'):
            st.session_state.simulation.start(assets, weights, params)
            st.success("Real-time simulation started!")
            
    with col2:
        if st.button("⏹️ Stop", key='stop_btn'):
            st.session_state.simulation.stop()
            st.warning("Simulation stopped")
    
    # Status indicator
    status_placeholder = st.sidebar.empty()
    
    # ---------------------- Real-time Display ----------------------
    results_placeholder = st.empty()
    
    while True:
        # Update status
        status_placeholder.markdown(
            f"**Status:** {'🟢 Running' if st.session_state.simulation.running else '🔴 Stopped'}"
        )
        
        # Get latest results
        results = st.session_state.simulation.latest_results
        
        if results:
            with results_placeholder.container():
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
                            results["portfolio_paths"],
                            params.time_horizon,
                            params.initial_portfolio_value
                        ),
                        use_container_width=True
                    )
                    
                    with st.expander("View Sample Paths"):
                        st.line_chart(
                            pd.DataFrame(
                                results["portfolio_paths"][:100].T,
                                index=pd.date_range(
                                    start=datetime.today(),
                                    periods=params.time_horizon + 1
                                )
                            )
                        )
                
                with tab2:
                    st.subheader("Asset Correlation Matrix")
                    fig, ax = plt.subplots(figsize=(8, 6))
                    sns.heatmap(
                        results["correlation_matrix"],
                        annot=True,
                        cmap='coolwarm',
                        center=0,
                        vmin=-1,
                        vmax=1,
                        ax=ax
                    )
                    st.pyplot(fig)
                    
                    st.subheader("Historical Performance")
                    st.line_chart(results["historical_data"])
                
                with tab3:
                    st.subheader("Portfolio Risk Metrics")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Expected Return", f"{results['metrics']['Expected Return']:.2%}")
                        st.metric("Annualized Volatility", f"{results['metrics']['Annualized Volatility']:.2%}")
                        st.metric(f"VaR {params.confidence_level:.0%}", f"{results['metrics'][f'VaR {params.confidence_level:.0%}']:.2%}")
                    
                    with col2:
                        st.metric("Sharpe Ratio", f"{results['metrics']['Sharpe Ratio']:.2f}")
                        st.metric("Sortino Ratio", f"{results['metrics']['Sortino Ratio']:.2f}")
                        st.metric(f"CVaR {params.confidence_level:.0%}", f"{results['metrics'][f'CVaR {params.confidence_level:.0%}']:.2%}")
                    
                    with col3:
                        st.metric("Max Drawdown", f"{results['metrics']['Max Drawdown']:.2%}")
                        st.metric("Probability of Loss", f"{results['metrics']['Probability of Loss']:.2%}")
                        st.metric("Skewness", f"{results['metrics']['Skewness']:.2f}")
                
                with tab4:
                    st.plotly_chart(
                        plot_returns_distribution((results["portfolio_paths"][:, -1]/100) - 1),
                        use_container_width=True
                    )
                
                with tab5:
                    st.subheader("Full Risk Report")
                    
                    report = {
                        "metadata": {
                            "date": results["timestamp"].isoformat(),
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
                        "metrics": results['metrics'],
                        "correlation_matrix": results["correlation_matrix"].to_dict()
                    }
                    
                    report_json = json.dumps(report, indent=2)
                    b64 = base64.b64encode(report_json.encode()).decode()
                    href = f'<a href="data:application/json;base64,{b64}" download="crypto_risk_report.json">📥 Download Full Report (JSON)</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    
                    with st.expander("📄 Report Preview"):
                        st.json(report)
        
        # Add a small delay to prevent high CPU usage
        time.sleep(1)
        
        # Break the loop if the simulation is stopped and we're not showing results
        if not st.session_state.simulation.running and not results:
            break

if __name__ == "__main__":
    main()