"""
Gestionnaire de la matrice de distances réelles pour TSP Meknès.
Assure le chargement, la persistance dans data/distance_matrix.csv,
et la mise à jour via l'API OSRM avec bascule automatique en mode secours.
"""

from pathlib import Path
from typing import Tuple, List, Dict, Any
import pandas as pd
import numpy as np

from utils.config import POINTS_CSV, DISTANCE_MATRIX_CSV
from routing.osrm_client import OSRMClient


def load_meknes_points(csv_path: Path = POINTS_CSV) -> pd.DataFrame:
    """
    Charge les points géographiques réels de Meknès depuis le fichier CSV.
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"Le fichier des points {csv_path} est introuvable.")

    df = pd.read_csv(csv_path)
    return df


def load_or_compute_distance_matrix(csv_matrix_path: Path = DISTANCE_MATRIX_CSV,
                                    points_path: Path = POINTS_CSV,
                                    force_refresh: bool = False) -> Tuple[np.ndarray, bool, str]:
    """
    Charge la matrice de distances depuis le cache CSV si disponible,
    ou interroge l'API OSRM. En cas d'échec réseau, bascule sur la matrice de secours réaliste.

    Retourne :
    - matrix : np.ndarray (41, 41)
    - is_live_osrm : bool (True si calculé en direct par OSRM ou chargé depuis un cache OSRM)
    - source_info : str décrivant l'origine de la matrice
    """
    points_df = load_meknes_points(points_path)
    n = len(points_df)
    coords = list(zip(points_df["latitude"].values, points_df["longitude"].values))

    # 1. Vérification du cache existant
    if not force_refresh and csv_matrix_path.exists():
        try:
            cached_matrix = np.loadtxt(csv_matrix_path, delimiter=",")
            if cached_matrix.shape == (n, n):
                return cached_matrix, True, "Matrice chargée depuis le cache persistant (OSRM)"
        except Exception:
            pass

    # 2. Tentative via API OSRM
    client = OSRMClient()
    matrix, success = client.fetch_distance_matrix(coords)

    if success and matrix is not None:
        # Sauvegarde dans le fichier CSV
        csv_matrix_path.parent.mkdir(parents=True, exist_ok=True)
        np.savetxt(csv_matrix_path, matrix, delimiter=",", fmt="%.4f")
        return matrix, True, "Matrice calculée en direct via l'API OSRM Driving Table"

    # 3. Fallback : calcul basé sur le facteur de sinuosité urbaine (1.35)
    fallback_matrix = client.compute_fallback_distance_matrix(coords, circuity_factor=1.35)
    csv_matrix_path.parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(csv_matrix_path, fallback_matrix, delimiter=",", fmt="%.4f")

    return fallback_matrix, False, "Mode démonstration : Distances calculées via sinuosité urbaine calibrée (Meknès)"
