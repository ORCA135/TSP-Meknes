# 🚚 TSP MEKNÈS – Intelligent Urban Route Optimization
### Application avancée d'optimisation de tournées par Algorithmes Génétiques, Optuna et IA Agentique

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B.svg)](https://streamlit.io/)
[![OSRM](https://img.shields.io/badge/OSRM-Routing%20Engine-00C853.svg)](http://project-osrm.org/)
[![Optuna](https://img.shields.io/badge/Optuna-Bayesian%20TPE-8A2BE2.svg)](https://optuna.org/)

---

## 📌 Présentation du Projet

Le projet **TSP MEKNÈS** est une solution logicielle d'ingénierie et de recherche opérationnelle dédiée à la résolution du **Problème du Voyageur de Commerce (Traveling Salesperson Problem - TSP)** appliqué au tissu urbain dense de la ville de **Meknès, Maroc**.

L'application calcule et visualise le circuit routier optimal reliant un **entrepôt logistique central (Hub Hamria)** et **40 points d'intérêt réels** (monuments historiques de la Médina, gares ferroviaires, hôpitaux, universités et zones commerciales) en minimisant la distance routière totale via le réseau routier d'**OpenStreetMap** et le moteur de calcul d'itinéraires **OSRM (Open Source Routing Machine)**.

L'espace d'état combinatoire pour 40 points est vertigineux :
$$\frac{(N-1)!}{2} = \frac{39!}{2} \approx 1.02 \times 10^{46} \text{ permutations possibles}$$

---

## 🏗️ Architecture en 4 Quadrants (Dashboard)

L'interface graphique est conçue comme un tableau de bord de décision moderne divisé en 4 quadrants équilibrés :

```
┌───────────────────────────────────────┬───────────────────────────────────────┐
│ QUADRANT 1 : Configuration & Modes    │ QUADRANT 2 : Analyse & Performance    │
│ • Définition du problème (Meknès)     │ • KPI Cards (Best, Initial, % Gain)   │
│ • Réglage hyperparamètres GA          │ • Courbe de convergence interactive   │
│ • Bouton B1 : MANUAL MODE             │ • Chromosome solution formaté         │
│ • Bouton B2 : OPTUNA OPTIMIZATION     │ • Badge de conformité TSP strict      │
│ • Bouton B3 : AGENTIC AI MODE         │ • Rapport d'arbitrage / essais Optuna │
├───────────────────────────────────────┼───────────────────────────────────────┤
│ QUADRANT 3 : Visualisation Cartésienne│ QUADRANT 4 : Cartographie Réelle OSRM │
│ • Plan 2D orthonormé (X, Y en km)     │ • Fond cartographique OpenStreetMap   │
│ • Entrepôt central en étoile rouge (★)│ • 40 points numérotés avec métadonnées│
│ • Marqueurs circulaires numérotés P01 │ • Tracé routier précis via OSRM       │
│ • Tracé vectoriel du circuit optimisé │ • Feuille de route détaillée segments │
└───────────────────────────────────────┴───────────────────────────────────────┘
```

---

## 🚀 Les Trois Modes d'Optimisation

### 🔵 Mode B1 : Manual Mode
L'utilisateur configure manuellement les hyperparamètres de l'Algorithme Génétique :
- **Population Size** : 50, 100, 500
- **Selection Method** : *Roulette Wheel Selection* (Roue biaisée) ou *Tournament Selection* (Sélection par tournoi, $k=5$)
- **Mutation Rate** : 0.2, 0.5, 0.8
- **Crossover Rate** : 0.2, 0.5, 0.8
- **Iterations** : 100, 500, 1000
- **Élitisme** : Conservation des meilleurs individus pour assurer la monotonie de convergence.

### 🟣 Mode B2 : Optuna Optimization
Recherche bayésienne automatique par estimateur de mélange de Parzen (**Tree-structured Parzen Estimator - TPE**) :
- Explore intelligemment l'espace continu et discret des hyperparamètres.
- Maximise le taux d'amélioration et minimise la distance totale en kilomètres.
- Fournit l'historique de chaque essai (*trial*), les temps d'exécution et la configuration championne.

### 🟢 Mode B3 : Agentic AI Mode (Système Multi-Agents Collaboratif)
Système d'intelligence artificielle à 3 agents experts fonctionnant en cascade :
1. **Agent 1 : Web Research Agent (GIS & Benchmarks)**
   - Analyse la topologie de Meknès (dispersion Médina vs Hamria, barrière naturelle d'Oued Boufekrane).
   - Extrait les statistiques de la matrice de distances (moyenne, écart-type, extrêmes).
   - Identifie la formation de grappes spatiales (*clustering*).
2. **Agent 2 : Scientific Agent (Genetic Theory & Operators)**
   - Étudie théoriquement les opérateurs de croisement (Ordered Crossover OX1 de Davis) et de mutation (Inversion 2-Opt).
   - Compare la pression sélective du Tournoi versus Roulette.
   - Soumet trois profils scientifiques argumentés (*Alpha Équilibré*, *Bêta Deep Search*, *Gamma Diversité*).
3. **Agent 3 : Reasoning & Arbitration Agent (Executive Decision)**
   - Analyse contradictoirement les rapports des agents 1 et 2.
   - Émet un avis d'arbitrage motivé pour sélectionner le profil optimal.
   - Transmet les paramètres retenus au moteur génétique et pilote la convergence.

---

## 📁 Organisation du Code Source

```text
TSP_Meknes/
│
├── app.py                      # Application principale Streamlit Dashboard
├── requirements.txt            # Dépendances Python certifiées
├── README.md                   # Documentation technique & académique
│
├── data/
│   ├── points_meknes.csv       # 40 POIs réels de Meknès + Entrepôt Central
│   └── distance_matrix.csv     # Matrice réelle 41x41 OSRM Driving Table
│
├── algorithms/
│   ├── genetic_algorithm.py    # Moteur d'évolution génétique et élitisme
│   ├── selection.py            # Roue de roulette & Sélection par tournoi
│   ├── crossover.py            # Ordered Crossover (OX1) & PMX
│   ├── mutation.py             # Inversion 2-Opt, Swap, Scramble
│   └── fitness.py              # Calcul de distance routière et fonction objectif
│
├── optimization/
│   └── optuna_optimizer.py     # Optimiseur bayésien TPE avec Optuna
│
├── agents/
│   ├── web_agent.py            # Agent IA 1 : Recherche géographique & cartographique
│   ├── scientific_agent.py     # Agent IA 2 : Analyse scientifique & convergence
│   └── arbitration_agent.py    # Agent IA 3 : Raisonnement, arbitrage & pipeline
│
├── routing/
│   ├── osrm_client.py          # Client API OSRM (Table & Route Driving Services)
│   ├── distance_matrix.py      # Gestionnaire de matrice de distances avec cache et fallback
│   └── map_visualization.py    # Générateur de carte interactive Folium
│
├── visualization/
│   ├── convergence.py          # Tracé Plotly de convergence (Best vs Mean)
│   └── cartesian_plot.py       # Projection 2D cartésienne interactive Plotly
│
└── utils/
    ├── config.py               # Constantes, coordonnées de Meknès & paramètres
    └── helpers.py              # Haversine, projection cartésienne & validation TSP
```

---

## 🛠️ Installation et Exécution

### 1. Prérequis
- Python 3.10, 3.11, 3.12, 3.13 ou 3.14.
- Connexion Internet (pour la première requête OSRM et les fonds de carte OpenStreetMap ; un mode démonstration hors-ligne automatique est intégré).

### 2. Installation de l'environnement virtuel
```bash
# Cloner ou se positionner dans le répertoire du projet
cd TSP-Meknes

# Créer un environnement virtuel
python -m venv .venv

# Activer l'environnement virtuel
# Sur Windows (PowerShell) :
.\.venv\Scripts\Activate.ps1
# Sur Linux / macOS :
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Lancement de l'application

#### A. Application Bureau Tkinter & Folium (Recommandée) :
```bash
python TP.py
# ou directement :
python gui_tkinter.py
```
Cette commande ouvre la fenêtre bureau native **Tkinter** intégrant les 4 quadrants, les figures Matplotlib interactives, la synchronisation des threads et la cartographie **Folium**.

#### B. Dashboard Web Streamlit :
```bash
streamlit run app.py
# ou :
python TP.py --web
```
L'interface s'ouvre dans votre navigateur web à l'adresse : `http://localhost:8501`.

---

## 🧪 Tests et Validation Mathématique

Chaque solution générée est automatiquement contrôlée par un validateur formel vérifiant les contraintes strictes du TSP :
- Le circuit débute à l'entrepôt central (indice `0`).
- Chaque client `1` à `40` est visité **exactement une fois**.
- Le circuit se clôture obligatoirement à l'entrepôt central.
- Aucune ville n'est omise, aucune ville n'est dupliquée.
- Longueur totale du chromosome : $N + 1 = 42$ nœuds.

Pour tester les composants unitaires en ligne de commande :
```bash
# Test du solveur génétique
python -c "from routing.distance_matrix import load_or_compute_distance_matrix; from algorithms.genetic_algorithm import GeneticAlgorithmTSP; m, _, _ = load_or_compute_distance_matrix(); ga = GeneticAlgorithmTSP(m); print(ga.solve()['best_distance'], 'km')"

# Test du pipeline Multi-Agents IA
python -c "from routing.distance_matrix import load_or_compute_distance_matrix, load_meknes_points; from agents.arbitration_agent import run_agentic_pipeline; m, _, _ = load_or_compute_distance_matrix(); df = load_meknes_points(); print(run_agentic_pipeline(m, df)['arbitration_decision']['decision_title'])"
```

---

## 🎓 Crédits & Cadre Académique
Projet réalisé dans le cadre d'études avancées en **Recherche Opérationnelle**, **Optimisation Combinatoire** et **Intelligence Artificielle Distribuée**.
- **Terrain d'étude :** Meknès, Maroc.
- **Moteur Cartographique :** OpenStreetMap & Project OSRM.
- **Framework d'optimisation :** Optuna & Algorithmes Évolutionnaires.
