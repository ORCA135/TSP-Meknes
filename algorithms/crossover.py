"""
Opérateurs de croisement (Crossover) adaptés aux permutations pour le TSP :
1. Ordered Crossover (OX1 - Croisement ordonné de Davis)
2. Partially Mapped Crossover (PMX - Croisement partiellement cartographié)
"""

import random
from typing import List, Tuple


def ordered_crossover_ox(parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
    """
    Ordered Crossover (OX1) pour permutations TSP.
    Préserve l'ordre relatif et la sous-séquence des villes.
    
    Fonctionnement :
    1. Sélection de deux points de coupure aléatoires [start, end].
    2. Copie du segment parent1[start:end] directement dans l'enfant 1.
    3. Remplissage des positions restantes à partir du parent 2 dans l'ordre séquentiel,
       en sautant les villes déjà présentes.
    4. Répétition symétrique pour l'enfant 2.
    """
    n = len(parent1)
    if n < 2:
        return parent1.copy(), parent2.copy()

    # Sélection de deux indices de coupure
    i, j = sorted(random.sample(range(n), 2))
    j += 1  # Pour inclure l'indice supérieur

    def _create_child(p1: List[int], p2: List[int]) -> List[int]:
        child = [-1] * n
        # Copie du segment central
        child[i:j] = p1[i:j]
        copied_set = set(p1[i:j])

        # Remplissage circulaire depuis p2
        p2_idx = 0
        for pos in range(n):
            if child[pos] == -1:
                while p2[p2_idx] in copied_set:
                    p2_idx += 1
                child[pos] = p2[p2_idx]
                p2_idx += 1
        return child

    child1 = _create_child(parent1, parent2)
    child2 = _create_child(parent2, parent1)

    return child1, child2


def pmx_crossover(parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
    """
    Partially Mapped Crossover (PMX) pour permutations TSP.
    Préserve les positions absolues des villes en établissant une table de correspondance.
    """
    n = len(parent1)
    if n < 2:
        return parent1.copy(), parent2.copy()

    i, j = sorted(random.sample(range(n), 2))
    j += 1

    def _create_pmx(p1: List[int], p2: List[int]) -> List[int]:
        child = [-1] * n
        child[i:j] = p1[i:j]

        # Table de correspondance p1 -> p2 dans le segment
        for pos in range(i, j):
            val2 = p2[pos]
            if val2 not in child[i:j]:
                current_val = val2
                while True:
                    idx_in_p1 = p1.index(current_val)
                    if not (i <= idx_in_p1 < j):
                        child[idx_in_p1] = val2
                        break
                    current_val = p2[idx_in_p1]

        # Remplir le reste avec p2
        for pos in range(n):
            if child[pos] == -1:
                child[pos] = p2[pos]

        return child

    return _create_pmx(parent1, parent2), _create_pmx(parent2, parent1)


def crossover(parent1: List[int],
              parent2: List[int],
              crossover_rate: float,
              method: str = "OX") -> Tuple[List[int], List[int]]:
    """
    Applique le croisement entre deux parents selon le taux de croisement (crossover_rate).
    Si le tirage dépasse le taux, les parents sont transmis intacts (clones).
    """
    if random.random() > crossover_rate:
        return parent1.copy(), parent2.copy()

    if method.upper() == "PMX":
        return pmx_crossover(parent1, parent2)
    else:
        return ordered_crossover_ox(parent1, parent2)
