"""
Méthodes de sélection pour l'algorithme génétique TSP :
1. Roue de roulette biaisée (Roulette Wheel Selection / Fitness Proportionate)
2. Sélection par tournoi (Tournament Selection)
"""

from typing import List
import numpy as np


def roulette_wheel_selection(population: List[List[int]],
                            fitnesses: np.ndarray,
                            num_parents: int) -> List[List[int]]:
    """
    Sélection par roue de roulette biaisée (Fitness Proportionate Selection).
    Chaque individu a une probabilité d'être sélectionné proportionnelle à sa fitness relative.
    Pour maintenir une pression sélective adéquate sur les distances proches,
    on applique un décalage normalisé : f_scaled = (f - min_f) + epsilon.
    """
    pop_size = len(population)
    if pop_size == 0 or num_parents == 0:
        return []

    # Ajustement de fitness pour éviter les probabilités nulles et accentuer le contraste
    f_min = np.min(fitnesses)
    f_max = np.max(fitnesses)

    if np.isclose(f_min, f_max):
        probabilities = np.ones(pop_size) / pop_size
    else:
        # Échelle linéaire pour donner plus de poids aux meilleurs
        scaled = (fitnesses - f_min) / (f_max - f_min) + 0.05
        probabilities = scaled / np.sum(scaled)

    selected_indices = np.random.choice(pop_size, size=num_parents, p=probabilities, replace=True)
    return [population[idx].copy() for idx in selected_indices]


def tournament_selection(population: List[List[int]],
                         distances: np.ndarray,
                         tournament_size: int,
                         num_parents: int) -> List[List[int]]:
    """
    Sélection par tournoi (Tournament Selection).
    Pour chaque parent à sélectionner, un sous-ensemble de 'tournament_size' individus
    est tiré aléatoirement. L'individu possédant la plus petite distance (meilleure solution)
    remporte le tournoi.
    """
    pop_size = len(population)
    if pop_size == 0 or num_parents == 0:
        return []

    k = max(2, min(tournament_size, pop_size))
    selected = []

    for _ in range(num_parents):
        contenders_indices = np.random.choice(pop_size, size=k, replace=False)
        best_idx = contenders_indices[np.argmin(distances[contenders_indices])]
        selected.append(population[best_idx].copy())

    return selected


def select_parents(population: List[List[int]],
                   distances: np.ndarray,
                   fitnesses: np.ndarray,
                   method: str,
                   num_parents: int,
                   tournament_size: int = 5) -> List[List[int]]:
    """
    Dispatcheur unifié pour la sélection des parents selon la méthode choisie :
    - 'Roulette Wheel Selection'
    - 'Tournament Selection'
    """
    normalized_method = method.strip().lower()

    if "roulette" in normalized_method:
        return roulette_wheel_selection(population, fitnesses, num_parents)
    else:
        # Par défaut : Tournament Selection
        return tournament_selection(population, distances, tournament_size, num_parents)
