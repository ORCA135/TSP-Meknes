# ==============================================================================
# 🚚 TSP MEKNÈS – Makefile d'Automatisation & Déploiement
# ==============================================================================

PYTHON ?= python
PIP ?= pip
STREAMLIT ?= streamlit

.PHONY: help install test run run-gui run-web tunnel clean

help:
	@echo "======================================================================"
	@echo "🚚 TSP MEKNÈS – Commandes disponibles via Makefile"
	@echo "======================================================================"
	@echo "  make install    : Installe toutes les dépendances (requirements.txt)"
	@echo "  make test       : Exécute la suite complète de validation (6/6 tests)"
	@echo "  make run        : Lance l'application principale (TP.py)"
	@echo "  make run-gui    : Lance l'interface bureau native Tkinter & Folium"
	@echo "  make run-web    : Lance le Dashboard Web Streamlit (port 8501)"
	@echo "  make tunnel     : Expose l'application sur le Web public (HTTPS)"
	@echo "  make clean      : Supprime les caches temporaires et fichiers compilés"
	@echo "======================================================================"

install:
	$(PIP) install -r requirements.txt

test:
	$(PYTHON) tests/test_pipeline.py

run:
	$(PYTHON) TP.py

run-gui:
	$(PYTHON) gui_tkinter.py

run-web:
	$(STREAMLIT) run app.py --server.port 8501 --server.address 0.0.0.0

tunnel:
	@echo "[INFO] Lancement du tunnel public HTTPS vers l'application..."
	ssh -o StrictHostKeyChecking=no -R 80:127.0.0.1:8501 nokey@localhost.run

clean:
	@echo "[INFO] Nettoyage des caches..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".cache_matplotlib" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "[OK] Nettoyage terminé."
