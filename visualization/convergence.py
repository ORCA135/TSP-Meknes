"""
Visualisation de la courbe de convergence de l'Algorithme Génétique avec Plotly :
- Évolution de la meilleure distance (Best Solution)
- Évolution de la distance moyenne de la population (Average Population)
"""

from typing import List
import plotly.graph_objects as go


def create_convergence_plot(history_best: List[float],
                            history_avg: List[float],
                            title: str = "Dynamique d'Évolution et de Convergence Génétique") -> go.Figure:
    """
    Construit le graphique interactif Plotly de la courbe de convergence.
    """
    generations = list(range(len(history_best)))

    fig = go.Figure()

    # Courbe de la distance moyenne
    fig.add_trace(go.Scatter(
        x=generations,
        y=history_avg,
        mode="lines",
        name="Distance Moyenne (Population)",
        line=dict(color="#FFA726", width=2, dash="dot"),
        hovertemplate="Génération %{x}<br>Dist. Moyenne : %{y:.2f} km<extra></extra>"
    ))

    # Courbe de la meilleure solution
    fig.add_trace(go.Scatter(
        x=generations,
        y=history_best,
        mode="lines",
        name="Meilleure Solution (Best Tour)",
        line=dict(color="#00E676", width=3),
        hovertemplate="Génération %{x}<br>Meilleure Dist. : %{y:.2f} km<extra></extra>"
    ))

    # Mise en forme moderne
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            x=0.05,
            font=dict(size=14, color="#ECEFF1")
        ),
        xaxis=dict(
            title="Nombre d'Itérations (Générations)",
            gridcolor="#37474F",
            zerolinecolor="#37474F",
            showgrid=True
        ),
        yaxis=dict(
            title="Distance Totale du Circuit (km)",
            gridcolor="#37474F",
            zerolinecolor="#37474F",
            showgrid=True
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
        height=380,
        hovermode="x unified"
    )

    return fig
