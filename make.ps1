param (
    [string]$Target = "help"
)

switch ($Target.ToLower()) {
    "help" {
        Write-Host "======================================================================" -ForegroundColor Cyan
        Write-Host "🚚 TSP MEKNÈS – Commandes disponibles (make.ps1)" -ForegroundColor Cyan
        Write-Host "======================================================================" -ForegroundColor Cyan
        Write-Host "  .\make.ps1 install    : Installe toutes les dépendances"
        Write-Host "  .\make.ps1 test       : Exécute la suite complète de validation"
        Write-Host "  .\make.ps1 run        : Lance l'application principale"
        Write-Host "  .\make.ps1 run-gui    : Lance l'interface bureau native Tkinter & Folium"
        Write-Host "  .\make.ps1 run-web    : Lance le Dashboard Web Streamlit"
        Write-Host "  .\make.ps1 tunnel     : Expose l'application sur le Web public (HTTPS)"
        Write-Host "  .\make.ps1 clean      : Nettoie les caches temporaires"
        Write-Host "======================================================================" -ForegroundColor Cyan
    }
    "install" {
        & .\.venv\Scripts\pip.exe install -r requirements.txt
    }
    "test" {
        & .\.venv\Scripts\python.exe tests\test_pipeline.py
    }
    "run" {
        & .\.venv\Scripts\python.exe TP.py
    }
    "run-gui" {
        & .\.venv\Scripts\python.exe gui_tkinter.py
    }
    "run-web" {
        & .\.venv\Scripts\streamlit.exe run app.py --server.port 8501 --server.address 0.0.0.0
    }
    "tunnel" {
        Write-Host "[INFO] Connexion au tunnel public..." -ForegroundColor Green
        & ssh -o StrictHostKeyChecking=no -R 80:127.0.0.1:8501 nokey@localhost.run
    }
    "clean" {
        if (Test-Path ".cache_matplotlib") { Remove-Item -Recurse -Force ".cache_matplotlib" }
        if (Test-Path "__pycache__") { Remove-Item -Recurse -Force "__pycache__" }
        Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force
        Write-Host "[OK] Nettoyage terminé." -ForegroundColor Green
    }
    default {
        Write-Host "Commande inconnue : $Target. Exécutez '.\make.ps1 help' pour voir la liste." -ForegroundColor Red
    }
}
