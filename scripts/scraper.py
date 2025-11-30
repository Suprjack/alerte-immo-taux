#!/usr/bin/env python3
"""
Scraper pour L'Alerte Immo & Taux
Récupère les taux (OAT, Euribor), news immobilier, Google Trends et sources officielles
"""

import os
import json
import argparse
import feedparser
import requests
from datetime import datetime
from pathlib import Path

# Google Trends
try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False
    print("⚠️ pytrends non installé - Google Trends désactivé")

# Configuration
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CONTENT_DIR = BASE_DIR / "content" / "articles"
IMAGES_DIR = BASE_DIR / "public" / "images"

# ============================================
# SOURCES RSS - NEWS IMMOBILIER
# ============================================
NEWS_SOURCES = [
    {
        "name": "Google News - Taux Immobilier",
        "url": "https://news.google.com/rss/search?q=taux+immobilier+france&hl=fr&gl=FR&ceid=FR:fr",
        "category": "taux",
        "priority": 1
    },
    {
        "name": "Google News - Crédit Immobilier",
        "url": "https://news.google.com/rss/search?q=crédit+immobilier+banque&hl=fr&gl=FR&ceid=FR:fr",
        "category": "credit",
        "priority": 1
    },
    {
        "name": "Google News - BCE Taux",
        "url": "https://news.google.com/rss/search?q=BCE+taux+directeur&hl=fr&gl=FR&ceid=FR:fr",
        "category": "bce",
        "priority": 2
    },
    {
        "name": "Google News - Immobilier Prix",
        "url": "https://news.google.com/rss/search?q=prix+immobilier+france&hl=fr&gl=FR&ceid=FR:fr",
        "category": "prix",
        "priority": 2
    }
]

# ============================================
# SOURCES OFFICIELLES (E-E-A-T Boost)
# ============================================
OFFICIAL_SOURCES = [
    {
        "name": "Service-Public.fr - Logement",
        "url": "https://www.service-public.fr/particuliers/actualites/rss",
        "category": "officiel",
        "priority": 0,  # Priorité max
        "keywords": ["logement", "immobilier", "ptz", "prêt", "crédit", "rénovation", "dpe", "énergie", "prime", "aide"]
    },
    {
        "name": "ANIL - Actualités",
        "url": "https://www.anil.org/feed/",
        "category": "officiel",
        "priority": 0,
        "keywords": ["prêt", "crédit", "taux", "logement", "locataire", "propriétaire", "copropriété"]
    },
    {
        "name": "Google News - PTZ 2025",
        "url": "https://news.google.com/rss/search?q=PTZ+prêt+taux+zéro+2025&hl=fr&gl=FR&ceid=FR:fr",
        "category": "aides",
        "priority": 1,
        "keywords": []
    },
    {
        "name": "Google News - MaPrimeRénov",
        "url": "https://news.google.com/rss/search?q=MaPrimeRénov+2025&hl=fr&gl=FR&ceid=FR:fr",
        "category": "aides",
        "priority": 1,
        "keywords": []
    },
    {
        "name": "Google News - DPE Diagnostic",
        "url": "https://news.google.com/rss/search?q=DPE+diagnostic+performance+énergétique&hl=fr&gl=FR&ceid=FR:fr",
        "category": "aides",
        "priority": 1,
        "keywords": []
    }
]

