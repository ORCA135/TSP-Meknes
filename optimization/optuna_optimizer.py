"""
Module d'optimisation des hyperparamètres par Optuna pour le TSP Meknès.
Recherche automatiquement la configuration optimale des paramètres de l'Algorithme Génétique :
- Population Size (50, 100, 500)
- Selection Method (Roulette Wheel Selection, Tournament Selection)
- Mutation Rate (0.2, 0.5, 0.8)
- Crossover Rate (0.2, 0.5, 0.8)
- Number of Iterations (100, 500, 1000)
"""

import time
from typing import Dict, Any, Callable, Optional
import numpy as np
import pandas as pd
import optuna

# Réduction de la verbosité des logs Optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)

from algorithms.genetic_algorithm import GeneticAlgorithmTSP
from utils.config import (
    POPULATION_SIZES,
    SELECTION_METHODS,
    MUTATION_RATES,
    CROSSOVER_RATES,
    ITERATION_OPTIONS
)


class OptunaTSPOptimizer:
    """
    Optimiseur bayésien (Tree-structured Parzen Estimator - TPE) via Optuna
    pour calibrer automatiquement l'algorithme génétique sur la matrice de Meknès.
    """

    def __init__(self,
                 distance_matrix: np.ndarray,
                 num_clients: int = 40,
                 n_trials: int = 15,
                 timeout: Optional[int] = 60,
                 seed: int = 42):
        self.distance_matrix = distance_matrix
        self.num_clients = num_clients
        self.n_trials = n_trials
        self.timeout = timeout
        self.seed = seed

    def optimize(self,
                 progress_callback: Optional[Callable[[int, int, float, Dict[str, Any]], None]] = None) -> Dict[str, Any]:
        """
        Lance l'étude Optuna pour minimiser la distance totale du circuit TSP.
        
        Paramètres :
        - progress_callback : fonction (trial_number, total_trials, current_best_dist, best_params)
        """
        sampler = optuna.samplers.TPESampler(seed=self.seed)
        study = optuna.create_study(direction="minimize", sampler=sampler)

        trial_count = 0
        current_best = float("inf")

        def objective(trial: optuna.Trial) -> float:
            nonlocal trial_count, current_best
            trial_count += 1

            # Espaces de recherche basés sur les spécifications du projet
            pop_size = trial.suggest_categorical("pop_size", POPULATION_SIZES)
            selection_method = trial.suggest_categorical("selection_method", SELECTION_METHODS)
            mutation_rate = trial.suggest_categorical("mutation_rate", MUTATION_RATES)
            crossover_rate = trial.suggest_categorical("crossover_rate", CROSSOVER_RATES)
            num_iterations = trial.suggest_categorical("num_iterations", ITERATION_OPTIONS)

            # Évaluation avec le solveur génétique
            ga = GeneticAlgorithmTSP(
                distance_matrix=self.distance_matrix,
                num_clients=self.num_clients,
                pop_size=pop_size,
                selection_method=selection_method,
                mutation_rate=mutation_rate,
                crossover_rate=crossover_rate,
                num_iterations=num_iterations,
                seed=self.seed + trial_count
            )

            result = ga.solve()
            best_dist = result["best_distance"]

            if best_dist < current_best:
                current_best = best_dist

            if progress_callback:
                progress_callback(trial_count, self.n_trials, current_best, trial.params)

            return best_dist

        start_time = time.time()
        study.optimize(objective, n_trials=self.n_trials, timeout=self.timeout)
        total_time = time.time() - start_time

        best_params = study.best_params
        best_value = study.best_value

        # Ré-exécuter une simulation complète avec les meilleurs hyperparamètres trouvés
        best_ga = GeneticAlgorithmTSP(
            distance_matrix=self.distance_matrix,
            num_clients=self.num_clients,
            pop_size=best_params["pop_size"],
            selection_method=best_params["selection_method"],
            mutation_rate=best_params["mutation_rate"],
            crossover_rate=best_params["crossover_rate"],
            num_iterations=best_params["num_iterations"],
            seed=self.seed
        )
        final_run = best_ga.solve()

        # Construction du DataFrame des essais
        trials_data = []
        for t in study.trials:
            if t.state == optuna.trial.TrialState.COMPLETE:
                d = {
                    "Trial": t.number + 1,
                    "Distance (km)": round(t.value, 3),
                    "Pop Size": t.params.get("pop_size"),
                    "Selection": t.params.get("selection_method"),
                    "Mutation Rate": t.params.get("mutation_rate"),
                    "Crossover Rate": t.params.get("crossover_rate"),
                    "Iterations": t.params.get("num_iterations"),
                    "Duration (s)": round(t.duration.total_seconds() if t.duration else 0.0, 2)
                }
                trials_data.append(d)

        trials_df = pd.DataFrame(trials_data)
        if not trials_df.empty:
            trials_df = trials_df.sort_values(by="Distance (km)").reset_index(drop=True)

        return {
            "best_params": best_params,
            "best_value": round(best_value, 3),
            "study": study,
            "trials_df": trials_df,
            "final_run": final_run,
            "total_optimization_time": round(total_time, 2),
            "n_trials_completed": len(study.trials)
        }
