"""
Suite de tests de validation complète pour TSP Meknès.
Vérifie la robustesse et la cohérence de tous les modules :
1. Données géographiques et matrice OSRM
2. Fonctions de fitness, sélection, croisement et mutation
3. Moteur génétique et validation formelle de la solution TSP
4. Optimiseur Optuna
5. Système Multi-Agents IA (Web -> Scientific -> Arbitration)
6. Générateurs graphiques Plotly et Folium
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Ajout du chemin racine
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from routing.distance_matrix import load_meknes_points, load_or_compute_distance_matrix
from algorithms.fitness import compute_tour_distance, evaluate_population
from algorithms.selection import roulette_wheel_selection, tournament_selection
from algorithms.crossover import ordered_crossover_ox, pmx_crossover
from algorithms.mutation import inversion_mutation, swap_mutation
from algorithms.genetic_algorithm import GeneticAlgorithmTSP
from optimization.optuna_optimizer import OptunaTSPOptimizer
from agents.arbitration_agent import run_agentic_pipeline
from visualization.convergence import create_convergence_plot
from visualization.cartesian_plot import create_cartesian_tsp_plot
from routing.map_visualization import create_meknes_folium_map
from utils.helpers import validate_tsp_solution


def run_tests():
    print("==================================================")
    print("🧪 DÉMARRAGE DE LA SUITE DE TESTS - TSP MEKNÈS")
    print("==================================================")

    # 1. Test des Données
    print("\n[Test 1/6] Chargement des données géographiques et de la matrice OSRM...")
    points_df = load_meknes_points()
    assert len(points_df) == 41, f"Attendu 41 points, reçu {len(points_df)}"
    assert points_df.iloc[0]["category"] == "Depot", "Le point 0 doit être l'entrepôt"
    print(f"  ✓ {len(points_df)} points réels chargés avec succès.")

    matrix, is_live, msg = load_or_compute_distance_matrix()
    assert matrix.shape == (41, 41), f"Taille matrice incorrecte : {matrix.shape}"
    assert np.all(np.diag(matrix) == 0.0), "La diagonale doit être nulle"
    assert np.min(matrix) >= 0.0, "Aucune distance ne peut être négative"
    print(f"  ✓ Matrice de distances (41x41) valide. Source : {msg}")

    # 2. Test des Opérateurs Génétiques
    print("\n[Test 2/6] Test unitaire des opérateurs génétiques...")
    sample_tour = list(range(1, 41))
    
    # Inversion & Swap
    mut_inv = inversion_mutation(sample_tour)
    assert set(mut_inv) == set(sample_tour), "La mutation ne doit pas altérer l'ensemble des villes"
    mut_swap = swap_mutation(sample_tour)
    assert set(mut_swap) == set(sample_tour), "La mutation swap doit conserver les villes"
    
    # Crossover OX & PMX
    p1 = sample_tour.copy()
    p2 = list(reversed(sample_tour))
    c1, c2 = ordered_crossover_ox(p1, p2)
    assert len(c1) == 40 and set(c1) == set(p1), "OX1 doit produire une permutation valide de taille 40"
    assert len(c2) == 40 and set(c2) == set(p1), "OX1 enfant 2 doit être une permutation valide"
    
    c1_pmx, c2_pmx = pmx_crossover(p1, p2)
    assert len(c1_pmx) == 40 and set(c1_pmx) == set(p1), "PMX doit produire une permutation valide"
    print("  ✓ Opérateurs de croisement (OX1, PMX) et mutation (2-Opt, Swap) conformes.")

    # 3. Test du Moteur Génétique Principal
    print("\n[Test 3/6] Résolution d'une tournée par Algorithme Génétique...")
    ga = GeneticAlgorithmTSP(
        distance_matrix=matrix,
        num_clients=40,
        pop_size=100,
        selection_method="Tournament Selection",
        mutation_rate=0.2,
        crossover_rate=0.8,
        num_iterations=100,
        seed=42
    )
    res = ga.solve()
    assert res["is_valid"] is True, f"Erreur de validation TSP : {res['validation_message']}"
    assert res["best_tour"][0] == 0 and res["best_tour"][-1] == 0, "Doit débuter et finir à l'entrepôt"
    assert len(res["best_tour"]) == 42, "Le circuit doit comporter exactement 42 étapes (0 + 40 clients + 0)"
    assert res["best_distance"] < res["initial_distance"], "L'optimisation doit améliorer ou maintenir la distance"
    print(f"  ✓ Solution TSP valide : Distance initiale {res['initial_distance']} km -> Finale {res['best_distance']} km (Gain: {res['improvement_percent']}%)")

    # 4. Test Optuna
    print("\n[Test 4/6] Exécution de l'optimiseur Optuna (3 essais rapides)...")
    opt = OptunaTSPOptimizer(distance_matrix=matrix, num_clients=40, n_trials=3, seed=42)
    opt_res = opt.optimize()
    assert "best_params" in opt_res and "best_value" in opt_res, "Optuna doit renvoyer les meilleurs hyperparamètres"
    assert len(opt_res["trials_df"]) == 3, "Nombre d'essais Optuna incorrect"
    print(f"  ✓ Optuna opérationnel. Meilleurs paramètres : {opt_res['best_params']} (Distance: {opt_res['best_value']} km)")

    # 5. Test Système Multi-Agents IA
    print("\n[Test 5/6] Exécution du pipeline Multi-Agents IA (Web -> Scientific -> Arbitration)...")
    pipeline_res = run_agentic_pipeline(distance_matrix=matrix, points_df=points_df)
    assert pipeline_res["web_report"]["status"] == "COMPLETED"
    assert pipeline_res["scientific_report"]["status"] == "COMPLETED"
    assert pipeline_res["arbitration_decision"]["status"] == "ARBITRATION_COMPLETED"
    assert pipeline_res["ga_result"]["is_valid"] is True
    print(f"  ✓ Système Multi-Agents validé. Arbitrage : '{pipeline_res['arbitration_decision']['decision_title']}'")

    # 6. Test Visualisations (Plotly & Folium)
    print("\n[Test 6/6] Génération des graphiques (Convergence, Cartésien 2D, Folium SIG)...")
    conv_fig = create_convergence_plot(res["history_best"], res["history_avg"])
    assert conv_fig is not None, "Échec génération courbe de convergence"

    cart_fig = create_cartesian_tsp_plot(points_df, res["best_tour"])
    assert cart_fig is not None, "Échec génération plan cartésien 2D"

    fmap, segments = create_meknes_folium_map(points_df, res["best_tour"], matrix)
    assert fmap is not None, "Échec génération carte Folium"
    assert len(segments) == 41, f"Attendu 41 segments (dont retour entrepôt), obtenu {len(segments)}"
    print(f"  ✓ Visualisations générées avec succès ({len(segments)} segments routiers cartographiés).")

    print("\n==================================================")
    print("🎉 TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS (6/6) !")
    print("==================================================")


if __name__ == "__main__":
    run_tests()
