"""
Client API pour le service de routage OSRM (Open Source Routing Machine) :
- Service Table OSRM : calcul de la matrice de distances routières réelles (en kilomètres).
- Service Route OSRM : calcul des itinéraires et géométries routières précises (GeoJSON polyline) pour la cartographie.
- Gestion robuste du mode hors-ligne, des erreurs réseau, du timeout et du rate-limiting.
"""

import time
from typing import List, Tuple, Dict, Any, Optional
import requests
import numpy as np

from utils.config import (
    OSRM_TABLE_URL,
    OSRM_ROUTE_URL,
    OSRM_TIMEOUT
)
from utils.helpers import haversine_distance


class OSRMClient:
    """
    Client HTTP pour interagir avec le serveur public OSRM ou un serveur local.
    """

    def __init__(self, timeout: int = OSRM_TIMEOUT):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "TSP-Meknes-Research-App/1.0 (academic/operational-research)"
        }

    def fetch_distance_matrix(self,
                              coordinates: List[Tuple[float, float]]) -> Tuple[Optional[np.ndarray], bool]:
        """
        Récupère la matrice de distances routières réelles (en km) pour une liste de coordonnées (lat, lon).
        Retourne :
        - matrix : np.ndarray (N x N) des distances en kilomètres
        - success : bool indiquant si l'API OSRM a répondu avec succès
        """
        n = len(coordinates)
        if n == 0:
            return None, False

        # OSRM attend le format : {lon},{lat};{lon},{lat}...
        coord_strings = [f"{lon:.6f},{lat:.6f}" for lat, lon in coordinates]
        coord_query = ";".join(coord_strings)
        url = f"{OSRM_TABLE_URL}/{coord_query}?annotations=distance"

        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "Ok" and "distances" in data:
                    raw_matrix = np.array(data["distances"], dtype=np.float64)
                    # OSRM retourne les distances en mètres -> conversion en kilomètres
                    km_matrix = raw_matrix / 1000.0
                    # Assurer que la diagonale est strictement 0.0
                    np.fill_diagonal(km_matrix, 0.0)
                    return km_matrix, True
        except Exception as e:
            # Erreur de connexion, timeout ou DNS -> mode dégradé
            pass

        return None, False

    def fetch_route_geometry(self,
                             coordinates: List[Tuple[float, float]]) -> Optional[Dict[str, Any]]:
        """
        Récupère l'itinéraire routier complet et les géométries détaillées (GeoJSON)
        suivant l'ordre des coordonnées fournies.
        """
        if len(coordinates) < 2:
            return None

        # OSRM route limite le nombre de waypoints par URL. Pour 41 points, l'URL fait environ 900 caractères.
        coord_strings = [f"{lon:.6f},{lat:.6f}" for lat, lon in coordinates]
        coord_query = ";".join(coord_strings)
        url = f"{OSRM_ROUTE_URL}/{coord_query}?overview=full&geometries=geojson&steps=true"

        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "Ok" and "routes" in data and len(data["routes"]) > 0:
                    route = data["routes"][0]
                    # geometry est un GeoJSON LineString (coordonnées [lon, lat])
                    return {
                        "distance_km": route["distance"] / 1000.0,
                        "duration_min": route["duration"] / 60.0,
                        "geometry": route["geometry"]["coordinates"],  # List of [lon, lat]
                        "legs": route.get("legs", [])
                    }
        except Exception:
            pass

        return None

    def compute_fallback_distance_matrix(self,
                                        coordinates: List[Tuple[float, float]],
                                        circuity_factor: float = 1.35) -> np.ndarray:
        """
        Génère une matrice de distances approchées réalistes en cas d'indisponibilité d'OSRM.
        Applique la distance Haversine multipliée par le facteur de sinuosité urbaine (circuity factor)
        typique des voiries de Meknès (1.30 à 1.40).
        """
        n = len(coordinates)
        matrix = np.zeros((n, n), dtype=np.float64)

        for i in range(n):
            lat1, lon1 = coordinates[i]
            for j in range(i + 1, n):
                lat2, lon2 = coordinates[j]
                d = haversine_distance(lat1, lon1, lat2, lon2) * circuity_factor
                matrix[i, j] = d
                matrix[j, i] = d

        return matrix