# ============================================
# GOOGLE TRENDS - Mots-clés à surveiller
# ============================================
TRENDS_KEYWORDS = [
    "taux immobilier",
    "crédit immobilier",
    "PTZ 2025",
    "taux usure",
    "renégociation prêt",
    "refus prêt immobilier",
    "MaPrimeRénov",
    "DPE",
    "prix immobilier baisse"
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


# ============================================
# FONCTIONS GOOGLE TRENDS
# ============================================
def fetch_google_trends():
    """Récupère les tendances Google pour nos mots-clés"""
    if not PYTRENDS_AVAILABLE:
        return {"trending": [], "breakout": None}

    try:
        pytrends = TrendReq(hl='fr-FR', tz=60)

        # Chercher les tendances relatives
        pytrends.build_payload(TRENDS_KEYWORDS[:5], cat=0, timeframe='now 7-d', geo='FR')
        interest = pytrends.interest_over_time()

        trends_data = {
            "trending": [],
            "breakout": None,
            "updated_at": datetime.now().isoformat()
        }

        if not interest.empty:
            # Trouver le mot-clé qui monte le plus
            latest = interest.iloc[-1].drop('isPartial', errors='ignore')
            previous = interest.iloc[-7].drop('isPartial', errors='ignore') if len(interest) > 7 else latest

            for keyword in latest.index:
                current_val = int(latest[keyword])
                prev_val = int(previous[keyword]) if keyword in previous else current_val
                change = current_val - prev_val

                trends_data["trending"].append({
                    "keyword": keyword,
                    "score": current_val,
                    "change": change,
                    "rising": change > 10
                })

            # Identifier le "breakout" (plus forte hausse)
            trends_data["trending"].sort(key=lambda x: x["change"], reverse=True)
            if trends_data["trending"] and trends_data["trending"][0]["change"] > 15:
                trends_data["breakout"] = trends_data["trending"][0]["keyword"]
                print(f"🔥 BREAKOUT détecté: {trends_data['breakout']}")

        return trends_data

    except Exception as e:
        print(f"⚠️ Erreur Google Trends: {e}")
        return {"trending": [], "breakout": None}


# ============================================
# FONCTIONS NEWS (avec sources officielles)
# ============================================
def fetch_news(max_articles=5):
    """Récupère les dernières news depuis les flux RSS"""
    all_articles = []

    # D'abord les sources NEWS classiques
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
                    "category": source["category"],
                    "priority": source.get("priority", 1),
                    "official": False
                }
                all_articles.append(article)
        except Exception as e:
            print(f"Erreur scraping {source['name']}: {e}")

    # Trier par date et limiter
    all_articles.sort(key=lambda x: x.get("published", ""), reverse=True)
    return all_articles[:max_articles]


def fetch_official_news(max_articles=3):
    """Récupère les news des sources officielles (Service-Public, ANIL)"""
    official_articles = []

    for source in OFFICIAL_SOURCES:
        try:
            feed = feedparser.parse(source["url"])
            keywords = source.get("keywords", [])

            for entry in feed.entries[:5]:
                title = entry.get("title", "").lower()
                summary = entry.get("summary", "").lower()

                # Si pas de keywords filtrés, ou si un keyword match
                is_relevant = not keywords or any(kw in title or kw in summary for kw in keywords)

                if is_relevant:
                    article = {
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "published": entry.get("published", ""),
                        "summary": entry.get("summary", "")[:500],
                        "source": source["name"],
                        "category": source["category"],
                        "priority": source.get("priority", 0),
                        "official": True
                    }
                    official_articles.append(article)

        except Exception as e:
            print(f"Erreur scraping officiel {source['name']}: {e}")

    # Dédupliquer et trier par priorité puis date
    official_articles.sort(key=lambda x: (x.get("priority", 1), x.get("published", "")), reverse=False)
    return official_articles[:max_articles]


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


def save_trends(trends):
    """Sauvegarde les tendances Google"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    trends_file = DATA_DIR / "trends.json"
    trends_file.write_text(json.dumps(trends, indent=2, ensure_ascii=False))
    print(f"✅ Trends sauvegardés: {trends_file}")
    return trends


def save_official(articles):
    """Sauvegarde les news officielles"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    official_file = DATA_DIR / "official.json"
    official_file.write_text(json.dumps(articles, indent=2, ensure_ascii=False))
    print(f"✅ {len(articles)} news officielles sauvegardées: {official_file}")
    return articles


def main():
    parser = argparse.ArgumentParser(description="Scraper Alerte Immo & Taux")
    parser.add_argument("--mode", choices=["morning", "evening", "all"], default="all")
    args = parser.parse_args()

    print(f"🔄 Scraping en mode: {args.mode}")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    # 1. Récupérer les taux
    print("\n📊 TAUX FINANCIERS")
    print("-" * 30)
    rates = fetch_rates()
    save_rates(rates)

    # 2. Récupérer les news classiques
    print("\n📰 NEWS IMMOBILIER")
    print("-" * 30)
    articles = fetch_news(max_articles=5 if args.mode == "morning" else 8)
    save_news(articles)

    # 3. Récupérer les news officielles (Service-Public, ANIL)
    print("\n🏛️ SOURCES OFFICIELLES")
    print("-" * 30)
    official = fetch_official_news(max_articles=3)
    save_official(official)

    # 4. Google Trends
    print("\n📈 GOOGLE TRENDS")
    print("-" * 30)
    trends = fetch_google_trends()
    save_trends(trends)

    if trends.get("breakout"):
        print(f"🔥 MOT-CLÉ BREAKOUT: {trends['breakout']}")

    print("\n" + "=" * 50)
    print(f"✅ Scraping terminé!")

    return {
        "rates": rates,
        "articles": articles,
        "official": official,
        "trends": trends
    }


if __name__ == "__main__":
    main()

