"""
Calcul de la fitness et de la distance totale pour le problème du voyageur de commerce (TSP).
"""

from typing import List, Sequence, Tuple
import numpy as np


def compute_tour_distance(chromosome: Sequence[int],
                          distance_matrix: np.ndarray,
                          depot_id: int = 0) -> float:
    """
    Calcule la distance totale parcourue (en kilomètres) pour un chromosome donné.
    Le chromosome représente l'ordre des clients visités (indices 1..N).
    Le circuit commence à l'entrepôt (depot_id) et se termine à l'entrepôt.

    Total Distance = dist(depot, c_1) + sum_{i=1}^{N-1} dist(c_i, c_{i+1}) + dist(c_N, depot)
    """
    if len(chromosome) == 0:
        return 0.0

    total_dist = 0.0
    current_node = depot_id

    for next_node in chromosome:
        total_dist += distance_matrix[current_node, next_node]
        current_node = next_node

    # Retour à l'entrepôt
    total_dist += distance_matrix[current_node, depot_id]

    return float(total_dist)


def compute_fitness(distance: float) -> float:
    """
    Convertit la distance totale en valeur de fitness pour la maximisation :
    Fitness = 1.0 / distance (avec protection contre la division par zéro).
    Plus la distance est petite, plus la fitness est élevée.
    """
    if distance <= 1e-9:
        return 1e9
    return 1.0 / distance


def evaluate_population(population: List[List[int]],
                        distance_matrix: np.ndarray,
                        depot_id: int = 0) -> Tuple[np.ndarray, np.ndarray]:
    """
    Évalue une population entière d'individus.
    Retourne :
    - distances : array 1D des distances totales de chaque individu (en km)
    - fitnesses : array 1D des scores de fitness correspondants
    """
    distances = np.array([
        compute_tour_distance(ind, distance_matrix, depot_id)
        for ind in population
    ], dtype=np.float64)

    fitnesses = 1.0 / np.maximum(distances, 1e-9)
    return distances, fitnesses
