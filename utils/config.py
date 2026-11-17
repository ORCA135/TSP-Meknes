"""
Configuration centrale pour TSP Meknès.
Définit les constantes, chemins, paramètres par défaut et coordonnées de référence.
"""

from pathlib import Path

# Chemins du projet
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
POINTS_CSV = DATA_DIR / "points_meknes.csv"
DISTANCE_MATRIX_CSV = DATA_DIR / "distance_matrix.csv"

# Coordonnées géographiques de référence - Meknès, Maroc
MEKNES_CENTER_LAT = 33.8938
MEKNES_CENTER_LON = -5.5516

# Entrepôt central (Depot Logistique / Hub Central Meknès - Ville Nouvelle / Gare)
DEPOT_ID = 0
DEPOT_NAME = "Entrepôt Central - Hub Logistique Hamria"
DEPOT_LAT = 33.8992
DEPOT_LON = -5.5425

# Paramètres de l'Algorithme Génétique autorisés
POPULATION_SIZES = [50, 100, 500]
SELECTION_METHODS = ["Roulette Wheel Selection", "Tournament Selection"]
MUTATION_RATES = [0.2, 0.5, 0.8]
CROSSOVER_RATES = [0.2, 0.5, 0.8]
ITERATION_OPTIONS = [100, 500, 1000]

# Valeurs par défaut
DEFAULT_POP_SIZE = 100
DEFAULT_SELECTION = "Tournament Selection"
DEFAULT_MUTATION_RATE = 0.2
DEFAULT_CROSSOVER_RATE = 0.8
DEFAULT_ITERATIONS = 500
DEFAULT_TOURNAMENT_SIZE = 5
DEFAULT_ELITISM_COUNT = 2

# Configuration API OSRM
OSRM_CAR_URL = "https://router.project-osrm.org"
OSRM_TABLE_URL = f"{OSRM_CAR_URL}/table/v1/driving"
OSRM_ROUTE_URL = f"{OSRM_CAR_URL}/route/v1/driving"
OSRM_TIMEOUT = 10  # secondes
OSRM_MAX_COORDINATES_PER_REQUEST = 45  # Sécurité pour éviter les erreurs 414 URI Too Long
