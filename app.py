"""
TSP MEKNÈS – Intelligent Urban Route Optimization
Application interactive de recherche opérationnelle combinant :
- Algorithmes Génétiques (GA)
- Optimisation des Hyperparamètres (Optuna)
- Intelligence Artificielle Multi-Agents (Agentic AI)
- Cartographie Interactive & Routage Réel OSRM / OpenStreetMap
"""

import time
import streamlit as st
import numpy as np
import pandas as pd
from streamlit_folium import st_folium

from utils.config import (
    POINTS_CSV,
    DISTANCE_MATRIX_CSV,
    POPULATION_SIZES,
    SELECTION_METHODS,
    MUTATION_RATES,
    CROSSOVER_RATES,
    ITERATION_OPTIONS,
    DEFAULT_POP_SIZE,
    DEFAULT_SELECTION,
    DEFAULT_MUTATION_RATE,
    DEFAULT_CROSSOVER_RATE,
    DEFAULT_ITERATIONS,
    DEPOT_ID,
    DEPOT_NAME
)
from utils.helpers import format_chromosome_display
from routing.distance_matrix import load_meknes_points, load_or_compute_distance_matrix
from algorithms.genetic_algorithm import GeneticAlgorithmTSP
from optimization.optuna_optimizer import OptunaTSPOptimizer
from agents.arbitration_agent import run_agentic_pipeline
from visualization.convergence import create_convergence_plot
from visualization.cartesian_plot import create_cartesian_tsp_plot
from routing.map_visualization import create_meknes_folium_map


