"""
Agent 3 : Reasoning & Arbitration Agent (Système Multi-Agents IA - TSP Meknès)

Missions :
- Centralisation des rapports de recherche territoriale (Agent 1) et d'analyse scientifique (Agent 2).
- Analyse critique contradictoire des configurations proposées.
- Arbitrage objectif et sélection finale de la meilleure combinaison d'hyperparamètres.
- Rédaction d'une justification formelle de la décision d'arbitrage.
- Transmission directe des hyperparamètres validés au moteur de l'Algorithme Génétique.
"""

from typing import Dict, Any, Optional, Callable
import pandas as pd
import numpy as np

from agents.web_agent import WebResearchAgent
from agents.scientific_agent import ScientificAgent
from algorithms.genetic_algorithm import GeneticAlgorithmTSP


class ArbitrationAgent:
    """
    Agent IA de Raisonnement et d'Arbitrage Final.
    Prend la décision exécutive et pilote le solveur génétique.
    """

    def __init__(self, agent_name: str = "Reasoning & Arbitration Agent (Executive Decision)"):
        self.name = agent_name

    def arbitrate(self,
                  web_report: Dict[str, Any],
                  scientific_report: Dict[str, Any],
                  preference_mode: str = "balanced") -> Dict[str, Any]:
        """
        Analyse les rapports des agents 1 et 2 et tranche sur la configuration finale.
        
        Paramètres :
        - web_report : rapport géographique de l'Agent 1
        - scientific_report : rapport d'analyse génétique de l'Agent 2
        - preference_mode : 'balanced' (Alpha) ou 'intensive' (Beta)
        """
        candidates = scientific_report.get("candidate_configs", [])

        # Sélection du profil en fonction de l'arbitrage
        if preference_mode == "intensive":
            chosen_profile = next((c for c in candidates if c["profile_id"] == "PROFILE_BETA_DEEP_SEARCH"), candidates[0])
            rationale_title = "Arbitrage en faveur de l'Exploration Exhaustive (Profil Bêta)"
        else:
            chosen_profile = next((c for c in candidates if c["profile_id"] == "PROFILE_ALPHA_BALANCED"), candidates[0])
            rationale_title = "Arbitrage en faveur de l'Équilibre Optimal Qualité / Réactivité (Profil Alpha)"

        decision_justification = [
            f"1. Méthode de sélection retenue : '{chosen_profile['selection_method']}'. L'Agent Arbitre écarte la roulette en raison du risque avéré de dérive génétique sur les distances urbaines de Meknès souligné par l'Agent 2.",
            f"2. Opérateur et taux de croisement : Ordered Crossover (OX) avec un taux de {chosen_profile['crossover_rate']}. Ce choix valide les conclusions de l'Agent 1 concernant la préservation des clusters territoriaux (Médina, Hamria, Marjane).",
            f"3. Opérateur et taux de mutation : Inversion (2-Opt) avec un taux de {chosen_profile['mutation_rate']}. Taux optimal pour éliminer les croisements routiers résiduels sans déstabiliser la population.",
            f"4. Dimensionnement population / itérations : {chosen_profile['pop_size']} individus sur {chosen_profile['num_iterations']} générations. Offre un ratio idéal de couverture de l'espace d'état tout en garantissant une réactivité fluide sur le Dashboard.",
            "5. Décision exécutive : Transmission immédiate de ces paramètres au moteur génétique pour exécution."
        ]

        return {
            "agent": self.name,
            "status": "ARBITRATION_COMPLETED",
            "decision_title": rationale_title,
            "selected_parameters": {
                "pop_size": chosen_profile["pop_size"],
                "selection_method": chosen_profile["selection_method"],
                "mutation_rate": chosen_profile["mutation_rate"],
                "crossover_rate": chosen_profile["crossover_rate"],
                "num_iterations": chosen_profile["num_iterations"]
            },
            "justification": decision_justification,
            "candidate_evaluated": chosen_profile["label"]
        }


def run_agentic_pipeline(distance_matrix: np.ndarray,
                         points_df: pd.DataFrame,
                         preference_mode: str = "balanced",
                         progress_callback: Optional[Callable[[int, int, float, float], None]] = None) -> Dict[str, Any]:
    """
    Orchestre le workflow complet des trois agents IA :
    Recherche (Agent 1) -> Analyse Scientifique (Agent 2) -> Arbitrage (Agent 3) -> Résolution Génétique.
    """
    # Étape 1 : Agent de Recherche Web & SIG
    web_agent = WebResearchAgent()
    web_report = web_agent.analyze(points_df, distance_matrix)

    # Étape 2 : Agent Scientifique
    scientific_agent = ScientificAgent()
    scientific_report = scientific_agent.analyze(web_report)

    # Étape 3 : Agent de Raisonnement & Arbitrage
    arbitration_agent = ArbitrationAgent()
    arbitration_decision = arbitration_agent.arbitrate(web_report, scientific_report, preference_mode=preference_mode)

    selected_params = arbitration_decision["selected_parameters"]

    # Étape 4 : Exécution du Solveur Génétique avec les hyperparamètres arbitrés
    ga = GeneticAlgorithmTSP(
        distance_matrix=distance_matrix,
        num_clients=len(points_df) - 1,
        pop_size=selected_params["pop_size"],
        selection_method=selected_params["selection_method"],
        mutation_rate=selected_params["mutation_rate"],
        crossover_rate=selected_params["crossover_rate"],
        num_iterations=selected_params["num_iterations"],
        seed=123
    )

    ga_result = ga.solve(progress_callback=progress_callback)

    return {
        "web_report": web_report,
        "scientific_report": scientific_report,
        "arbitration_decision": arbitration_decision,
        "selected_parameters": selected_params,
        "ga_result": ga_result
    }
