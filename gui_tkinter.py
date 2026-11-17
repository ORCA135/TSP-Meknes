"""
TSP MEKNÈS – Application Graphique Professionnelle sous Tkinter & Folium
Architecture complète en 4 quadrants :
- Quadrant 1 : Configuration et Modes (Manuel, Optuna, Agentic AI)
- Quadrant 2 : Analyse des performances (KPIs, Courbe de convergence, Chromosome)
- Quadrant 3 : Visualisation cartésienne 2D (Plan orthonormé en km, étoile entrepôt ★, 40 points)
- Quadrant 4 : Cartographie réelle et routage OSRM (Folium Leaflet, tracé routier, tableau des segments)
"""

import os
import sys
import threading
import webbrowser
from pathlib import Path
from typing import List, Dict, Any, Optional

# Configuration du cache Matplotlib pour éviter les conflits d'accès
os.environ["MPLCONFIGDIR"] = str(Path(__file__).parent / ".cache_matplotlib")

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import des composants métier TSP Meknès
from utils.config import (
    POINTS_CSV,
    DISTANCE_MATRIX_CSV,
    POPULATION_SIZES,
    SELECTION_METHODS,
    MUTATION_RATES,
    CROSSOVER_RATES,
    ITERATION_OPTIONS,
    DEFAULT_POP_SIZE,
    DEFAULT_SELECTION,
    DEFAULT_MUTATION_RATE,
    DEFAULT_CROSSOVER_RATE,
    DEFAULT_ITERATIONS,
    DEPOT_ID,
    DEPOT_NAME,
    MEKNES_CENTER_LAT,
    MEKNES_CENTER_LON
)
from utils.helpers import gps_to_cartesian_km, format_chromosome_display, validate_tsp_solution
from routing.distance_matrix import load_meknes_points, load_or_compute_distance_matrix
from algorithms.genetic_algorithm import GeneticAlgorithmTSP
from optimization.optuna_optimizer import OptunaTSPOptimizer
from agents.arbitration_agent import run_agentic_pipeline
from routing.map_visualization import create_meknes_folium_map

# Tentative d'import de tkinterweb pour affichage HTML embarqué
try:
    from tkinterweb import HtmlFrame
    HAS_TKINTERWEB = True
except ImportError:
    HAS_TKINTERWEB = False


