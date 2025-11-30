#!/usr/bin/env python3
"""
Scraper V3 pour L'Alerte Immo & Taux
- News immobilier (RSS)
- Sources officielles (Service-Public, ANIL)
- Google Trends (breakout keywords)
- Forums (MoneyVox, ForumConstruire) - vraies questions des gens
- Prix immobilier par ville (baisse/hausse)
- Enchères judiciaires (leads investisseurs)
"""

import os
import json
import re
import argparse
import feedparser
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

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
# FORUMS - Vraies questions des gens (GOLD pour SEO)
# ============================================
FORUMS_SOURCES = [
    {
        "name": "MoneyVox - Crédit Immobilier",
        "url": "https://www.moneyvox.fr/forums/fil/credit-immobilier.30/",
        "category": "credit",
        "type": "forum"
    },
    {
        "name": "MoneyVox - Rachat de Crédit",
        "url": "https://www.moneyvox.fr/forums/fil/rachat-de-credit.31/",
        "category": "rachat",
        "type": "forum"
    },
    {
        "name": "ForumConstruire - Financement",
        "url": "https://www.forumconstruire.com/construire/forum-financement-104.php",
        "category": "financement",
        "type": "forum"
    }
]

# ============================================
# VILLES À TRACKER (Top 50 + villes pSEO)
# ============================================
TOP_CITIES = [
    "paris", "marseille", "lyon", "toulouse", "nice", "nantes", "strasbourg",
    "montpellier", "bordeaux", "lille", "rennes", "reims", "toulon", "grenoble",
    "dijon", "angers", "nimes", "aix-en-provence", "saint-etienne", "clermont-ferrand",
    "le-havre", "brest", "tours", "amiens", "limoges", "perpignan", "metz",
    "besancon", "orleans", "rouen", "mulhouse", "caen", "nancy", "argenteuil",
    "saint-denis", "montreuil", "roubaix", "tourcoing", "avignon", "dunkerque"
]

# ============================================
# ENCHÈRES JUDICIAIRES (Leads investisseurs)
# ============================================
AUCTION_SOURCES = [
    {
        "name": "Licitor",
        "url": "https://www.licitor.com/ventes-aux-encheres-immobilieres.html",
        "type": "auction"
    }
]


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


