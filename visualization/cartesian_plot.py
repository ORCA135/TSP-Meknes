"""
Visualisation cartésienne 2D interactive du TSP Meknès :
- Projection géographique vers un plan cartésien local (X, Y) en kilomètres.
- Entrepôt central représenté par une étoile rouge remarquable (★).
- Points clients représentés par des marqueurs circulaires numérotés avec métadonnées.
- Tracé ordonné des segments du circuit optimal reliant l'entrepôt à tous les clients.
"""

from typing import List, Optional
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils.helpers import gps_to_cartesian_km
from utils.config import DEPOT_ID


def create_cartesian_tsp_plot(points_df: pd.DataFrame,
                             tour: Optional[List[int]] = None,
                             title: str = "Plan Cartésien 2D – Tournée Urbaine Meknès") -> go.Figure:
    """
    Génère la figure 2D cartésienne interactive Plotly.
    
    Paramètres :
    - points_df : DataFrame des 41 points (id, name, category, latitude, longitude, address)
    - tour : Liste ordonnée des indices [0, c1, ..., c40, 0]. Si None, affiche uniquement les points.
    """
    # Calcul des coordonnées cartésiennes en km pour chaque point
    xs, ys, names, categories, labels, ids = [], [], [], [], [], []

    # Dictionnaire de recherche rapide par ID
    points_dict = {}
    for _, row in points_df.iterrows():
        p_id = int(row["id"])
        x_km, y_km = gps_to_cartesian_km(row["latitude"], row["longitude"])
        points_dict[p_id] = {
            "x": x_km,
            "y": y_km,
            "name": row["name"],
            "category": row["category"],
            "address": row["address"],
            "lat": row["latitude"],
            "lon": row["longitude"]
        }

    fig = go.Figure()

    # 1. Tracé des arêtes du circuit (si tour fourni)
    if tour and len(tour) >= 2:
        tour_xs = [points_dict[node]["x"] for node in tour]
        tour_ys = [points_dict[node]["y"] for node in tour]

        # Ligne continue du circuit
        fig.add_trace(go.Scatter(
            x=tour_xs,
            y=tour_ys,
            mode="lines",
            name="Circuit TSP Optimisé",
            line=dict(color="#29B6F6", width=2.5),
            hoverinfo="skip"
        ))

        # Flèches / marqueurs directionnels discrets sur le circuit
        # Calcul des points médians pour visualiser le sens de parcours
        mid_xs = [(tour_xs[i] + tour_xs[i+1]) / 2 for i in range(len(tour_xs)-1)]
        mid_ys = [(tour_ys[i] + tour_ys[i+1]) / 2 for i in range(len(tour_ys)-1)]

        fig.add_trace(go.Scatter(
            x=mid_xs,
            y=mid_ys,
            mode="markers",
            name="Sens de parcours",
            marker=dict(symbol="triangle-right", size=7, color="#80D8FF"),
            hoverinfo="skip",
            showlegend=False
        ))

    # 2. Points clients (1 à 40)
    client_xs = [points_dict[i]["x"] for i in points_dict if i != DEPOT_ID]
    client_ys = [points_dict[i]["y"] for i in points_dict if i != DEPOT_ID]
    client_text = [f"P{i:02d}" for i in points_dict if i != DEPOT_ID]
    client_hover = [
        f"<b>P{i:02d} : {points_dict[i]['name']}</b><br>"
        f"Catégorie : {points_dict[i]['category']}<br>"
        f"Adresse : {points_dict[i]['address']}<br>"
        f"Coord. Cartésiennes : ({points_dict[i]['x']:.2f} km, {points_dict[i]['y']:.2f} km)<br>"
        f"GPS : ({points_dict[i]['lat']:.4f}°N, {points_dict[i]['lon']:.4f}°O)<extra></extra>"
        for i in points_dict if i != DEPOT_ID
    ]

    fig.add_trace(go.Scatter(
        x=client_xs,
        y=client_ys,
        mode="markers+text",
        name="Clients (40 points)",
        text=client_text,
        textposition="top center",
        textfont=dict(size=9, color="#ECEFF1"),
        marker=dict(
            symbol="circle",
            size=10,
            color="#FFCA28",
            line=dict(color="#263238", width=1.5)
        ),
        hovertemplate=client_hover
    ))

    # 3. Entrepôt central (Étoile rouge ★)
    depot_info = points_dict[DEPOT_ID]
    fig.add_trace(go.Scatter(
        x=[depot_info["x"]],
        y=[depot_info["y"]],
        mode="markers+text",
        name="Entrepôt Central (Hub)",
        text=["★ ENTREPÔT"],
        textposition="bottom center",
        textfont=dict(size=12, color="#FF5252", family="Arial Black"),
        marker=dict(
            symbol="star",
            size=18,
            color="#FF1744",
            line=dict(color="#FFFFFF", width=2)
        ),
        hovertemplate=(
            f"<b>★ {depot_info['name']}</b><br>"
            f"Statut : Base de départ et retour du circuit<br>"
            f"Coord. Cartésiennes : ({depot_info['x']:.2f} km, {depot_info['y']:.2f} km)<br>"
            f"GPS : ({depot_info['lat']:.4f}°N, {depot_info['lon']:.4f}°O)<extra></extra>"
        )
    ))

    # Mise en forme cartésienne avec échelle orthonormée
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            x=0.05,
            font=dict(size=14, color="#ECEFF1")
        ),
        xaxis=dict(
            title="Axe X – Déplacement Est-Ouest (km)",
            gridcolor="#37474F",
            zerolinecolor="#78909C",
            zerolinewidth=1.5,
            showgrid=True
        ),
        yaxis=dict(
            title="Axe Y – Déplacement Nord-Sud (km)",
            gridcolor="#37474F",
            zerolinecolor="#78909C",
            zerolinewidth=1.5,
            showgrid=True,
            scaleanchor="x",
            scaleratio=1  # Échelle orthonormée 1:1 pour éviter toute distorsion
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(33, 33, 33, 0.7)"
        ),
        template="plotly_dark",
        margin=dict(l=40, r=20, t=50, b=40),
        height=450
    )

    return fig
