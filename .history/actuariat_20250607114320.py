import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from scipy import stats
import statsmodels.api as sm
import pydeck as pdk

# Configuration de la page
st.set_page_config(
    page_title="Analyse Actuarielle - Modèle Lee-Carter",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .sidebar .sidebar-content {
        background-color: #343a40;
        color: white;
    }
    h1 {
        color: #2c3e50;
        border-bottom: 2px solid #2c3e50;
        padding-bottom: 10px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 24px;
    }
    .stSelectbox, .stSlider, .stNumberInput {
        margin-bottom: 20px;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Titre de l'application
st.title("📊 Analyse Actuarielle Avancée - Modèle Lee-Carter")
st.markdown("""
    *Application interactive pour l'analyse des taux de mortalité et la projection des risques*  
    *Données: Tables de mortalité HMD - Cohorte masculine née en 1940*
    """)

# Sidebar - Paramètres
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Actuarial_logo.svg/1200px-Actuarial_logo.svg.png", width=100)
    st.title("Paramètres")
    
    analysis_choice = st.selectbox(
        "Sélectionnez l'analyse:",
        ["Visualisation des données", "Modèle Lee-Carter", "Projections", "Calcul de la VAP", "Analyse du risque"]
    )
    
    st.markdown("---")
    st.markdown("**Paramètres du modèle**")
    start_year = st.slider("Année de début", 1950, 2000, 1975)
    end_year = st.slider("Année de fin", 2000, 2050, 2022)
    cohort_year = st.number_input("Année de cohorte", 1900, 2000, 1940)
    
    st.markdown("---")
    st.markdown("**Paramètres de projection**")
    projection_years = st.slider("Années de projection", 5, 50, 25)
    confidence_level = st.slider("Niveau de confiance", 0.90, 0.999, 0.995, 0.001)
    
    st.markdown("---")
    st.markdown("**Paramètres financiers**")
    discount_rate = st.number_input("Taux d'actualisation (%)", 0.0, 10.0, 2.0) / 100
    annuity_amount = st.number_input("Montant de la rente", 1000, 100000, 10000, 1000)

# Chargement des données (simulé - en production, utiliser des vrais fichiers)
@st.cache_data
def load_data():
    # Simulation des données de décès
    years = list(range(1950, 2023))
    ages = list(range(50, 91))
    
    # Création d'un DataFrame aléatoire mais réaliste
    np.random.seed(42)
    death_rates = np.zeros((len(ages), len(years)))
    
    # Tendance générale de mortalité
    for i, age in enumerate(ages):
        base_rate = 0.001 * (1.08 ** (age - 50))
        trend = np.linspace(0, -0.015, len(years))
        noise = np.random.normal(0, 0.0001, len(years))
        death_rates[i,:] = base_rate * (1 + trend) + noise
    
    deaths = pd.DataFrame(death_rates, index=ages, columns=years)
    deaths = deaths.reset_index().melt(id_vars='index', var_name='Year', value_name='Deaths')
    deaths = deaths.rename(columns={'index': 'Age'})
    
    # Expositions (simulées comme proportionnelles aux décès)
    exposures = deaths.copy()
    exposures['Exposure'] = exposures['Deaths'] * np.random.uniform(800, 1200, len(exposures))
    
    return deaths, exposures

deaths, exposures = load_data()

# Page principale en fonction du choix
if analysis_choice == "Visualisation des données":
    st.header("📊 Exploration des Données")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Données de décès")
        st.dataframe(deaths.head(10), height=300)
        
        age_filter = st.slider("Filtrer par âge", 50, 90, (50, 90))
        filtered_deaths = deaths[(deaths['Age'] >= age_filter[0]) & (deaths['Age'] <= age_filter[1])]
        
        fig = px.line(filtered_deaths, x='Year', y='Deaths', color='Age',
                     title="Évolution des décès par âge")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Données d'exposition")
        st.dataframe(exposures.head(10), height=300)
        
        fig = px.line(exposures.groupby('Year')['Exposure'].sum().reset_index(), 
                     x='Year', y='Exposure',
                     title="Exposition totale par année")
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Analyse de la cohorte 1940")
    
    cohort_data = deaths[(deaths['Year'] - deaths['Age'] == cohort_year) & (deaths['Age'] >= 50)]
    cohort_data = cohort_data.merge(exposures, on=['Age', 'Year'])
    cohort_data['qxt'] = cohort_data['Deaths_x'] / cohort_data['Exposure']
    cohort_data['log_qxt'] = np.log(cohort_data['qxt'])
    
    fig = px.line(cohort_data, x='Age', y='qxt', 
                 title=f"Taux de mortalité pour la cohorte {cohort_year}")
    st.plotly_chart(fig, use_container_width=True)

elif analysis_choice == "Modèle Lee-Carter":
    st.header("🔍 Modèle Lee-Carter")
    
    st.markdown("""
    Le modèle Lee-Carter est une méthode de projection de la mortalité qui décompose les taux de mortalité en:
    - Un composant âge-spécifique (ax)
    - Un composant temps-spécifique (kt)
    - Un paramètre d'interaction (bx)
    """)
    
    # Simulation des paramètres LC
    np.random.seed(123)
    ages = np.arange(50, 91)
    ax = np.log(0.01) + 0.05 * (ages - 50) / 40
    bx = 0.8 + 0.2 * np.sin((ages - 50) * np.pi / 40)
    kt = np.linspace(5, -5, 73)  # 1950-2022
    
    # Affichage des paramètres
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig, ax1 = plt.subplots()
        ax1.plot(ages, ax, color='blue')
        ax1.set_title("Paramètre ax (niveau de mortalité)")
        ax1.set_xlabel("Âge")
        st.pyplot(fig)
    
    with col2:
        fig, ax2 = plt.subplots()
        ax2.plot(ages, bx, color='green')
        ax2.set_title("Paramètre bx (sensibilité à kt)")
        ax2.set_xlabel("Âge")
        st.pyplot(fig)
    
    with col3:
        fig, ax3 = plt.subplots()
        ax3.plot(range(1950, 2023), kt, color='red')
        ax3.set_title("Paramètre kt (indice temporel)")
        ax3.set_xlabel("Année")
        st.pyplot(fig)
    
    st.markdown("---")
    st.subheader("Ajustement du modèle")
    
    # Matrice des taux de mortalité simulés
    log_mx = np.outer(ax, np.ones(len(kt))) + np.outer(bx, kt)
    mx = np.exp(log_mx)
    
    # Visualisation 3D
    st.markdown("**Surface des taux de mortalité (log) - Modèle Lee-Carter**")
    
    years = list(range(1950, 2023))
    ages = list(range(50, 91))
    
    fig = px.imshow(log_mx, 
                   x=years, 
                   y=ages,
                   labels=dict(x="Année", y="Âge", color="log(qxt)"),
                   title="Matrice des taux de mortalité (log)")
    st.plotly_chart(fig, use_container_width=True)

elif analysis_choice == "Projections":
    st.header("🔮 Projections de Mortalité")
    
    st.markdown(f"""
    Projection des taux de mortalité sur {projection_years} ans pour la cohorte {cohort_year}
    """)
    
    # Simulation des projections
    np.random.seed(42)
    future_years = list(range(2023, 2023 + projection_years + 1))
    all_years = list(range(1950, 2023 + projection_years + 1))
    
    # Extension de kt avec une marche aléatoire
    kt_history = np.linspace(5, -5, 73)  # 1950-2022
    kt_proj = [kt_history[-1]]
    for _ in range(projection_years):
        kt_proj.append(kt_proj[-1] + np.random.normal(-0.1, 0.3))
    
    kt_full = np.concatenate([kt_history, kt_proj[1:]])
    
    # Calcul des taux projetés
    ages = np.arange(50, 91)
    ax = np.log(0.01) + 0.05 * (ages - 50) / 40
    bx = 0.8 + 0.2 * np.sin((ages - 50) * np.pi / 40)
    
    log_mx_full = np.outer(ax, np.ones(len(kt_full))) + np.outer(bx, kt_full)
    mx_full = np.exp(log_mx_full)
    
    # Visualisation
    fig = px.line(x=all_years, y=kt_full, 
                 title="Projection de l'indice kt (marche aléatoire)")
    fig.add_vline(x=2022.5, line_dash="dash", line_color="red")
    fig.update_layout(xaxis_title="Année", yaxis_title="Valeur de kt")
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Taux de mortalité projetés")
    
    selected_age = st.slider("Sélectionnez un âge pour visualiser", 50, 90, 65)
    age_idx = selected_age - 50
    
    fig = px.line(x=all_years, y=mx_full[age_idx, :], 
                 title=f"Taux de mortalité à l'âge {selected_age} - Historique et Projection")
    fig.add_vline(x=2022.5, line_dash="dash", line_color="red")
    fig.update_layout(xaxis_title="Année", yaxis_title="qxt")
    st.plotly_chart(fig, use_container_width=True)
    
    # Tableau des taux projetés
    st.markdown("**Valeurs projetées (sélection)**")
    proj_data = pd.DataFrame({
        'Année': future_years,
        'qxt': mx_full[age_idx, -projection_years-1:],
        'log(qxt)': log_mx_full[age_idx, -projection_years-1:]
    })
    st.dataframe(proj_data.style.format({'qxt': '{:.6f}', 'log(qxt)': '{:.4f}'}))

elif analysis_choice == "Calcul de la VAP":
    st.header("💰 Calcul de la Valeur Actuelle Probable")
    
    st.markdown(f"""
    Calcul de la valeur actuelle probable d'une rente viagère pour un assuré de {2005 - cohort_year} ans en 2005  
    **Paramètres:**  
    - Taux d'actualisation: {discount_rate*100:.1f}%  
    - Montant de la rente: {annuity_amount:,.0f}€  
    """)
    
    # Simulation d'une table de mortalité
    ages = np.arange(65, 111)
    qx = 0.001 * (1.08 ** (ages - 65))
    px = 1 - qx
    lx = 100000 * np.cumprod(np.concatenate([[1], px[:-1]]))
    dx = lx * qx
    
    mortality_table = pd.DataFrame({
        'Age': ages,
        'qx': qx,
        'px': px,
        'lx': lx,
        'dx': dx
    })
    
    # Calcul de la VAP
    discount_factors = (1 + discount_rate) ** -(ages - 65)
    vap = annuity_amount * np.sum((lx / lx[0]) * discount_factors)
    
    # Affichage des résultats
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Table de mortalité (extrait)**")
        st.dataframe(mortality_table.head(10).style.format({
            'qx': '{:.6f}',
            'px': '{:.6f}',
            'lx': '{:.0f}',
            'dx': '{:.0f}'
        }))
    
    with col2:
        st.markdown("**Résultats du calcul**")
        
        st.metric("Valeur Actuelle Probable", f"{vap:,.2f}€")
        st.metric("Espérance de vie résiduelle", f"{np.sum(lx[1:])/lx[0]:.2f} ans")
        
        st.markdown("""
        **Formule de calcul:**  
        VAP = Σ (lx/l0 * rente * (1 + taux)^-t
        """)
    
    st.markdown("---")
    st.subheader("Décomposition des flux actualisés")
    
    fig = px.bar(
        x=ages,
        y=annuity_amount * (lx / lx[0]) * discount_factors,
        labels={'x': 'Âge', 'y': 'Flux actualisé (€)'},
        title="Flux de rente actualisés par âge"
    )
    st.plotly_chart(fig, use_container_width=True)

elif analysis_choice == "Analyse du risque":
    st.header("⚠️ Analyse du Risque Actuariel")
    
    st.markdown(f"""
    Simulation Monte Carlo pour estimer la réserve requise au niveau de confiance {confidence_level*100:.1f}%
    """)
    
    # Paramètres de simulation
    n_sim = st.slider("Nombre de simulations", 1000, 50000, 10000)
    
    if st.button("Lancer la simulation"):
        st.info(f"Exécution de {n_sim:,} simulations...")
        
        # Simulation des durées de vie
        np.random.seed(123)
        u = np.random.uniform(0, 1, n_sim)
        
        # Table de mortalité (simplifiée)
        ages = np.arange(65, 111)
        qx = 0.001 * (1.08 ** (ages - 65))
        px = 1 - qx
        cum_px = np.cumprod(px)
        
        # Trouver l'âge de décès pour chaque simulation
        death_ages = np.zeros(n_sim)
        for i in range(n_sim):
            death_ages[i] = ages[np.argmax(u[i] > cum_px)] if np.any(u[i] > cum_px) else 110
        
        # Calcul des pertes
        discount_factors = (1 + discount_rate) ** -(death_ages - 65)
        losses = annuity_amount * (1 - discount_factors) / discount_rate
        
        # Calcul des indicateurs
        mean_loss = np.mean(losses)
        var = np.percentile(losses, confidence_level * 100)
        es = losses[losses >= var].mean()
        
        # Affichage des résultats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Perte moyenne (VAP)", f"{mean_loss:,.2f}€")
        
        with col2:
            st.metric(f"Value-at-Risk ({confidence_level*100:.1f}%)", f"{var:,.2f}€")
        
        with col3:
            st.metric("Expected Shortfall", f"{es:,.2f}€")
        
        st.markdown("---")
        st.subheader("Distribution des pertes")
        
        fig = px.histogram(
            x=losses,
            nbins=50,
            labels={'x': 'Montant des pertes (€)'},
            title=f"Distribution des pertes sur {n_sim:,} simulations"
        )
        fig.add_vline(x=mean_loss, line_dash="dash", line_color="green", annotation_text="Moyenne")
        fig.add_vline(x=var, line_dash="dash", line_color="red", annotation_text="VaR")
        st.plotly_chart(fig, use_container_width=True)
        
        # Courbe des réserves par niveau de confiance
        alphas = np.linspace(0.9, 0.999, 100)
        reserves = np.percentile(losses, alphas * 100)
        
        fig = px.line(
            x=alphas,
            y=reserves,
            labels={'x': 'Niveau de confiance', 'y': 'Réserve requise (€)'},
            title="Réserve en fonction du niveau de confiance"
        )
        fig.add_hline(y=mean_loss, line_dash="dash", line_color="green")
        st.plotly_chart(fig, use_container_width=True)

# Pied de page
st.markdown("---")
st.markdown("""
    *Application développée avec Streamlit - Analyse Actuarielle Avancée*  
    *Données simulées pour illustration - © 2023*
    """)