# ============================================
# SCRAPING FORUMS - Questions réelles des gens
# ============================================
def fetch_forum_topics(max_topics=10):
    """Scrape les sujets tendance des forums immobilier"""
    all_topics = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    for source in FORUMS_SOURCES:
        try:
            print(f"  → Scraping {source['name']}...")
            response = requests.get(source["url"], headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            # MoneyVox structure
            if "moneyvox" in source["url"]:
                threads = soup.select('.structItem-title a')[:5]
                for thread in threads:
                    title = thread.get_text(strip=True)
                    link = thread.get('href', '')
                    if not link.startswith('http'):
                        link = f"https://www.moneyvox.fr{link}"

                    all_topics.append({
                        "title": title,
                        "link": link,
                        "source": source["name"],
                        "category": source["category"],
                        "scraped_at": datetime.now().isoformat()
                    })

            # ForumConstruire structure
            elif "forumconstruire" in source["url"]:
                threads = soup.select('.sujet_titre a')[:5]
                for thread in threads:
                    title = thread.get_text(strip=True)
                    link = thread.get('href', '')
                    if not link.startswith('http'):
                        link = f"https://www.forumconstruire.com{link}"

                    all_topics.append({
                        "title": title,
                        "link": link,
                        "source": source["name"],
                        "category": source["category"],
                        "scraped_at": datetime.now().isoformat()
                    })

        except Exception as e:
            print(f"  ⚠️ Erreur {source['name']}: {e}")

    # Extraire les questions clés (pour créer du contenu FAQ)
    questions = extract_questions_from_topics(all_topics)

    return {
        "topics": all_topics[:max_topics],
        "questions": questions,
        "count": len(all_topics),
        "updated_at": datetime.now().isoformat()
    }


def extract_questions_from_topics(topics):
    """Extrait les vraies questions des titres de forum"""
    questions = []
    question_patterns = [
        r"(comment|combien|pourquoi|quand|est-ce que|peut-on|faut-il|quel|quelle)",
        r"\?$",
        r"(refus|problème|aide|conseil|avis)"
    ]

    for topic in topics:
        title = topic["title"].lower()
        is_question = any(re.search(pattern, title, re.IGNORECASE) for pattern in question_patterns)

        if is_question:
            questions.append({
                "question": topic["title"],
                "category": topic["category"],
                "source": topic["source"]
            })

    return questions[:10]  # Top 10 questions


def load_previous_rates():
    """Charge les taux précédents pour calculer la variation"""
    rates_file = DATA_DIR / "rates.json"
    if rates_file.exists():
        return json.loads(rates_file.read_text())
    return {}


# ============================================
# PRIX IMMOBILIER PAR VILLE (SEO Local Gold)
# ============================================
def fetch_city_prices(cities=None, max_cities=20):
    """Récupère les tendances de prix par ville via MeilleursAgents"""
    if cities is None:
        cities = TOP_CITIES[:max_cities]

    city_data = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    print(f"  → Analyse prix pour {len(cities)} villes...")

    for city in cities[:max_cities]:
        try:
            # Utiliser l'API DVF (Demandes de Valeurs Foncières) - données publiques
            # ou scraper MeilleursAgents pour les tendances
            url = f"https://www.meilleursagents.com/prix-immobilier/{city}/"
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extraire le prix moyen
                price_elem = soup.select_one('.price-evolution__price')
                trend_elem = soup.select_one('.price-evolution__variation')

                price = None
                trend = None
                trend_value = 0

                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price_match = re.search(r'([\d\s]+)\s*€', price_text.replace(' ', ''))
                    if price_match:
                        price = int(price_match.group(1).replace(' ', ''))

                if trend_elem:
                    trend_text = trend_elem.get_text(strip=True)
                    if '+' in trend_text:
                        trend = "hausse"
                        trend_match = re.search(r'\+([\d,]+)', trend_text)
                        if trend_match:
                            trend_value = float(trend_match.group(1).replace(',', '.'))
                    elif '-' in trend_text:
                        trend = "baisse"
                        trend_match = re.search(r'-([\d,]+)', trend_text)
                        if trend_match:
                            trend_value = -float(trend_match.group(1).replace(',', '.'))
                    else:
                        trend = "stable"

                city_data.append({
                    "city": city.replace('-', ' ').title(),
                    "slug": city,
                    "price_m2": price,
                    "trend": trend,
                    "trend_percent": trend_value,
                    "url": f"/courtier-immobilier/{city}",
                    "scraped_at": datetime.now().isoformat()
                })

        except Exception as e:
            print(f"    ⚠️ Erreur {city}: {e}")
            continue

    # Trier par variation (les plus grosses baisses d'abord = opportunités)
    city_data.sort(key=lambda x: x.get("trend_percent", 0))

    # Identifier les opportunités (baisses > 2%)
    opportunities = [c for c in city_data if c.get("trend_percent", 0) < -2]

    return {
        "cities": city_data,
        "opportunities": opportunities,
        "top_baisse": city_data[0] if city_data else None,
        "top_hausse": city_data[-1] if city_data else None,
        "count": len(city_data),
        "updated_at": datetime.now().isoformat()
    }


# ============================================
# ENCHÈRES JUDICIAIRES (Leads Investisseurs)
# ============================================
def fetch_auctions(max_auctions=10):
    """Scrape les prochaines enchères immobilières"""
    auctions = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    # Scraper les annonces d'enchères
    try:
        # Licitor ou autre source d'enchères
        url = "https://www.licitor.com/ventes-aux-encheres-immobilieres.html"
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Adapter selon la structure du site
            listings = soup.select('.vente-item, .annonce, article')[:max_auctions]

            for listing in listings:
                title = listing.select_one('h2, h3, .titre')
                price = listing.select_one('.prix, .price')
                location = listing.select_one('.lieu, .location, .ville')
                date = listing.select_one('.date')

                if title:
                    auctions.append({
                        "title": title.get_text(strip=True)[:100],
                        "price": price.get_text(strip=True) if price else "NC",
                        "location": location.get_text(strip=True) if location else "France",
                        "date": date.get_text(strip=True) if date else "Prochainement",
                        "type": "enchere_judiciaire",
                        "scraped_at": datetime.now().isoformat()
                    })

    except Exception as e:
        print(f"  ⚠️ Erreur enchères: {e}")

    # Si pas de données, générer des exemples pour le contenu
    if not auctions:
        auctions = [
            {
                "title": "Appartement T3 - Vente judiciaire",
                "price": "À partir de 80 000€",
                "location": "Lyon 3ème",
                "date": "Décembre 2024",
                "type": "enchere_judiciaire",
                "note": "Données exemple - configurer scraping réel"
            }
        ]

    return {
        "auctions": auctions,
        "count": len(auctions),
        "updated_at": datetime.now().isoformat()
    }


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


def save_forums(data):
    """Sauvegarde les données forums"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    forums_file = DATA_DIR / "forums.json"
    forums_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"✅ {data['count']} topics forums sauvegardés + {len(data['questions'])} questions")
    return data


def save_city_prices(data):
    """Sauvegarde les prix par ville"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    prices_file = DATA_DIR / "city_prices.json"
    prices_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"✅ Prix pour {data['count']} villes sauvegardés")
    if data.get('opportunities'):
        print(f"   🔥 {len(data['opportunities'])} villes en baisse > 2%")
    return data


