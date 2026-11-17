"""
Fonctions utilitaires pour le projet TSP Meknès :
- Calcul de distance Haversine
- Projection géographique vers plan cartésien 2D (km)
- Validation et formatage des chromosomes TSP
- Métriques et formatage d'affichage
"""

import math
from typing import List, Tuple
from utils.config import MEKNES_CENTER_LAT, MEKNES_CENTER_LON, DEPOT_ID


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcule la distance orthodromique (Haversine) en kilomètres entre deux coordonnées GPS.
    """
    R = 6371.0  # Rayon moyen de la Terre en km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def gps_to_cartesian_km(lat: float, lon: float,
                        center_lat: float = MEKNES_CENTER_LAT,
                        center_lon: float = MEKNES_CENTER_LON) -> Tuple[float, float]:
    """
    Projette des coordonnées GPS (lat, lon) vers un repère cartésien 2D local (X, Y) en kilomètres,
    centré sur la ville de Meknès (projection équirectangulaire locale).
    - X : est-ouest en km
    - Y : nord-sud en km
    """
    R = 6371.0
    lat_rad = math.radians(center_lat)
    x = math.radians(lon - center_lon) * math.cos(lat_rad) * R
    y = math.radians(lat - center_lat) * R
    return x, y


def format_chromosome_display(tour: List[int], max_items: int = 12) -> str:
    """
    Formate un chromosome en chaîne lisible avec flèches :
    Exemple : 'Entrepôt → P12 → P05 → ... → P40 → Entrepôt'
    """
    if not tour:
        return "Circuit vide"

    # Vérifie si le tour commence et finit par l'entrepôt
    items = []
    for idx in tour:
        if idx == DEPOT_ID:
            items.append("Entrepôt")
        else:
            items.append(f"P{idx:02d}")

    if len(items) <= max_items:
        return " → ".join(items)
    else:
        half = max_items // 2
        head = " → ".join(items[:half])
        tail = " → ".join(items[-half:])
        return f"{head} → ... ({len(items)-max_items} points) ... → {tail}"


def validate_tsp_solution(tour: List[int], num_clients: int = 40) -> Tuple[bool, str]:
    """
    Vérifie la validité mathématique et opérationnelle d'un circuit TSP :
    - Commence et finit à l'entrepôt (0).
    - Contient exactement num_clients clients distincts (1..num_clients).
    - Aucun point manquant, aucun doublon.
    """
    if not tour:
        return False, "Le tour est vide."

    if tour[0] != DEPOT_ID or tour[-1] != DEPOT_ID:
        return False, f"Le circuit doit débuter et se terminer à l'entrepôt ({DEPOT_ID})."

    clients_in_tour = tour[1:-1]
    expected_clients = set(range(1, num_clients + 1))
    actual_clients = set(clients_in_tour)

    if len(clients_in_tour) != num_clients:
        return False, f"Nombre de points clients incorrect : {len(clients_in_tour)} au lieu de {num_clients}."

    if len(actual_clients) != num_clients:
        duplicates = len(clients_in_tour) - len(actual_clients)
        return False, f"Présence de {duplicates} point(s) dupliqué(s) dans le circuit."

    if actual_clients != expected_clients:
        missing = expected_clients - actual_clients
        return False, f"Points manquants : {sorted(list(missing))}."

    return True, "Solution TSP valide."
