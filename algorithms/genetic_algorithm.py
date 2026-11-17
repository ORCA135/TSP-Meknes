"""
Moteur principal de l'Algorithme Génétique pour le TSP (TSP Meknès).
Implémente le cycle évolutif complet :
- Initialisation de la population (permutations aléatoires)
- Évaluation de la fitness (basée sur la matrice de distances réelles)
- Élitisme (conservation des meilleurs individus)
- Sélection (Tournoi ou Roue de roulette)
- Croisement (Ordered Crossover OX)
- Mutation (Inversion 2-Opt / Swap)
- Callback de progression pour interface temps réel
"""

import time
import random
from typing import List, Dict, Any, Callable, Optional, Tuple
import numpy as np

from algorithms.fitness import evaluate_population, compute_tour_distance
from algorithms.selection import select_parents
from algorithms.crossover import crossover
from algorithms.mutation import mutate
from utils.helpers import validate_tsp_solution


class GeneticAlgorithmTSP:
    """
    Solveur TSP par Algorithme Génétique.
    """

    def __init__(self,
                 distance_matrix: np.ndarray,
                 num_clients: int = 40,
                 depot_id: int = 0,
                 pop_size: int = 100,
                 selection_method: str = "Tournament Selection",
                 mutation_rate: float = 0.2,
                 crossover_rate: float = 0.8,
                 num_iterations: int = 500,
                 tournament_size: int = 5,
                 elitism_count: int = 2,
                 seed: Optional[int] = None):

        self.distance_matrix = distance_matrix
        self.num_clients = num_clients
        self.depot_id = depot_id
        self.pop_size = pop_size
        self.selection_method = selection_method
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.num_iterations = num_iterations
        self.tournament_size = tournament_size
        self.elitism_count = max(1, min(elitism_count, pop_size // 4))

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

    def _initialize_population(self) -> List[List[int]]:
        """
        Génère une population initiale de 'pop_size' permutations des clients 1..N.
        Inclut également une heuristique du plus proche voisin (Nearest Neighbor) pour amorcer la population.
        """
        population: List[List[int]] = []
        base_clients = list(range(1, self.num_clients + 1))

        # 1. Insertion d'une solution gloutonne (Plus Proche Voisin) pour accélérer la convergence
        nn_individual = self._nearest_neighbor_tour()
        if nn_individual:
            population.append(nn_individual)

        # 2. Complétion avec des permutations aléatoires diversifiées
        while len(population) < self.pop_size:
            ind = base_clients.copy()
            random.shuffle(ind)
            population.append(ind)

        return population

    def _nearest_neighbor_tour(self) -> List[int]:
        """
        Construit un tour initial selon l'heuristique gloutonne du plus proche voisin.
        """
        unvisited = set(range(1, self.num_clients + 1))
        current = self.depot_id
        tour = []

        while unvisited:
            next_city = min(unvisited, key=lambda c: self.distance_matrix[current, c])
            tour.append(next_city)
            unvisited.remove(next_city)
            current = next_city

        return tour

    def solve(self, progress_callback: Optional[Callable[[int, int, float, float], None]] = None) -> Dict[str, Any]:
        """
        Exécute l'algorithme génétique sur 'num_iterations' générations.
        
        Paramètres :
        - progress_callback : fonction appelée à chaque génération avec (gen, max_gen, best_dist, avg_dist)

        Retourne un dictionnaire contenant :
        - best_tour : chromosome complet avec entrepôt [0, c1, ..., c40, 0]
        - best_distance : float (km)
        - initial_distance : float (km)
        - improvement_percent : float (%)
        - history_best : List[float]
        - history_avg : List[float]
        - execution_time : float (secondes)
        - generations_run : int
        - is_valid : bool
        - validation_message : str
        """
        start_time = time.time()

        # 1. Initialisation
        population = self._initialize_population()
        distances, fitnesses = evaluate_population(population, self.distance_matrix, self.depot_id)

        # Meilleur initial
        best_idx = int(np.argmin(distances))
        best_individual = population[best_idx].copy()
        best_distance = float(distances[best_idx])
        initial_distance = best_distance

        history_best: List[float] = [best_distance]
        history_avg: List[float] = [float(np.mean(distances))]

        if progress_callback:
            progress_callback(0, self.num_iterations, best_distance, history_avg[-1])

        # 2. Boucle évolutive principale
        for gen in range(1, self.num_iterations + 1):
            # A. Tri des individus pour l'élitisme
            sorted_indices = np.argsort(distances)
            new_population: List[List[int]] = []

            # Conservation des élites
            for e_idx in sorted_indices[:self.elitism_count]:
                new_population.append(population[e_idx].copy())

            # B. Sélection des parents
            num_needed = self.pop_size - self.elitism_count
            parents = select_parents(
                population=population,
                distances=distances,
                fitnesses=fitnesses,
                method=self.selection_method,
                num_parents=num_needed,
                tournament_size=self.tournament_size
            )

            # C. Croisement & Mutation
            for i in range(0, num_needed, 2):
                p1 = parents[i]
                p2 = parents[(i + 1) % len(parents)]

                c1, c2 = crossover(p1, p2, self.crossover_rate, method="OX")

                # Mutation
                c1 = mutate(c1, self.mutation_rate, method="inversion")
                new_population.append(c1)

                if len(new_population) < self.pop_size:
                    c2 = mutate(c2, self.mutation_rate, method="inversion")
                    new_population.append(c2)

            population = new_population[:self.pop_size]

            # D. Évaluation
            distances, fitnesses = evaluate_population(population, self.distance_matrix, self.depot_id)

            cur_best_idx = int(np.argmin(distances))
            cur_best_dist = float(distances[cur_best_idx])
            cur_avg_dist = float(np.mean(distances))

            if cur_best_dist < best_distance:
                best_distance = cur_best_dist
                best_individual = population[cur_best_idx].copy()

            history_best.append(best_distance)
            history_avg.append(cur_avg_dist)

            # Mise à jour du callback (fréquence adaptée)
            if progress_callback and (gen % max(1, self.num_iterations // 50) == 0 or gen == self.num_iterations):
                progress_callback(gen, self.num_iterations, best_distance, cur_avg_dist)

        execution_time = time.time() - start_time

        # Circuit complet avec l'entrepôt au départ et à l'arrivée
        complete_tour = [self.depot_id] + best_individual + [self.depot_id]

        # Validation formelle de la solution
        is_valid, val_msg = validate_tsp_solution(complete_tour, self.num_clients)

        improvement = 0.0
        if initial_distance > 0:
            improvement = ((initial_distance - best_distance) / initial_distance) * 100.0

        return {
            "best_tour": complete_tour,
            "best_chromosome_clients": best_individual,
            "best_distance": round(best_distance, 3),
            "initial_distance": round(initial_distance, 3),
            "improvement_percent": round(max(0.0, improvement), 2),
            "history_best": history_best,
            "history_avg": history_avg,
            "execution_time": round(execution_time, 3),
            "generations_run": self.num_iterations,
            "pop_size": self.pop_size,
            "selection_method": self.selection_method,
            "mutation_rate": self.mutation_rate,
            "crossover_rate": self.crossover_rate,
            "is_valid": is_valid,
            "validation_message": val_msg
        }