def save_auctions(data):
    """Sauvegarde les enchères"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    auctions_file = DATA_DIR / "auctions.json"
    auctions_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"✅ {data['count']} enchères sauvegardées")
    return data


def main():
    parser = argparse.ArgumentParser(description="Scraper V3 - Alerte Immo & Taux")
    parser.add_argument("--mode", choices=["morning", "evening", "all", "full"], default="all")
    parser.add_argument("--skip-forums", action="store_true", help="Skip forum scraping")
    parser.add_argument("--skip-prices", action="store_true", help="Skip city prices")
    parser.add_argument("--skip-auctions", action="store_true", help="Skip auctions")
    args = parser.parse_args()

    print(f"🔄 SCRAPER V3 - Mode: {args.mode}")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    results = {}

    # 1. Récupérer les taux
    print("\n📊 TAUX FINANCIERS")
    print("-" * 40)
    rates = fetch_rates()
    save_rates(rates)
    results["rates"] = rates

    # 2. Récupérer les news classiques
    print("\n📰 NEWS IMMOBILIER")
    print("-" * 40)
    articles = fetch_news(max_articles=5 if args.mode == "morning" else 8)
    save_news(articles)
    results["articles"] = articles

    # 3. Récupérer les news officielles (Service-Public, ANIL)
    print("\n🏛️ SOURCES OFFICIELLES (E-E-A-T)")
    print("-" * 40)
    official = fetch_official_news(max_articles=3)
    save_official(official)
    results["official"] = official

    # 4. Google Trends
    print("\n📈 GOOGLE TRENDS")
    print("-" * 40)
    trends = fetch_google_trends()
    save_trends(trends)
    results["trends"] = trends

    if trends.get("breakout"):
        print(f"   🔥 MOT-CLÉ BREAKOUT: {trends['breakout']}")

    # 5. Forums - Questions réelles des gens (SEO Gold)
    if not args.skip_forums:
        print("\n💬 FORUMS (Questions réelles)")
        print("-" * 40)
        forums = fetch_forum_topics(max_topics=10)
        save_forums(forums)
        results["forums"] = forums

        if forums.get("questions"):
            print(f"   📝 Questions extraites:")
            for q in forums["questions"][:3]:
                print(f"      • {q['question'][:60]}...")

    # 6. Prix par ville (SEO Local)
    if not args.skip_prices and args.mode in ["evening", "all", "full"]:
        print("\n🏠 PRIX IMMOBILIER PAR VILLE")
        print("-" * 40)
        city_prices = fetch_city_prices(max_cities=15)
        save_city_prices(city_prices)
        results["city_prices"] = city_prices

        if city_prices.get("top_baisse"):
            top = city_prices["top_baisse"]
            print(f"   📉 Plus forte baisse: {top['city']} ({top.get('trend_percent', 0):.1f}%)")
        if city_prices.get("top_hausse"):
            top = city_prices["top_hausse"]
            print(f"   📈 Plus forte hausse: {top['city']} ({top.get('trend_percent', 0):+.1f}%)")

    # 7. Enchères judiciaires (Leads investisseurs)
    if not args.skip_auctions and args.mode in ["evening", "full"]:
        print("\n⚖️ ENCHÈRES JUDICIAIRES")
        print("-" * 40)
        auctions = fetch_auctions(max_auctions=5)
        save_auctions(auctions)
        results["auctions"] = auctions

    # Résumé final
    print("\n" + "=" * 60)
    print("✅ SCRAPING V3 TERMINÉ!")
    print("-" * 40)
    print(f"   📊 Taux: OAT {rates.get('oat_10y', {}).get('value', 'N/A')}%")
    print(f"   📰 Articles: {len(articles)}")
    print(f"   🏛️ Sources officielles: {len(official)}")

    if trends.get("trending"):
        print(f"   📈 Trends: {len(trends['trending'])} mots-clés trackés")

    if "forums" in results:
        print(f"   💬 Forums: {results['forums']['count']} topics, {len(results['forums']['questions'])} questions")

    if "city_prices" in results:
        print(f"   🏠 Villes: {results['city_prices']['count']} analysées")
        if results['city_prices'].get('opportunities'):
            print(f"   🔥 Opportunités (baisse >2%): {len(results['city_prices']['opportunities'])} villes")

    if "auctions" in results:
        print(f"   ⚖️ Enchères: {results['auctions']['count']}")

    print("=" * 60)

    return results


if __name__ == "__main__":
    main()

