"""
Opérateurs de mutation pour le TSP :
1. Inversion Mutation (équivalent génétique du mouvement 2-Opt)
2. Swap Mutation (échange de deux villes)
3. Scramble Mutation (mélange d'un sous-segment)
"""

import random
from typing import List


def swap_mutation(individual: List[int]) -> List[int]:
    """
    Échange aléatoirement la position de deux villes dans le chromosome.
    """
    n = len(individual)
    if n < 2:
        return individual.copy()

    mutated = individual.copy()
    i, j = random.sample(range(n), 2)
    mutated[i], mutated[j] = mutated[j], mutated[i]
    return mutated


def inversion_mutation(individual: List[int]) -> List[int]:
    """
    Inversion Mutation (2-Opt génétique) :
    Sélectionne deux points de coupure et inverse l'ordre des villes entre ces deux points.
    Très efficace pour décroiser les arêtes dans les tournées TSP.
    """
    n = len(individual)
    if n < 2:
        return individual.copy()

    mutated = individual.copy()
    i, j = sorted(random.sample(range(n), 2))
    mutated[i:j+1] = reversed(mutated[i:j+1])
    return mutated


def scramble_mutation(individual: List[int]) -> List[int]:
    """
    Scramble Mutation :
    Sélectionne une sous-séquence et mélange aléatoirement les villes à l'intérieur.
    """
    n = len(individual)
    if n < 2:
        return individual.copy()

    mutated = individual.copy()
    i, j = sorted(random.sample(range(n), 2))
    sub = mutated[i:j+1]
    random.shuffle(sub)
    mutated[i:j+1] = sub
    return mutated


def mutate(individual: List[int],
           mutation_rate: float,
           method: str = "inversion") -> List[int]:
    """
    Applique la mutation avec une probabilité 'mutation_rate'.
    Si le tirage aléatoire est inférieur ou égal à mutation_rate, l'opérateur de mutation s'applique.
    """
    if random.random() > mutation_rate:
        return individual.copy()

    normalized = method.lower()
    if "swap" in normalized:
        return swap_mutation(individual)
    elif "scramble" in normalized:
        return scramble_mutation(individual)
    else:
        # Inversion (2-Opt) par défaut pour ses performances remarquables sur le TSP
        return inversion_mutation(individual)