# Configuration de la page Streamlit
st.set_page_config(
    page_title="TSP Meknès – Intelligent Route Optimization",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Style CSS personnalisé pour un rendu Dashboard haut de gamme
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 10px 0 5px 0;
        margin-bottom: 0px;
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E88E5;
        letter-spacing: 0.5px;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.05rem;
        font-weight: 400;
        color: #90A4AE;
        margin-top: 2px;
        margin-bottom: 15px;
    }
    .quadrant-box {
        background-color: #1a1f2c;
        border: 1px solid #2d3748;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 20px;
        min-height: 520px;
    }
    .quadrant-header {
        font-size: 1.15rem;
        font-weight: 700;
        color: #E2E8F0;
        border-bottom: 2px solid #2B6CB0;
        padding-bottom: 6px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .kpi-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
    .kpi-label {
        font-size: 0.75rem;
        color: #94A3B8;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .kpi-val {
        font-size: 1.4rem;
        font-weight: 800;
        color: #38BDF8;
        margin: 4px 0;
    }
    .badge-valid {
        display: inline-block;
        background-color: #065F46;
        color: #34D399;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 20px;
        border: 1px solid #059669;
    }
    .badge-info {
        display: inline-block;
        background-color: #1E3A8A;
        color: #93C5FD;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 20px;
        border: 1px solid #2563EB;
    }
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# Initialisation du Session State
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.points_df = load_meknes_points(POINTS_CSV)
    matrix, is_live, msg = load_or_compute_distance_matrix(DISTANCE_MATRIX_CSV, POINTS_CSV)
    st.session_state.distance_matrix = matrix
    st.session_state.is_live_osrm = is_live
    st.session_state.matrix_source = msg
    st.session_state.current_mode = "Initial"
    st.session_state.optuna_summary = None
    st.session_state.agentic_summary = None

    # Tour initial (Plus Proche Voisin) pour affichage par défaut immédiat
    default_ga = GeneticAlgorithmTSP(
        distance_matrix=st.session_state.distance_matrix,
        num_clients=len(st.session_state.points_df) - 1,
        pop_size=50,
        num_iterations=20,
        seed=42
    )
    st.session_state.ga_result = default_ga.solve()


# En-tête principal de l'application
st.markdown("""
<div class="main-header">
    <div class="main-title">🚚 TSP MEKNÈS – Intelligent Urban Route Optimization</div>
    <div class="sub-title">Genetic Algorithms | Hyperparameter Optimization | Agentic AI | Real-Time Mapping</div>
</div>
""", unsafe_allow_html=True)


# Bandeau d'état réseau et métadonnées territoriales
col_meta1, col_meta2, col_meta3, col_meta4 = st.columns([2, 1, 1, 1])
with col_meta1:
    source_color = "🟢" if st.session_state.is_live_osrm else "🟡"
    st.caption(f"{source_color} **Routage :** {st.session_state.matrix_source}")
with col_meta2:
    st.caption("📍 **Ville :** Meknès, Maroc")
with col_meta3:
    st.caption("🎯 **Points :** 40 clients + 1 Hub")
with col_meta4:
    st.caption(f"⚙️ **Mode actif :** `{st.session_state.current_mode}`")


# Zone de notification et barre de progression dynamique
progress_placeholder = st.empty()
status_placeholder = st.empty()


# ==============================================================================
# DIVISION EN 4 QUADRANTS ÉQUILIBRÉS
# ==============================================================================

# Ligne 1 : Quadrant 1 (Configuration & Modes) | Quadrant 2 (Résultats & Performance)
col_q1, col_q2 = st.columns(2)

# Ligne 2 : Quadrant 3 (Visualisation Cartésienne 2D) | Quadrant 4 (Cartographie Réelle OSRM)
col_q3, col_q4 = st.columns(2)


# ------------------------------------------------------------------------------
# QUADRANT 1 – Configuration et paramètres du problème
# ------------------------------------------------------------------------------
with col_q1:
    st.markdown("""
    <div class="quadrant-header">
        <span>⚙️</span> QUADRANT 1 – Configuration & Modes d'Optimisation
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📍 A. Définition du problème territorial", expanded=False):
        st.write(f"- **Ville :** Meknès, Maroc (Zone urbaine dense)")
        st.write(f"- **Entrepôt Central :** {DEPOT_NAME}")
        num_pts_slider = st.slider("Nombre de points de livraison :", min_value=10, max_value=40, value=40, step=5,
                                  help="Nombre de points géographiques actifs pour l'optimisation (fixé à 40 par défaut).")
        st.write("- **Distance :** Distance routière réelle en kilomètres (API OSRM Driving Table).")
        st.write("- **Contraintes :** TSP strict (boucle hamiltonienne fermée, 1 seule visite par client).")

    st.markdown("##### 🧬 B. Paramètres de l'Algorithme Génétique")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        pop_size = st.selectbox(
            "1. Population Size :",
            options=POPULATION_SIZES,
            index=POPULATION_SIZES.index(DEFAULT_POP_SIZE)
        )
        selection_method = st.selectbox(
            "2. Selection Method :",
            options=SELECTION_METHODS,
            index=SELECTION_METHODS.index(DEFAULT_SELECTION)
        )
        mutation_rate = st.selectbox(
            "3. Mutation Rate :",
            options=MUTATION_RATES,
            index=MUTATION_RATES.index(DEFAULT_MUTATION_RATE)
        )

    with col_p2:
        crossover_rate = st.selectbox(
            "4. Crossover Rate :",
            options=CROSSOVER_RATES,
            index=CROSSOVER_RATES.index(DEFAULT_CROSSOVER_RATE)
        )
        num_iterations = st.selectbox(
            "5. Number of Iterations :",
            options=ITERATION_OPTIONS,
            index=ITERATION_OPTIONS.index(DEFAULT_ITERATIONS)
        )
        elitism_rate = st.slider("Élitisme (individus conservés) :", 1, 5, 2)

    st.markdown("##### 🚀 C. Sélection du Mode d'Optimisation")
    col_b1, col_b2, col_b3 = st.columns(3)

    # Bouton 1 : MODE MANUEL
    with col_b1:
        run_manual = st.button("🔵 B1 – MANUAL", use_container_width=True,
                               help="Lance l'algorithme génétique avec vos paramètres manuels.")

    # Bouton 2 : OPTUNA OPTIMIZATION
    with col_b2:
        run_optuna = st.button("🟣 B2 – OPTUNA", use_container_width=True,
                               help="Recherche bayésienne automatique des meilleurs hyperparamètres.")

    # Bouton 3 : AGENTIC AI MODE
    with col_b3:
        run_agentic = st.button("🟢 B3 – AGENTIC AI", use_container_width=True,
                                help="Collaboration multi-agents : Recherche -> Analyse -> Arbitrage.")

    # --- TRAITEMENT DU BOUTON B1 : MANUAL MODE ---
    if run_manual:
        st.session_state.current_mode = "MANUAL MODE"
        st.session_state.optuna_summary = None
        st.session_state.agentic_summary = None

        p_bar = progress_placeholder.progress(0, text="Initialisation de la population génétique...")
        
        def ga_callback(gen, max_gen, best_dist, avg_dist):
            pct = int((gen / max_gen) * 100)
            p_bar.progress(pct, text=f"Progression [MANUAL] : Génération {gen}/{max_gen} | Meilleure distance : {best_dist:.2f} km")

        ga_solver = GeneticAlgorithmTSP(
            distance_matrix=st.session_state.distance_matrix,
            num_clients=num_pts_slider,
            pop_size=pop_size,
            selection_method=selection_method,
            mutation_rate=mutation_rate,
            crossover_rate=crossover_rate,
            num_iterations=num_iterations,
            elitism_count=elitism_rate
        )

        res = ga_solver.solve(progress_callback=ga_callback)
        st.session_state.ga_result = res
        p_bar.progress(100, text=f"✅ Optimisation manuelle terminée en {res['execution_time']}s | Distance finale : {res['best_distance']} km")
        time.sleep(0.5)
        st.rerun()

    # --- TRAITEMENT DU BOUTON B2 : OPTUNA OPTIMIZATION ---
    if run_optuna:
        st.session_state.current_mode = "OPTUNA OPTIMIZATION"
        st.session_state.agentic_summary = None

        p_bar = progress_placeholder.progress(0, text="Lancement de l'étude Optuna (TPE Sampler)...")

        def optuna_callback(trial_num, total_trials, cur_best, cur_params):
            pct = int((trial_num / total_trials) * 100)
            p_bar.progress(pct, text=f"Optuna Essai {trial_num}/{total_trials} | Meilleure distance trouvée : {cur_best:.2f} km")

        optimizer = OptunaTSPOptimizer(
            distance_matrix=st.session_state.distance_matrix,
            num_clients=num_pts_slider,
            n_trials=12,
            timeout=45
        )

        opt_res = optimizer.optimize(progress_callback=optuna_callback)
        st.session_state.optuna_summary = opt_res
        st.session_state.ga_result = opt_res["final_run"]
        p_bar.progress(100, text=f"✅ Optimisation Optuna terminée en {opt_res['total_optimization_time']}s | Meilleure distance : {opt_res['best_value']} km")
        time.sleep(0.5)
        st.rerun()

    # --- TRAITEMENT DU BOUTON B3 : AGENTIC AI MODE ---
    if run_agentic:
        st.session_state.current_mode = "AGENTIC AI MODE"
        st.session_state.optuna_summary = None

        p_bar = progress_placeholder.progress(10, text="Agent 1 (Web Research) : Analyse territoriale de Meknès & topologie routière...")
        time.sleep(0.3)
        p_bar.progress(40, text="Agent 2 (Scientific) : Analyse théorique des opérateurs génétiques & profils de convergence...")
        time.sleep(0.3)
        p_bar.progress(70, text="Agent 3 (Arbitration) : Arbitrage contradictoire & sélection exécutive des hyperparamètres...")
        time.sleep(0.3)

        def agent_ga_callback(gen, max_gen, best_dist, avg_dist):
            pct = 70 + int((gen / max_gen) * 30)
            p_bar.progress(min(99, pct), text=f"Résolution Génétique Arbitrée : Génération {gen}/{max_gen} | Distance : {best_dist:.2f} km")

        agent_pipeline_res = run_agentic_pipeline(
            distance_matrix=st.session_state.distance_matrix,
            points_df=st.session_state.points_df,
            preference_mode="balanced",
            progress_callback=agent_ga_callback
        )

        st.session_state.agentic_summary = agent_pipeline_res
        st.session_state.ga_result = agent_pipeline_res["ga_result"]
        p_bar.progress(100, text=f"✅ Pipeline Multi-Agents achevé | Distance finale : {agent_pipeline_res['ga_result']['best_distance']} km")
        time.sleep(0.5)
        st.rerun()


# ------------------------------------------------------------------------------
# QUADRANT 2 – Analyse des performances et résultats
# ------------------------------------------------------------------------------
with col_q2:
    st.markdown("""
    <div class="quadrant-header">
        <span>📊</span> QUADRANT 2 – Analyse des Performances & Résultats
    </div>
    """, unsafe_allow_html=True)

    ga_res = st.session_state.ga_result

    # B. Indicateurs de performance (KPI Cards)
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Best Distance</div>
            <div class="kpi-val" style="color: #34D399;">{ga_res['best_distance']} <span style="font-size:0.8rem">km</span></div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Initial Distance</div>
            <div class="kpi-val" style="color: #F87171;">{ga_res['initial_distance']} <span style="font-size:0.8rem">km</span></div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Improvement</div>
            <div class="kpi-val" style="color: #60A5FA;">+{ga_res['improvement_percent']}%</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Exec Time</div>
            <div class="kpi-val">{ga_res['execution_time']} <span style="font-size:0.8rem">s</span></div>
        </div>
        """, unsafe_allow_html=True)
    with k5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Iterations</div>
            <div class="kpi-val">{ga_res['generations_run']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # A. Courbe de convergence interactive
    conv_fig = create_convergence_plot(
        history_best=ga_res["history_best"],
        history_avg=ga_res["history_avg"],
        title="Convergence Génétique : Meilleur Circuit vs Moyenne de Population"
    )
    st.plotly_chart(conv_fig, use_container_width=True)

    # C. Chromosome solution et conformité TSP
    st.markdown("##### 🧬 Chromosome Solution Optimale")
    chromo_str = format_chromosome_display(ga_res["best_tour"], max_items=14)
    st.code(chromo_str, language="text")

    col_val1, col_val2 = st.columns([2, 1])
    with col_val1:
        if ga_res.get("is_valid", True):
            st.markdown('<span class="badge-valid">✓ Solution TSP Valide : Boucle fermée (Entrepôt ➔ 40 Clients ➔ Entrepôt) sans doublon</span>', unsafe_allow_html=True)
        else:
            st.error(f"Erreur de validité : {ga_res.get('validation_message')}")
    with col_val2:
        st.markdown(f"<span class='badge-info'>Individus : {ga_res.get('pop_size', pop_size)} | Mut : {ga_res.get('mutation_rate', mutation_rate)}</span>", unsafe_allow_html=True)

    # Détails contextuels selon le mode exécuté
    if st.session_state.optuna_summary is not None:
        with st.expander("🔍 Rapport détaillé de l'étude Optuna", expanded=False):
            opt_data = st.session_state.optuna_summary
            st.write(f"**Meilleurs Hyperparamètres identifiés :** {opt_data['best_params']}")
            st.dataframe(opt_data["trials_df"].head(6), use_container_width=True)

    if st.session_state.agentic_summary is not None:
        with st.expander("🤖 Délibération du Système Multi-Agents IA", expanded=False):
            ag_data = st.session_state.agentic_summary
            st.markdown(f"**Décision de l'Arbitre :** {ag_data['arbitration_decision']['decision_title']}")
            for justif in ag_data["arbitration_decision"]["justification"]:
                st.write(f"• {justif}")


# ------------------------------------------------------------------------------
# QUADRANT 3 – Visualisation cartésienne du TSP
# ------------------------------------------------------------------------------
with col_q3:
    st.markdown("""
    <div class="quadrant-header">
        <span>📐</span> QUADRANT 3 – Visualisation Cartésienne 2D
    </div>
    """, unsafe_allow_html=True)

    cartesian_fig = create_cartesian_tsp_plot(
        points_df=st.session_state.points_df,
        tour=st.session_state.ga_result["best_tour"],
        title="Topologie 2D des 40 Points & Tracé de la Tournée Optimisée"
    )
    st.plotly_chart(cartesian_fig, use_container_width=True)

    st.caption("ℹ️ Repère centré sur Meknès (X: Est-Ouest en km, Y: Nord-Sud en km). L'étoile rouge (★) symbolise l'entrepôt central Hamria.")


# ------------------------------------------------------------------------------
# QUADRANT 4 – Cartographie réelle et routage OSRM
# ------------------------------------------------------------------------------
with col_q4:
    st.markdown("""
    <div class="quadrant-header">
        <span>🗺️</span> QUADRANT 4 – Cartographie Réelle & Routage OSRM
    </div>
    """, unsafe_allow_html=True)

    fmap, segments_info = create_meknes_folium_map(
        points_df=st.session_state.points_df,
        tour=st.session_state.ga_result["best_tour"],
        distance_matrix=st.session_state.distance_matrix
    )

    # Affichage de la carte Folium interactive
    st_folium(fmap, width=None, height=450, returned_objects=[])

    st.caption(f"🛣️ **Itinéraire Routier OSRM :** {st.session_state.ga_result['best_distance']} km parcourus dans l'agglomération de Meknès.")

    # Tableau repliable des segments du parcours
    if segments_info:
        with st.expander("📋 Feuille de route détaillée (Segments du parcours)", expanded=False):
            segs_df = pd.DataFrame(segments_info)
            st.dataframe(segs_df, use_container_width=True, height=220)


# ==============================================================================
# PIED DE PAGE & DOCUMENTATION TECHNIQUE DU PROJET
# ==============================================================================
st.markdown("---")
with st.expander("📚 Notes scientifiques, Méthodologie & Hypothèses de Recherche Opérationnelle", expanded=False):
    st.markdown("""
    ### Hypothèses et Cadre Mathématique
    - **Problème :** Le Problème du Voyageur de Commerce (Traveling Salesperson Problem - TSP symétrique) consiste à déterminer le cycle hamiltonien de coût minimal reliant un dépôt central $D$ et $N=40$ points de livraison dans l'agglomération de Meknès.
    - **Matrice de Coûts Réelle :** Contrairement aux modèles théoriques simplifiés reposant sur la distance euclidienne (à vol d'oiseau), cette application exploite la véritable distance routière calculée via l'API **OSRM (Open Source Routing Machine)** sur le graphe routier d'OpenStreetMap.
    - **Espace de Recherche Combinatoire :** Pour $N=40$, la taille de l'espace de recherche est $(N-1)! / 2 = 39! / 2 \\approx 1.02 \\times 10^{46}$ circuits possibles, rendant toute recherche exhaustive impossible.
    - **Moteur Génétique :** Repose sur la permutation des indices $1..40$, l'opérateur de croisement ordonné **OX1 (Davis)** préservant l'ordre relatif des villes, et la mutation par inversion (équivalent 2-Opt) qui élimine les croisements de voirie.
    - **Mode Optuna :** Recherche bayésienne guidée par l'algorithme TPE pour calibrer simultanément taille de population, opérateurs de sélection, taux de croisement et mutation.
    - **Mode Agentic AI :** Architecture collaborative à trois agents simulant une équipe d'ingénieurs en SIG, Recherche Opérationnelle et Direction Technique pour arbitrer rationnellement les meilleurs réglages.
    """)