class TSPMeknesTkinterApp:
    """
    Application Bureau Tkinter pour l'optimisation de tournées urbaines TSP à Meknès.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("TSP MEKNÈS – Intelligent Urban Route Optimization (Tkinter & Folium)")
        self.root.geometry("1480x920")
        self.root.minsize(1200, 750)

        # Palette graphique moderne (Dark / Slate Professional Theme)
        self.bg_dark = "#0F172A"       # Arrière-plan général
        self.card_bg = "#1E293B"       # Cartes / Quadrants
        self.accent_blue = "#0284C7"   # Bleu technologique
        self.accent_green = "#10B981"  # Vert performance
        self.accent_amber = "#F59E0B"  # Ambre
        self.accent_purple = "#8B5CF6" # Violet Optuna
        self.text_primary = "#F8FAFC"  # Texte blanc
        self.text_muted = "#94A3B8"    # Texte gris
        self.border_color = "#334155"  # Bordures

        self.root.configure(bg=self.bg_dark)

        # Chargement des données territoriales de Meknès
        self.points_df = load_meknes_points(POINTS_CSV)
        self.distance_matrix, self.is_live_osrm, self.matrix_source = load_or_compute_distance_matrix(
            DISTANCE_MATRIX_CSV, POINTS_CSV
        )

        # Variables d'état
        self.current_tour: List[int] = []
        self.current_result: Dict[str, Any] = {}
        self.map_html_path = Path(__file__).parent / "data" / "meknes_folium_map.html"
        self.is_running = False

        # Configuration des styles TTK
        self._setup_styles()

        # Construction de l'interface
        self._build_header()
        self._build_quadrants()

        # Initialisation par défaut (tour initial rapide)
        self._run_initial_baseline()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Configuration des styles personnalisés
        style.configure("TFrame", background=self.bg_dark)
        style.configure("Card.TFrame", background=self.card_bg, relief="solid", borderwidth=1)
        style.configure("TLabel", background=self.card_bg, foreground=self.text_primary, font=("Segoe UI", 9))
        style.configure("Header.TLabel", font=("Segoe UI", 11, "bold"), foreground=self.accent_blue)
        style.configure("Muted.TLabel", foreground=self.text_muted, font=("Segoe UI", 8))
        style.configure("TCombobox", fieldbackground="#0F172A", background="#1E293B", foreground="#FFFFFF")

        # Style Treeview
        style.configure("Treeview",
                        background="#0F172A",
                        foreground="#FFFFFF",
                        fieldbackground="#0F172A",
                        font=("Segoe UI", 8),
                        rowheight=22)
        style.configure("Treeview.Heading",
                        background="#1E293B",
                        foreground="#38BDF8",
                        font=("Segoe UI", 8, "bold"))
        style.map("Treeview", background=[("selected", "#0284C7")])

    def _build_header(self):
        """En-tête principal de l'application."""
        header_frame = tk.Frame(self.root, bg=self.bg_dark, pady=8)
        header_frame.pack(fill="x", padx=16)

        title_lbl = tk.Label(
            header_frame,
            text="🚚 TSP MEKNÈS – Intelligent Urban Route Optimization",
            font=("Segoe UI", 18, "bold"),
            bg=self.bg_dark,
            fg="#38BDF8"
        )
        title_lbl.pack()

        subtitle_lbl = tk.Label(
            header_frame,
            text="Genetic Algorithms | Hyperparameter Optimization (Optuna) | Agentic AI | Real-Time Mapping (Folium & OSRM)",
            font=("Segoe UI", 9),
            bg=self.bg_dark,
            fg=self.text_muted
        )
        subtitle_lbl.pack()

        # Barre d'état source
        status_text = f"📍 Meknès, Maroc | 40 Clients + Entrepôt Hamria | {'🟢 OSRM Driving Table (Direct)' if self.is_live_osrm else '🟡 Mode Secours Calibré'}"
        source_lbl = tk.Label(
            header_frame,
            text=status_text,
            font=("Segoe UI", 8, "italic"),
            bg=self.bg_dark,
            fg="#34D399"
        )
        source_lbl.pack(pady=2)

    def _build_quadrants(self):
        """Organisation en grille 2x2 des quatre quadrants équilibrés."""
        grid_container = tk.Frame(self.root, bg=self.bg_dark)
        grid_container.pack(fill="both", expand=True, padx=12, pady=4)

        grid_container.columnconfigure(0, weight=1, uniform="quad_col")
        grid_container.columnconfigure(1, weight=1, uniform="quad_col")
        grid_container.rowconfigure(0, weight=1, uniform="quad_row")
        grid_container.rowconfigure(1, weight=1, uniform="quad_row")

        # QUADRANT 1 : Haut Gauche
        self.frame_q1 = tk.Frame(grid_container, bg=self.card_bg, highlightbackground=self.border_color, highlightthickness=1)
        self.frame_q1.grid(row=0, column=0, padx=6, pady=6, sticky="nsew")
        self._setup_quadrant_1()

        # QUADRANT 2 : Haut Droite
        self.frame_q2 = tk.Frame(grid_container, bg=self.card_bg, highlightbackground=self.border_color, highlightthickness=1)
        self.frame_q2.grid(row=0, column=1, padx=6, pady=6, sticky="nsew")
        self._setup_quadrant_2()

        # QUADRANT 3 : Bas Gauche
        self.frame_q3 = tk.Frame(grid_container, bg=self.card_bg, highlightbackground=self.border_color, highlightthickness=1)
        self.frame_q3.grid(row=1, column=0, padx=6, pady=6, sticky="nsew")
        self._setup_quadrant_3()

        # QUADRANT 4 : Bas Droite
        self.frame_q4 = tk.Frame(grid_container, bg=self.card_bg, highlightbackground=self.border_color, highlightthickness=1)
        self.frame_q4.grid(row=1, column=1, padx=6, pady=6, sticky="nsew")
        self._setup_quadrant_4()

    # --------------------------------------------------------------------------
    # QUADRANT 1 : CONFIGURATION ET MODES
    # --------------------------------------------------------------------------
    def _setup_quadrant_1(self):
        header = tk.Label(self.frame_q1, text="⚙️ QUADRANT 1 – Configuration & Modes d'Optimisation",
                          font=("Segoe UI", 11, "bold"), bg=self.card_bg, fg=self.accent_blue)
        header.pack(anchor="w", padx=12, pady=6)

        # Sous-panneau A : Définition du problème
        p_frame = tk.LabelFrame(self.frame_q1, text=" A. Définition du problème ",
                                bg=self.card_bg, fg=self.text_primary, font=("Segoe UI", 8, "bold"), padx=8, pady=4)
        p_frame.pack(fill="x", padx=10, pady=4)

        tk.Label(p_frame, text="• Ville : Meknès, Maroc (Zone urbaine dense)", bg=self.card_bg, fg=self.text_primary).pack(anchor="w")
        tk.Label(p_frame, text="• Entrepôt : Hub Hamria (Départ & Arrivée du circuit)", bg=self.card_bg, fg=self.text_primary).pack(anchor="w")
        tk.Label(p_frame, text="• Distance : Distance routière réelle en kilomètres (OSRM)", bg=self.card_bg, fg=self.text_primary).pack(anchor="w")

        # Sous-panneau B : Paramètres de l'Algorithme Génétique
        param_frame = tk.LabelFrame(self.frame_q1, text=" B. Paramètres de l'Algorithme Génétique ",
                                    bg=self.card_bg, fg=self.text_primary, font=("Segoe UI", 8, "bold"), padx=8, pady=4)
        param_frame.pack(fill="x", padx=10, pady=4)

        grid_p = tk.Frame(param_frame, bg=self.card_bg)
        grid_p.pack(fill="x")

        # 1. Population Size
        tk.Label(grid_p, text="1. Population Size :", bg=self.card_bg, fg=self.text_primary).grid(row=0, column=0, sticky="w", pady=2)
        self.combo_pop = ttk.Combobox(grid_p, values=POPULATION_SIZES, width=12, state="readonly")
        self.combo_pop.set(DEFAULT_POP_SIZE)
        self.combo_pop.grid(row=0, column=1, padx=6, pady=2, sticky="w")

        # 2. Selection Method
        tk.Label(grid_p, text="2. Selection Method :", bg=self.card_bg, fg=self.text_primary).grid(row=0, column=2, sticky="w", padx=(12, 0), pady=2)
        self.combo_sel = ttk.Combobox(grid_p, values=SELECTION_METHODS, width=22, state="readonly")
        self.combo_sel.set(DEFAULT_SELECTION)
        self.combo_sel.grid(row=0, column=3, padx=6, pady=2, sticky="w")

        # 3. Mutation Rate
        tk.Label(grid_p, text="3. Mutation Rate :", bg=self.card_bg, fg=self.text_primary).grid(row=1, column=0, sticky="w", pady=2)
        self.combo_mut = ttk.Combobox(grid_p, values=MUTATION_RATES, width=12, state="readonly")
        self.combo_mut.set(DEFAULT_MUTATION_RATE)
        self.combo_mut.grid(row=1, column=1, padx=6, pady=2, sticky="w")

        # 4. Crossover Rate
        tk.Label(grid_p, text="4. Crossover Rate :", bg=self.card_bg, fg=self.text_primary).grid(row=1, column=2, sticky="w", padx=(12, 0), pady=2)
        self.combo_cross = ttk.Combobox(grid_p, values=CROSSOVER_RATES, width=22, state="readonly")
        self.combo_cross.set(DEFAULT_CROSSOVER_RATE)
        self.combo_cross.grid(row=1, column=3, padx=6, pady=2, sticky="w")

        # 5. Iterations
        tk.Label(grid_p, text="5. Iterations :", bg=self.card_bg, fg=self.text_primary).grid(row=2, column=0, sticky="w", pady=2)
        self.combo_iter = ttk.Combobox(grid_p, values=ITERATION_OPTIONS, width=12, state="readonly")
        self.combo_iter.set(DEFAULT_ITERATIONS)
        self.combo_iter.grid(row=2, column=1, padx=6, pady=2, sticky="w")

        # Sous-panneau C : Trois boutons de commande
        btn_frame = tk.Frame(self.frame_q1, bg=self.card_bg)
        btn_frame.pack(fill="x", padx=10, pady=8)

        self.btn_manual = tk.Button(
            btn_frame,
            text="🔵 B1 – MANUAL MODE",
            bg="#0284C7",
            fg="#FFFFFF",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=10,
            pady=6,
            cursor="hand2",
            command=self._on_click_manual
        )
        self.btn_manual.pack(side="left", expand=True, fill="x", padx=3)

        self.btn_optuna = tk.Button(
            btn_frame,
            text="🟣 B2 – OPTUNA OPTIM",
            bg="#7C3AED",
            fg="#FFFFFF",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=10,
            pady=6,
            cursor="hand2",
            command=self._on_click_optuna
        )
        self.btn_optuna.pack(side="left", expand=True, fill="x", padx=3)

        self.btn_agentic = tk.Button(
            btn_frame,
            text="🟢 B3 – AGENTIC AI",
            bg="#059669",
            fg="#FFFFFF",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=10,
            pady=6,
            cursor="hand2",
            command=self._on_click_agentic
        )
        self.btn_agentic.pack(side="left", expand=True, fill="x", padx=3)

        # Sous-panneau D : Barre de progression & statut
        prog_frame = tk.Frame(self.frame_q1, bg=self.card_bg)
        prog_frame.pack(fill="x", padx=10, pady=4)

        self.progress_bar = ttk.Progressbar(prog_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill="x", pady=2)

        self.lbl_status = tk.Label(
            prog_frame,
            text="Prêt. Sélectionnez un mode pour lancer l'optimisation.",
            font=("Segoe UI", 8, "italic"),
            bg=self.card_bg,
            fg=self.text_muted
        )
        self.lbl_status.pack(anchor="w")

    # --------------------------------------------------------------------------
    # QUADRANT 2 : ANALYSE DES PERFORMANCES ET RÉSULTATS
    # --------------------------------------------------------------------------
    def _setup_quadrant_2(self):
        header = tk.Label(self.frame_q2, text="📊 QUADRANT 2 – Analyse des Performances & Résultats",
                          font=("Segoe UI", 11, "bold"), bg=self.card_bg, fg=self.accent_blue)
        header.pack(anchor="w", padx=12, pady=6)

        # Cartes KPI
        kpi_container = tk.Frame(self.frame_q2, bg=self.card_bg)
        kpi_container.pack(fill="x", padx=10, pady=2)

        for i in range(5):
            kpi_container.columnconfigure(i, weight=1)

        self.kpi_best_val = self._create_kpi_card(kpi_container, 0, "BEST DISTANCE", "-- km", "#34D399")
        self.kpi_init_val = self._create_kpi_card(kpi_container, 1, "INITIAL DIST.", "-- km", "#F87171")
        self.kpi_gain_val = self._create_kpi_card(kpi_container, 2, "IMPROVEMENT", "-- %", "#60A5FA")
        self.kpi_time_val = self._create_kpi_card(kpi_container, 3, "EXEC TIME", "-- s", "#FBBF24")
        self.kpi_iter_val = self._create_kpi_card(kpi_container, 4, "ITERATIONS", "--", "#C084FC")

        # Courbe de convergence Matplotlib intégrée
        self.fig_conv = Figure(figsize=(5.5, 2.3), dpi=100, facecolor=self.card_bg)
        self.ax_conv = self.fig_conv.add_subplot(111)
        self.ax_conv.set_facecolor("#0F172A")
        self.ax_conv.tick_params(colors="#94A3B8", labelsize=7)
        for spine in self.ax_conv.spines.values():
            spine.set_color("#334155")

        self.canvas_conv = FigureCanvasTkAgg(self.fig_conv, master=self.frame_q2)
        self.canvas_conv.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=2)

        # Chromosome solution
        chromo_frame = tk.Frame(self.frame_q2, bg=self.card_bg)
        chromo_frame.pack(fill="x", padx=10, pady=4)

        tk.Label(chromo_frame, text="🧬 Chromosome Solution :", bg=self.card_bg, fg=self.text_primary, font=("Segoe UI", 8, "bold")).pack(anchor="w")

        self.txt_chromosome = tk.Text(chromo_frame, height=2, bg="#0F172A", fg="#38BDF8", font=("Consolas", 8),
                                      relief="solid", borderwidth=1, wrap="word")
        self.txt_chromosome.pack(fill="x", pady=2)

        self.lbl_valid = tk.Label(chromo_frame, text="✓ Solution TSP conforme", bg=self.card_bg, fg="#34D399", font=("Segoe UI", 8, "bold"))
        self.lbl_valid.pack(anchor="w")

    def _create_kpi_card(self, parent, col, title, initial_val, color):
        frame = tk.Frame(parent, bg="#0F172A", relief="solid", borderwidth=1, padx=4, pady=4)
        frame.grid(row=0, column=col, padx=3, pady=2, sticky="nsew")

        t_lbl = tk.Label(frame, text=title, font=("Segoe UI", 6, "bold"), bg="#0F172A", fg=self.text_muted)
        t_lbl.pack()

        v_lbl = tk.Label(frame, text=initial_val, font=("Segoe UI", 11, "bold"), bg="#0F172A", fg=color)
        v_lbl.pack()
        return v_lbl

    # --------------------------------------------------------------------------
    # QUADRANT 3 : VISUALISATION CARTÉSIENNE 2D
    # --------------------------------------------------------------------------
    def _setup_quadrant_3(self):
        header = tk.Label(self.frame_q3, text="📐 QUADRANT 3 – Visualisation Cartésienne 2D",
                          font=("Segoe UI", 11, "bold"), bg=self.card_bg, fg=self.accent_blue)
        header.pack(anchor="w", padx=12, pady=6)

        self.fig_cart = Figure(figsize=(5.5, 3.5), dpi=100, facecolor=self.card_bg)
        self.ax_cart = self.fig_cart.add_subplot(111)
        self.ax_cart.set_facecolor("#0F172A")
        self.ax_cart.tick_params(colors="#94A3B8", labelsize=7)
        for spine in self.ax_cart.spines.values():
            spine.set_color("#334155")

        self.canvas_cart = FigureCanvasTkAgg(self.fig_cart, master=self.frame_q3)
        self.canvas_cart.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=4)

        tk.Label(self.frame_q3,
                 text="ℹ️ Coordonnées projetées en km centrées sur Meknès. ★ Étoile rouge = Entrepôt Central Hamria.",
                 bg=self.card_bg, fg=self.text_muted, font=("Segoe UI", 7, "italic")).pack(anchor="w", padx=10, pady=2)

    # --------------------------------------------------------------------------
    # QUADRANT 4 : CARTOGRAPHIE RÉELLE ET ROUTAGE OSRM (FOLIUM)
    # --------------------------------------------------------------------------
    def _setup_quadrant_4(self):
        header_frame = tk.Frame(self.frame_q4, bg=self.card_bg)
        header_frame.pack(fill="x", padx=12, pady=6)

        header = tk.Label(header_frame, text="🗺️ QUADRANT 4 – Cartographie Réelle Folium & Routage OSRM",
                          font=("Segoe UI", 11, "bold"), bg=self.card_bg, fg=self.accent_blue)
        header.pack(side="left")

        btn_open_map = tk.Button(
            header_frame,
            text="🌐 Ouvrir dans le Navigateur",
            bg="#059669",
            fg="#FFFFFF",
            font=("Segoe UI", 8, "bold"),
            padx=8,
            pady=3,
            relief="flat",
            cursor="hand2",
            command=self._open_map_in_browser
        )
        btn_open_map.pack(side="right")

        content_pane = tk.Frame(self.frame_q4, bg=self.card_bg)
        content_pane.pack(fill="both", expand=True, padx=10, pady=2)

        # Affichage HTML Folium embarqué (si tkinterweb disponible) ou aperçu interactif
        if HAS_TKINTERWEB:
            self.map_view_frame = HtmlFrame(content_pane, messages_enabled=False)
            self.map_view_frame.pack(fill="both", expand=True, pady=2)
        else:
            self.map_notice_frame = tk.Frame(content_pane, bg="#0F172A", relief="solid", borderwidth=1)
            self.map_notice_frame.pack(fill="both", expand=True, pady=2)

            tk.Label(self.map_notice_frame, text="🗺️ Carte Interactive Folium Générée",
                     font=("Segoe UI", 12, "bold"), bg="#0F172A", fg="#38BDF8").pack(pady=10)
            tk.Label(self.map_notice_frame,
                     text="La carte Leaflet complète intègre les 40 points réels de Meknès,\nle tracé OSRM et les métadonnées géographiques.\nCliquez sur le bouton ci-dessus pour naviguer en plein écran.",
                     font=("Segoe UI", 9), bg="#0F172A", fg=self.text_primary, justify="center").pack(pady=5)

        # Tableau des segments routiers
        seg_lbl = tk.Label(self.frame_q4, text="📋 Feuille de Route OSRM (Segments du circuit) :",
                           bg=self.card_bg, fg=self.text_primary, font=("Segoe UI", 8, "bold"))
        seg_lbl.pack(anchor="w", padx=10, pady=(4, 2))

        tree_frame = tk.Frame(self.frame_q4, bg=self.card_bg)
        tree_frame.pack(fill="x", padx=10, pady=2)

        columns = ("step", "from", "to", "dist", "cumul")
        self.tree_segments = ttk.Treeview(tree_frame, columns=columns, show="headings", height=5)
        self.tree_segments.heading("step", text="Étape")
        self.tree_segments.heading("from", text="Origine")
        self.tree_segments.heading("to", text="Destination")
        self.tree_segments.heading("dist", text="Distance (km)")
        self.tree_segments.heading("cumul", text="Cumulée (km)")

        self.tree_segments.column("step", width=50, anchor="center")
        self.tree_segments.column("from", width=180, anchor="w")
        self.tree_segments.column("to", width=180, anchor="w")
        self.tree_segments.column("dist", width=80, anchor="center")
        self.tree_segments.column("cumul", width=80, anchor="center")

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_segments.yview)
        self.tree_segments.configure(yscrollcommand=tree_scroll.set)

        self.tree_segments.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

    # --------------------------------------------------------------------------
    # LOGIQUE D'EXÉCUTION & ACTIONS
    # --------------------------------------------------------------------------
    def _run_initial_baseline(self):
        """Lance une première solution gloutonne pour initialiser le dashboard."""
        ga = GeneticAlgorithmTSP(
            distance_matrix=self.distance_matrix,
            num_clients=40,
            pop_size=50,
            num_iterations=20,
            seed=42
        )
        res = ga.solve()
        self._update_all_quadrants(res, mode_name="Initialisation")

    def _on_click_manual(self):
        """Gestion du Bouton B1 - MANUAL MODE."""
        if self.is_running:
            return

        pop = int(self.combo_pop.get())
        sel = self.combo_sel.get()
        mut = float(self.combo_mut.get())
        cross = float(self.combo_cross.get())
        num_iter = int(self.combo_iter.get())

        self._set_ui_running(True)
        self.lbl_status.config(text="Exécution de l'Algorithme Génétique (Mode Manuel)...", fg="#38BDF8")

        def task():
            def cb(gen, max_gen, best_d, avg_d):
                pct = int((gen / max_gen) * 100)
                self.root.after(0, lambda: self._update_progress(pct, f"Génération {gen}/{max_gen} | Meilleure dist : {best_d:.2f} km"))

            solver = GeneticAlgorithmTSP(
                distance_matrix=self.distance_matrix,
                num_clients=40,
                pop_size=pop,
                selection_method=sel,
                mutation_rate=mut,
                crossover_rate=cross,
                num_iterations=num_iter
            )
            res = solver.solve(progress_callback=cb)
            self.root.after(0, lambda: self._on_optimization_finished(res, "MANUAL MODE"))

        threading.Thread(target=task, daemon=True).start()

    def _on_click_optuna(self):
        """Gestion du Bouton B2 - OPTUNA OPTIMIZATION."""
        if self.is_running:
            return

        self._set_ui_running(True)
        self.lbl_status.config(text="Optimisation Bayésienne Optuna (TPE Sampler)...", fg="#A78BFA")

        def task():
            def opt_cb(t_num, total_t, cur_best, cur_params):
                pct = int((t_num / total_t) * 100)
                self.root.after(0, lambda: self._update_progress(pct, f"Optuna Essai {t_num}/{total_t} | Meilleure dist : {cur_best:.2f} km"))

            opt = OptunaTSPOptimizer(
                distance_matrix=self.distance_matrix,
                num_clients=40,
                n_trials=10,
                timeout=40
            )
            opt_res = opt.optimize(progress_callback=opt_cb)
            res = opt_res["final_run"]
            self.root.after(0, lambda: self._on_optimization_finished(res, f"OPTUNA ({opt_res['best_params']['selection_method']}, Pop:{opt_res['best_params']['pop_size']})"))

        threading.Thread(target=task, daemon=True).start()

    def _on_click_agentic(self):
        """Gestion du Bouton B3 - AGENTIC AI MODE."""
        if self.is_running:
            return

        self._set_ui_running(True)
        self.lbl_status.config(text="Système Multi-Agents : Recherche -> Analyse -> Arbitrage...", fg="#34D399")

        def task():
            def agent_cb(gen, max_gen, best_d, avg_d):
                pct = int((gen / max_gen) * 100)
                self.root.after(0, lambda: self._update_progress(pct, f"Tournée Arbitrée : Gen {gen}/{max_gen} | Dist : {best_d:.2f} km"))

            pipeline_res = run_agentic_pipeline(
                distance_matrix=self.distance_matrix,
                points_df=self.points_df,
                preference_mode="balanced",
                progress_callback=agent_cb
            )
            res = pipeline_res["ga_result"]
            decision = pipeline_res["arbitration_decision"]["decision_title"]
            self.root.after(0, lambda: self._on_optimization_finished(res, f"AGENTIC AI ({decision})"))

        threading.Thread(target=task, daemon=True).start()

    def _set_ui_running(self, running: bool):
        self.is_running = running
        state = "disabled" if running else "normal"
        self.btn_manual.config(state=state)
        self.btn_optuna.config(state=state)
        self.btn_agentic.config(state=state)

    def _update_progress(self, percent: int, text: str):
        self.progress_bar["value"] = percent
        self.lbl_status.config(text=text)

    def _on_optimization_finished(self, res: Dict[str, Any], mode_label: str):
        self._set_ui_running(False)
        self.progress_bar["value"] = 100
        self.lbl_status.config(text=f"✅ Optimisation terminée [{mode_label}] | Distance : {res['best_distance']} km en {res['execution_time']}s")
        self._update_all_quadrants(res, mode_name=mode_label)

    # --------------------------------------------------------------------------
    # MISE À JOUR SYNCHRONE DES 4 QUADRANTS
    # --------------------------------------------------------------------------
    def _update_all_quadrants(self, res: Dict[str, Any], mode_name: str = ""):
        self.current_result = res
        self.current_tour = res["best_tour"]

        # 1. Mise à jour Quadrant 2 : KPIs
        self.kpi_best_val.config(text=f"{res['best_distance']} km")
        self.kpi_init_val.config(text=f"{res['initial_distance']} km")
        self.kpi_gain_val.config(text=f"+{res['improvement_percent']}%")
        self.kpi_time_val.config(text=f"{res['execution_time']} s")
        self.kpi_iter_val.config(text=str(res['generations_run']))

        # Chromosome solution formaté
        chromo_str = format_chromosome_display(self.current_tour, max_items=12)
        self.txt_chromosome.delete("1.0", tk.END)
        self.txt_chromosome.insert(tk.END, chromo_str)

        if res.get("is_valid", True):
            self.lbl_valid.config(text="✓ Circuit TSP valide : Boucle fermée (Entrepôt ➔ 40 Clients ➔ Entrepôt)", fg="#34D399")
        else:
            self.lbl_valid.config(text=f"⚠️ {res.get('validation_message')}", fg="#F87171")

        # Courbe de convergence
        self.ax_conv.clear()
        self.ax_conv.set_facecolor("#0F172A")
        gens = list(range(len(res["history_best"])))
        self.ax_conv.plot(gens, res["history_avg"], color="#F59E0B", linestyle=":", linewidth=1.5, label="Moyenne Population")
        self.ax_conv.plot(gens, res["history_best"], color="#10B981", linewidth=2.0, label="Meilleur Circuit")
        self.ax_conv.set_title("Courbe de Convergence (Distance en km)", fontsize=8, color="#ECEFF1", pad=4)
        self.ax_conv.set_xlabel("Itérations (Générations)", fontsize=7, color="#94A3B8")
        self.ax_conv.set_ylabel("Distance (km)", fontsize=7, color="#94A3B8")
        self.ax_conv.grid(True, linestyle="--", alpha=0.3, color="#334155")
        self.ax_conv.legend(fontsize=7, facecolor="#1E293B", edgecolor="#334155", labelcolor="#F8FAFC", loc="upper right")
        self.fig_conv.tight_layout()
        self.canvas_conv.draw()

        # 2. Mise à jour Quadrant 3 : Plan Cartésien 2D
        self.ax_cart.clear()
        self.ax_cart.set_facecolor("#0F172A")

        points_dict = {}
        for _, row in self.points_df.iterrows():
            pid = int(row["id"])
            x_km, y_km = gps_to_cartesian_km(row["latitude"], row["longitude"])
            points_dict[pid] = (x_km, y_km, row["name"])

        # Tracé du circuit ordonné
        if self.current_tour and len(self.current_tour) >= 2:
            tx = [points_dict[node][0] for node in self.current_tour]
            ty = [points_dict[node][1] for node in self.current_tour]
            self.ax_cart.plot(tx, ty, color="#38BDF8", linewidth=1.8, zorder=2, alpha=0.85)

        # Points clients (1 à 40)
        cx = [points_dict[i][0] for i in points_dict if i != DEPOT_ID]
        cy = [points_dict[i][1] for i in points_dict if i != DEPOT_ID]
        self.ax_cart.scatter(cx, cy, color="#F59E0B", s=35, zorder=3, edgecolors="#1E293B", linewidths=0.8)

        for i in points_dict:
            if i != DEPOT_ID:
                self.ax_cart.annotate(f"P{i:02d}", (points_dict[i][0], points_dict[i][1]),
                                      fontsize=6, color="#F8FAFC", xytext=(0, 4),
                                      textcoords="offset points", ha="center")

        # Entrepôt central (★ Étoile rouge)
        depot_x, depot_y, _ = points_dict[DEPOT_ID]
        self.ax_cart.scatter([depot_x], [depot_y], color="#EF4444", marker="*", s=160, zorder=4,
                             edgecolors="#FFFFFF", linewidths=1.2, label="Entrepôt Central")

        self.ax_cart.set_title("Plan Cartésien 2D (Déplacements en km)", fontsize=8, color="#ECEFF1", pad=4)
        self.ax_cart.set_xlabel("Axe X (Est-Ouest en km)", fontsize=7, color="#94A3B8")
        self.ax_cart.set_ylabel("Axe Y (Nord-Sud en km)", fontsize=7, color="#94A3B8")
        self.ax_cart.grid(True, linestyle="--", alpha=0.3, color="#334155")
        self.ax_cart.set_aspect("equal", adjustable="datalim")
        self.fig_cart.tight_layout()
        self.canvas_cart.draw()

        # 3. Mise à jour Quadrant 4 : Folium & Segments
        fmap, segments = create_meknes_folium_map(self.points_df, self.current_tour, self.distance_matrix)
        self.map_html_path.parent.mkdir(parents=True, exist_ok=True)
        fmap.save(str(self.map_html_path))

        # Rechargement de l'iframe HTML si tkinterweb actif
        if HAS_TKINTERWEB:
            try:
                self.map_view_frame.load_file(str(self.map_html_path))
            except Exception:
                pass

        # Remplissage du tableau des segments
        for item in self.tree_segments.get_children():
            self.tree_segments.delete(item)

        for s in segments:
            self.tree_segments.insert("", "end", values=(
                s["Segment"],
                s["Origine"],
                s["Destination"],
                f"{s['Distance (km)']:.2f}",
                f"{s['Cumulée (km)']:.2f}"
            ))

    def _open_map_in_browser(self):
        """Ouvre la carte Folium interactive dans le navigateur par défaut de l'utilisateur."""
        if self.map_html_path.exists():
            webbrowser.open(f"file://{self.map_html_path.resolve()}")
        else:
            messagebox.showinfo("Information", "Veuillez d'abord exécuter une optimisation.")


def main():
    root = tk.Tk()
    app = TSPMeknesTkinterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
