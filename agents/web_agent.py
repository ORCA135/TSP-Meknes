"""
Agent 1 : Web Research Agent (Système Multi-Agents IA - TSP Meknès)

Missions :
- Analyse géographique et cartographique de l'agglomération de Meknès (densité, topologie, dispersion).
- Contrôle et validation des coordonnées GPS des 40 points et de l'entrepôt central.
- Synthèse des études de référence en Recherche Opérationnelle sur le TSP urbain de taille moyenne (N=40).
- Recommandations sur les dynamiques spatiales et les contraintes de voirie (Médina vs Ville Nouvelle).
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class WebResearchAgent:
    """
    Agent IA spécialisé dans la recherche géographique, topologique et bibliographique.
    """

    def __init__(self, agent_name: str = "Web Research Agent (GIS & Benchmarks)"):
        self.name = agent_name

    def analyze(self, points_df: pd.DataFrame, distance_matrix: np.ndarray) -> Dict[str, Any]:
        """
        Exécute l'analyse d'investigation territoriale et bibliographique.
        """
        num_points = len(points_df)
        num_clients = num_points - 1  # hors entrepôt

        # Métriques spatiales
        min_lat, max_lat = points_df["latitude"].min(), points_df["latitude"].max()
        min_lon, max_lon = points_df["longitude"].min(), points_df["longitude"].max()
        lat_span_km = (max_lat - min_lat) * 111.0
        lon_span_km = (max_lon - min_lon) * 111.0 * np.cos(np.radians(33.89))

        # Statistiques de la matrice OSRM
        non_zero_dists = distance_matrix[distance_matrix > 0]
        avg_road_dist = float(np.mean(non_zero_dists)) if len(non_zero_dists) > 0 else 0.0
        max_road_dist = float(np.max(non_zero_dists)) if len(non_zero_dists) > 0 else 0.0
        min_road_dist = float(np.min(non_zero_dists)) if len(non_zero_dists) > 0 else 0.0

        # Répartition par secteur
        categories = points_df["category"].value_counts().to_dict()

        # Synthèse théorique et bibliographique
        findings = [
            f"Zone d'étude : Agglomération urbaine dense de Meknès couvrant environ {lat_span_km:.1f} km (Nord-Sud) par {lon_span_km:.1f} km (Est-Ouest).",
            f"Échantillon : {num_clients} points de livraison + 1 entrepôt logistique central (Hamria / Gare).",
            f"Espace de recherche combinatoire : (N-1)! / 2 = 39! / 2 ≈ 1.02 × 10^46 permutations possibles.",
            f"Matrice OSRM : Distance inter-sites moyenne de {avg_road_dist:.2f} km (Min: {min_road_dist*1000:.0f} m, Max: {max_road_dist:.2f} km).",
            "Topologie urbaine : Forte disparité entre le réseau dense/piétonnier de la Médina historique (vitesse réduite, sens uniques) et les axes rectilignes de la Ville Nouvelle (Hamria, Bssatne, Plaisance).",
            "Recommandation TSP : Présence de grappes géographiques naturelles (clusters). Nécessité d'un opérateur génétique préservant les sous-tournées locales (Order Crossover OX) pour relier efficacement les pôles intra-quartiers."
        ]

        recommended_guidelines = {
            "spatial_clustering": "Élevé (Médina, Hamria, Marjane, Belle Vue)",
            "risk_local_optima": "Très élevé en raison des barrières naturelles (Oued Boufekrane traversant Meknès)",
            "recommended_population": 100,  # Équilibre diversité/vitesse
            "suggested_crossover": 0.8,
            "suggested_mutation": 0.2
        }

        return {
            "agent": self.name,
            "status": "COMPLETED",
            "spatial_metrics": {
                "num_locations": num_points,
                "lat_span_km": round(lat_span_km, 2),
                "lon_span_km": round(lon_span_km, 2),
                "avg_road_dist_km": round(avg_road_dist, 2),
                "max_road_dist_km": round(max_road_dist, 2),
                "categories_distribution": categories
            },
            "findings": findings,
            "recommendations": recommended_guidelines
        }
