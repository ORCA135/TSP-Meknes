"""
Visualisation cartographique interactive SIG sous Folium pour TSP Meknès :
- Fond de carte OpenStreetMap haute définition.
- 40 points clients géolocalisés avec pastilles numérotées et métadonnées.
- Entrepôt central distingué par une icône spéciale rouge vif.
- Tracé du circuit routier réel calculé par OSRM (ou géométrie directe de repli).
- Infobulles, fenêtres popup et tableau récapitulatif des segments.
"""

from typing import List, Optional, Dict, Any, Tuple
import folium
from folium import plugins
import pandas as pd

from utils.config import MEKNES_CENTER_LAT, MEKNES_CENTER_LON, DEPOT_ID
from routing.osrm_client import OSRMClient


def create_meknes_folium_map(points_df: pd.DataFrame,
                             tour: Optional[List[int]] = None,
                             distance_matrix: Optional[Any] = None) -> Tuple[folium.Map, List[Dict[str, Any]]]:
    """
    Crée une carte interactive Folium avec les 40 points de Meknès et le routage réel.
    
    Retourne :
    - m : objet folium.Map
    - segments_info : liste des informations sur chaque segment du parcours
    """
    # 1. Initialisation de la carte centrée sur Meknès
    m = folium.Map(
        location=[MEKNES_CENTER_LAT, MEKNES_CENTER_LON],
        zoom_start=13,
        tiles="OpenStreetMap",
        control_scale=True
    )

    points_by_id = {int(row["id"]): row for _, row in points_df.iterrows()}
    segments_info: List[Dict[str, Any]] = []

    # 2. Ajout de l'entrepôt central
    depot_row = points_by_id[DEPOT_ID]
    depot_popup = f"""
    <div style="font-family: Arial; min-width: 180px;">
        <h4 style="color: #D32F2F; margin: 0 0 5px 0;">★ Entrepôt Central</h4>
        <b>Nom :</b> {depot_row['name']}<br>
        <b>Adresse :</b> {depot_row['address']}<br>
        <b>GPS :</b> {depot_row['latitude']:.4f}°N, {depot_row['longitude']:.4f}°O<br>
        <span style="color: #388E3C; font-weight: bold;">Point de Départ & Arrivée</span>
    </div>
    """

    folium.Marker(
        location=[depot_row["latitude"], depot_row["longitude"]],
        popup=folium.Popup(depot_popup, max_width=300),
        tooltip="★ Entrepôt Central - Hub Hamria",
        icon=folium.Icon(color="red", icon="home", prefix="fa")
    ).add_to(m)

    # Ordre de visite des clients si tour fourni
    visit_order_map = {}
    if tour and len(tour) > 2:
        # tour = [0, c1, c2, ..., c40, 0]
        for step_idx, client_id in enumerate(tour[1:-1], start=1):
            visit_order_map[client_id] = step_idx

    # 3. Ajout des 40 points clients
    for p_id, row in points_by_id.items():
        if p_id == DEPOT_ID:
            continue

        step_num = visit_order_map.get(p_id, None)
        badge_text = f"Étape #{step_num}" if step_num else f"Point P{p_id:02d}"

        client_popup = f"""
        <div style="font-family: Arial; min-width: 200px;">
            <h4 style="color: #1976D2; margin: 0 0 5px 0;">P{p_id:02d} - {row['name']}</h4>
            <b>Catégorie :</b> {row['category']}<br>
            <b>Ordre de passage :</b> <span style="color: #E65100; font-weight: bold;">{badge_text}</span><br>
            <b>Adresse :</b> {row['address']}<br>
            <b>GPS :</b> {row['latitude']:.4f}°N, {row['longitude']:.4f}°O
        </div>
        """

        # Marqueur circulaire avec numéro
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=8,
            color="#0D47A1",
            weight=2,
            fill=True,
            fill_color="#FFB300" if step_num else "#29B6F6",
            fill_opacity=0.9,
            popup=folium.Popup(client_popup, max_width=300),
            tooltip=f"P{p_id:02d}: {row['name']} ({badge_text})"
        ).add_to(m)

    # 4. Tracé du circuit routier réel
    if tour and len(tour) >= 2:
        client = OSRMClient()
        tour_coords = [
            (points_by_id[node]["latitude"], points_by_id[node]["longitude"])
            for node in tour
        ]

        # Tentative d'obtention de la géométrie routière OSRM
        route_data = client.fetch_route_geometry(tour_coords)

        if route_data and "geometry" in route_data and len(route_data["geometry"]) > 0:
            # OSRM renvoie [lon, lat] -> inversion en [lat, lon] pour Folium
            polyline_points = [[lat, lon] for lon, lat in route_data["geometry"]]
            folium.PolyLine(
                locations=polyline_points,
                color="#00C853",
                weight=5,
                opacity=0.85,
                tooltip=f"Itinéraire Routier OSRM : {route_data['distance_km']:.2f} km"
            ).add_to(m)
        else:
            # Mode de secours : tracé direct point par point
            polyline_points = [[lat, lon] for lat, lon in tour_coords]
            folium.PolyLine(
                locations=polyline_points,
                color="#00B0FF",
                weight=4,
                opacity=0.8,
                dash_array="6, 8",
                tooltip="Tracé du circuit (Mode démonstration SIG)"
            ).add_to(m)

        # Construction du tableau récapitulatif des segments
        cumulative_dist = 0.0
        for i in range(len(tour) - 1):
            u, v = tour[i], tour[i + 1]
            u_name = "Entrepôt" if u == 0 else f"P{u:02d} ({points_by_id[u]['name']})"
            v_name = "Entrepôt" if v == 0 else f"P{v:02d} ({points_by_id[v]['name']})"

            seg_dist = 0.0
            if distance_matrix is not None:
                seg_dist = float(distance_matrix[u, v])
            cumulative_dist += seg_dist

            segments_info.append({
                "Segment": f"#{i+1}",
                "Origine": u_name,
                "Destination": v_name,
                "Distance (km)": round(seg_dist, 3),
                "Cumulée (km)": round(cumulative_dist, 3)
            })

    # Ajout du contrôle plein écran
    plugins.Fullscreen(position="topright").add_to(m)

    return m, segments_info
