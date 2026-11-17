"""
Point d'entrée principal pour TSP Meknès.
Lance par défaut l'application bureau Tkinter & Folium.
Permet également de basculer sur l'interface Streamlit web via l'option --web.
"""

import sys
import subprocess
from pathlib import Path


def main():
    print("=" * 75)
    print("🚚 TSP MEKNÈS – Intelligent Urban Route Optimization")
    print("Technologies : Tkinter | Folium | Genetic Algorithms | Optuna | Agentic AI")
    print("=" * 75)

    base_dir = Path(__file__).parent

    # Vérification des arguments
    if "--web" in sys.argv or "--streamlit" in sys.argv:
        app_path = base_dir / "app.py"
        print("\n[INFO] Lancement de l'interface Streamlit sur http://localhost:8501 ...")
        cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]
    else:
        app_path = base_dir / "gui_tkinter.py"
        print("\n[INFO] Lancement de l'application Bureau Tkinter & Folium...")
        cmd = [sys.executable, str(app_path)]

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n[INFO] Fermeture de l'application.")


if __name__ == "__main__":
    main()
