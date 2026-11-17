"""
Script d'assistance au déploiement en 1 clic pour Streamlit Community Cloud.
- Vérifie la configuration Git locale et distante.
- Génère l'URL officielle de déploiement direct Streamlit Cloud (1-Click Deploy).
- Ouvre automatiquement la page de déploiement dans le navigateur.
"""

import sys
import subprocess
import webbrowser
from pathlib import Path


def run_cmd(cmd: list) -> str:
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return ""


def main():
    print("=" * 75)
    print("🚀 DÉPLOIEMENT STREAMLIT COMMUNITY CLOUD – TSP MEKNÈS")
    print("=" * 75)

    # 1. Vérification de l'état Git
    remote_url = run_cmd(["git", "remote", "get-url", "origin"])

    if not remote_url:
        print("\n[Étape 1/2] Aucun dépôt distant GitHub n'est encore configuré.")
        print("\n👉 Pour lier votre dépôt GitHub, exécutez :")
        print("    git remote add origin https://github.com/VOTRE_NOM_UTILISATEUR/tsp-meknes.git")
        print("    git push -u origin main")
        print("\nOu utilisez la commande makefile :")
        print("    .\\make.ps1 github-setup https://github.com/VOTRE_NOM_UTILISATEUR/tsp-meknes.git")

        print("\n[Étape 2/2] Ouverture de la page de création de dépôt GitHub et de Streamlit Cloud...")
        webbrowser.open("https://github.com/new")
        webbrowser.open("https://share.streamlit.io/deploy")
        return

    # Extraction du chemin utilisateur/projet depuis l'URL Git
    clean_repo = remote_url.replace(".git", "")
    if "github.com/" in clean_repo:
        repo_slug = clean_repo.split("github.com/")[-1]
    elif "github.com:" in clean_repo:
        repo_slug = clean_repo.split("github.com:")[-1]
    else:
        repo_slug = clean_repo

    # 2. Push éventuel des dernières modifications
    if "--push" in sys.argv:
        print("\n[INFO] Envoi des dernières modifications vers GitHub...")
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", "Mise a jour pour deploiement Streamlit Cloud"])
        subprocess.run(["git", "push", "-u", "origin", "main"])

    # 3. Construction de l'URL de déploiement en 1 clic
    deploy_url = f"https://share.streamlit.io/deploy?repository={repo_slug}&branch=main&mainModule=app.py"

    print(f"\n✅ Dépôt GitHub détecté : {repo_slug}")
    print("\n🔗 LIEN OFFICIEL DE DÉPLOIEMENT STREAMLIT CLOUD (1-CLIC) :")
    print("-" * 75)
    print(f"👉 {deploy_url}")
    print("-" * 75)
    print("\nParamètres pré-configurés :")
    print(f"  • Repository  : {repo_slug}")
    print("  • Branch      : main")
    print("  • Main Module : app.py")

    print("\n[ACTION] Ouverture automatique de la page de déploiement dans votre navigateur...")
    webbrowser.open(deploy_url)


if __name__ == "__main__":
    main()
