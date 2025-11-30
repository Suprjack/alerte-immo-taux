#!/usr/bin/env python3
"""
Scraper pour L'Alerte Immo & Taux
Récupère les taux (OAT, Euribor) et les news immobilier
"""

import os
import json
import argparse
import feedparser
import requests
from datetime import datetime
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CONTENT_DIR = BASE_DIR / "content" / "articles"

# Sources RSS pour les news immobilier
NEWS_SOURCES = [
    {
        "name": "Google News - Taux Immobilier",
        "url": "https://news.google.com/rss/search?q=taux+immobilier+france&hl=fr&gl=FR&ceid=FR:fr",
        "category": "taux"
    },
    {
        "name": "Google News - Crédit Immobilier",
        "url": "https://news.google.com/rss/search?q=crédit+immobilier+banque&hl=fr&gl=FR&ceid=FR:fr",
        "category": "credit"
    },
    {
        "name": "Google News - BCE Taux",
        "url": "https://news.google.com/rss/search?q=BCE+taux+directeur&hl=fr&gl=FR&ceid=FR:fr",
        "category": "bce"
    },
    {
        "name": "Google News - Immobilier Prix",
        "url": "https://news.google.com/rss/search?q=prix+immobilier+france&hl=fr&gl=FR&ceid=FR:fr",
        "category": "prix"
    }
]

# API pour les taux (sources publiques)
RATES_SOURCES = {
    "oat_10y": {
        "name": "OAT 10 ans",
        "url": "https://www.boursorama.com/bourse/obligations/cours/1rPFR10YT/",
        "fallback": 3.12
    },
    "euribor_3m": {
        "name": "Euribor 3 mois",
        "url": "https://www.euribor-rates.eu/fr/taux-euribor-actuels/2/euribor-taux-3-mois/",
        "fallback": 3.45
    }
}


def fetch_news(max_articles=5):
    """Récupère les dernières news depuis les flux RSS"""
    all_articles = []
    
    for source in NEWS_SOURCES:
        try:
            feed = feedparser.parse(source["url"])
            for entry in feed.entries[:3]:
                article = {
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "summary": entry.get("summary", "")[:500],
                    "source": source["name"],
                    "category": source["category"]
                }
                all_articles.append(article)
        except Exception as e:
            print(f"Erreur scraping {source['name']}: {e}")
    
    # Trier par date et limiter
    all_articles.sort(key=lambda x: x.get("published", ""), reverse=True)
    return all_articles[:max_articles]


def fetch_rates():
    """Récupère les taux actuels (avec fallback)"""
    rates = {}
    previous_rates = load_previous_rates()
    
    for rate_id, config in RATES_SOURCES.items():
        # Pour l'instant on utilise les fallbacks (à remplacer par vraie API)
        current_value = config["fallback"]
        previous_value = previous_rates.get(rate_id, {}).get("value", current_value)
        
        change = round(current_value - previous_value, 3)
        direction = "up" if change > 0 else ("down" if change < 0 else "stable")
        
        rates[rate_id] = {
            "name": config["name"],
            "value": current_value,
            "change": change,
            "direction": direction
        }
    
    rates["updated_at"] = datetime.now().isoformat()
    return rates


def load_previous_rates():
    """Charge les taux précédents pour calculer la variation"""
    rates_file = DATA_DIR / "rates.json"
    if rates_file.exists():
        return json.loads(rates_file.read_text())
    return {}


def save_rates(rates):
    """Sauvegarde les taux dans un fichier JSON"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rates_file = DATA_DIR / "rates.json"
    rates_file.write_text(json.dumps(rates, indent=2, ensure_ascii=False))
    print(f"✅ Taux sauvegardés: {rates_file}")


def save_news(articles):
    """Sauvegarde les articles dans un fichier JSON"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    news_file = DATA_DIR / "news.json"
    news_file.write_text(json.dumps(articles, indent=2, ensure_ascii=False))
    print(f"✅ {len(articles)} articles sauvegardés: {news_file}")
    return articles


def main():
    parser = argparse.ArgumentParser(description="Scraper Alerte Immo & Taux")
    parser.add_argument("--mode", choices=["morning", "evening", "all"], default="all")
    args = parser.parse_args()

    print(f"🔄 Scraping en mode: {args.mode}")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("-" * 40)

    # Toujours récupérer les taux
    rates = fetch_rates()
    save_rates(rates)

    # Récupérer les news
    articles = fetch_news(max_articles=5 if args.mode == "morning" else 8)
    save_news(articles)

    print("-" * 40)
    print(f"✅ Scraping terminé!")
    return {"rates": rates, "articles": articles}


if __name__ == "__main__":
    main()

