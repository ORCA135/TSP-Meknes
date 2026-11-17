@echo off
setlocal

set TARGET=%1
if "%TARGET%"=="" set TARGET=help

if "%TARGET%"=="help" (
    echo ======================================================================
    echo TSP MEKNES - Commandes disponibles ^(make.bat^)
    echo ======================================================================
    echo   make deploy     : Genere le lien de deploiement Streamlit Cloud
    echo   make link       : Affiche le lien web public actif
    echo   make install    : Installe les dependances
    echo   make test       : Execute la suite de tests
    echo   make run        : Lance l'application principale
    echo   make run-gui    : Lance l'interface bureau Tkinter et Folium
    echo   make run-web    : Lance le Dashboard Web Streamlit
    echo   make tunnel     : Expose l'application sur le Web public ^(HTTPS^)
    echo   make clean      : Nettoie les caches
    echo ======================================================================
    goto :eof
)

if "%TARGET%"=="deploy" (
    .\.venv\Scripts\python deploy.py --push
    goto :eof
)

if "%TARGET%"=="link" (
    echo ======================================================================
    echo LIEN WEB PUBLIC ACTIF :
    echo https://997e4b1ca29acc.app.lhr.life
    echo ======================================================================
    goto :eof
)

if "%TARGET%"=="install" (
    .\.venv\Scripts\pip install -r requirements.txt
    goto :eof
)

if "%TARGET%"=="test" (
    .\.venv\Scripts\python tests\test_pipeline.py
    goto :eof
)

if "%TARGET%"=="run" (
    .\.venv\Scripts\python TP.py
    goto :eof
)

if "%TARGET%"=="run-gui" (
    .\.venv\Scripts\python gui_tkinter.py
    goto :eof
)

if "%TARGET%"=="run-web" (
    .\.venv\Scripts\streamlit run app.py --server.port 8501 --server.address 0.0.0.0
    goto :eof
)

if "%TARGET%"=="tunnel" (
    ssh -o StrictHostKeyChecking=no -R 80:127.0.0.1:8501 nokey@localhost.run
    goto :eof
)

if "%TARGET%"=="clean" (
    if exist .cache_matplotlib rmdir /s /q .cache_matplotlib
    if exist __pycache__ rmdir /s /q __pycache__
    echo [OK] Nettoyage termine.
    goto :eof
)

echo Commande inconnue: %TARGET%. Tapez 'make help' pour voir la liste.
