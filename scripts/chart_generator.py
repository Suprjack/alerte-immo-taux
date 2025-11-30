#!/usr/bin/env python3
"""
Générateur de graphiques pour L'Alerte Immo & Taux
Crée des images visuelles pour le SEO (Google Images)
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️ matplotlib non installé - Génération de graphiques désactivée")

# Configuration
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = BASE_DIR / "public" / "images" / "charts"

# Style du graphique (mode sombre pour matcher le site)
CHART_STYLE = {
    "bg_color": "#0a0a0a",
    "text_color": "#ffffff",
    "grid_color": "#333333",
    "line_color_primary": "#facc15",  # Jaune insider
    "line_color_secondary": "#ef4444",  # Rouge alerte
    "line_color_tertiary": "#22c55e",  # Vert
}


def load_rates_history():
    """Charge l'historique des taux (ou génère des données simulées)"""
    history_file = DATA_DIR / "rates_history.json"
    
    if history_file.exists():
        return json.loads(history_file.read_text())
    
    # Générer un historique simulé sur 30 jours
    history = []
    base_oat = 3.12
    base_euribor = 3.45
    
    for i in range(30, 0, -1):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        # Variation aléatoire réaliste
        import random
        oat = round(base_oat + random.uniform(-0.15, 0.15), 2)
        euribor = round(base_euribor + random.uniform(-0.10, 0.10), 2)
        
        history.append({
            "date": date,
            "oat_10y": oat,
            "euribor_3m": euribor
        })
        
        base_oat = oat
        base_euribor = euribor
    
    # Sauvegarder pour la prochaine fois
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    history_file.write_text(json.dumps(history, indent=2))
    
    return history


def update_rates_history(current_rates):
    """Ajoute les taux actuels à l'historique"""
    history = load_rates_history()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Vérifier si aujourd'hui existe déjà
    if history and history[-1]["date"] == today:
        history[-1] = {
            "date": today,
            "oat_10y": current_rates.get("oat_10y", {}).get("value", 3.12),
            "euribor_3m": current_rates.get("euribor_3m", {}).get("value", 3.45)
        }
    else:
        history.append({
            "date": today,
            "oat_10y": current_rates.get("oat_10y", {}).get("value", 3.12),
            "euribor_3m": current_rates.get("euribor_3m", {}).get("value", 3.45)
        })
    
    # Garder seulement 90 jours
    history = history[-90:]
    
    history_file = DATA_DIR / "rates_history.json"
    history_file.write_text(json.dumps(history, indent=2))
    
    return history


def generate_oat_chart(history, output_name="oat-30-jours.png"):
    """Génère le graphique OAT 10 ans"""
    if not MATPLOTLIB_AVAILABLE:
        print("❌ matplotlib requis pour générer les graphiques")
        return None
    
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Extraire les données
    dates = [datetime.strptime(h["date"], "%Y-%m-%d") for h in history[-30:]]
    values = [h["oat_10y"] for h in history[-30:]]
    
    # Créer le graphique
    fig, ax = plt.subplots(figsize=(10, 5), facecolor=CHART_STYLE["bg_color"])
    ax.set_facecolor(CHART_STYLE["bg_color"])
    
    # Tracer la ligne
    ax.plot(dates, values, color=CHART_STYLE["line_color_primary"], linewidth=2.5)
    ax.fill_between(dates, values, alpha=0.2, color=CHART_STYLE["line_color_primary"])
    
    # Style
    ax.set_title("📈 OAT 10 ans - 30 derniers jours", color=CHART_STYLE["text_color"], fontsize=14, fontweight='bold', pad=15)
    ax.set_ylabel("Taux (%)", color=CHART_STYLE["text_color"])
    
    # Grille
    ax.grid(True, color=CHART_STYLE["grid_color"], linestyle='--', alpha=0.5)
    ax.tick_params(colors=CHART_STYLE["text_color"])
    
    # Formater les dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    plt.xticks(rotation=45)
    
    # Spines
    for spine in ax.spines.values():
        spine.set_color(CHART_STYLE["grid_color"])
    
    # Ajouter la valeur actuelle
    current_value = values[-1]
    ax.annotate(f'{current_value}%', 
                xy=(dates[-1], current_value),
                xytext=(10, 10), textcoords='offset points',
                color=CHART_STYLE["line_color_primary"],
                fontsize=12, fontweight='bold')
    
    # Watermark
    fig.text(0.99, 0.01, "L'Alerte Immo & Taux", ha='right', va='bottom', 
             color=CHART_STYLE["text_color"], alpha=0.5, fontsize=8)
    
    plt.tight_layout()
    
    output_path = IMAGES_DIR / output_name
    plt.savefig(output_path, dpi=150, facecolor=CHART_STYLE["bg_color"])
    plt.close()
    
    print(f"✅ Graphique généré: {output_path}")
    return str(output_path)


def generate_comparison_chart(history, output_name="taux-comparaison.png"):
    """Génère un graphique comparatif OAT vs Euribor"""
    if not MATPLOTLIB_AVAILABLE:
        return None
    
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    
    dates = [datetime.strptime(h["date"], "%Y-%m-%d") for h in history[-30:]]
    oat_values = [h["oat_10y"] for h in history[-30:]]
    euribor_values = [h["euribor_3m"] for h in history[-30:]]
    
    fig, ax = plt.subplots(figsize=(10, 5), facecolor=CHART_STYLE["bg_color"])
    ax.set_facecolor(CHART_STYLE["bg_color"])
    
    ax.plot(dates, oat_values, color=CHART_STYLE["line_color_primary"], linewidth=2, label="OAT 10 ans")
    ax.plot(dates, euribor_values, color=CHART_STYLE["line_color_secondary"], linewidth=2, label="Euribor 3M")
    
    ax.set_title("📊 OAT 10 ans vs Euribor 3 mois", color=CHART_STYLE["text_color"], fontsize=14, fontweight='bold', pad=15)
    ax.set_ylabel("Taux (%)", color=CHART_STYLE["text_color"])
    ax.grid(True, color=CHART_STYLE["grid_color"], linestyle='--', alpha=0.5)
    ax.tick_params(colors=CHART_STYLE["text_color"])
    ax.legend(facecolor=CHART_STYLE["bg_color"], edgecolor=CHART_STYLE["grid_color"], labelcolor=CHART_STYLE["text_color"])
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    plt.xticks(rotation=45)
    
    for spine in ax.spines.values():
        spine.set_color(CHART_STYLE["grid_color"])
    
    fig.text(0.99, 0.01, "L'Alerte Immo & Taux", ha='right', va='bottom', 
             color=CHART_STYLE["text_color"], alpha=0.5, fontsize=8)
    
    plt.tight_layout()
    
    output_path = IMAGES_DIR / output_name
    plt.savefig(output_path, dpi=150, facecolor=CHART_STYLE["bg_color"])
    plt.close()
    
    print(f"✅ Graphique comparatif généré: {output_path}")
    return str(output_path)


def main():
    """Génère tous les graphiques"""
    print("📊 GÉNÉRATION DES GRAPHIQUES")
    print("=" * 40)
    
    # Charger les taux actuels
    rates_file = DATA_DIR / "rates.json"
    if rates_file.exists():
        current_rates = json.loads(rates_file.read_text())
        history = update_rates_history(current_rates)
    else:
        history = load_rates_history()
    
    # Générer les graphiques
    generate_oat_chart(history)
    generate_comparison_chart(history)
    
    print("=" * 40)
    print("✅ Tous les graphiques générés!")


if __name__ == "__main__":
    main()

