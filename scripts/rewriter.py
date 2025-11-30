#!/usr/bin/env python3
"""
Rewriter Gemini V3 pour L'Alerte Immo & Taux
Persona: "L'Insider Whistleblower" - Expert financier rebelle et cynique

V3: CTA dynamique, maillage interne, Google Trends, Forums FAQ, Prix par ville
"""

import os
import json
import argparse
from datetime import datetime
from pathlib import Path

from google import genai

# Configuration
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CONTENT_DIR = BASE_DIR / "content" / "articles"

# Clé API Gemini (depuis variable d'environnement)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# ============================================================
# MAILLAGE INTERNE - Liens automatiques
# ============================================================
INTERNAL_LINKS = {
    "calculer": "/calculateur",
    "capacité d'emprunt": "/calculateur",
    "simulateur": "/calculateur",
    "simulation": "/calculateur",
    "combien emprunter": "/calculateur",
    "PTZ": "/ptz-pret-taux-zero",
    "prêt à taux zéro": "/ptz-pret-taux-zero",
    "MaPrimeRénov": "/aides-renovation",
    "DPE": "/dpe-diagnostic",
    "Paris": "/taux-immobilier-paris",
    "Lyon": "/taux-immobilier-lyon",
    "Marseille": "/taux-immobilier-marseille",
}

# ============================================================
# PROMPTS "INSIDER WHISTLEBLOWER"
# ============================================================

PERSONA_BASE = """Tu es "L'Insider" - un expert financier rebelle et cynique qui dit ce que les banques cachent.

TON STYLE:
- Urgent, direct, sans filtre
- Phrases courtes et percutantes
- Tu tutoies le lecteur
- Tu donnes ton AVIS tranché (acheter MAINTENANT ou ATTENDRE)
- Tu utilises des métaphores ("la fenêtre se referme", "les banques se frottent les mains")
- Tu conclus TOUJOURS par: "La fenêtre de tir se referme."

CE QUE TU NE FAIS JAMAIS:
- Être neutre ou timide
- Dire "il est conseillé de consulter un professionnel"
- Utiliser du jargon bancaire ennuyeux
"""

PROMPT_MORNING = PERSONA_BASE + """
MISSION: Écris le FLASH MARCHÉ du matin (300-400 mots).

DONNÉES DU JOUR:
{rates_data}

DERNIÈRES NEWS:
{news_data}

{trends_section}

{official_section}

FORMAT ATTENDU:
1. Un titre H2 clickbait intelligent (ex: "## Les taux s'envolent: ta banque ne t'appellera pas")
2. Analyse des chiffres (ça monte ou ça baisse? Pourquoi?)
3. Ce que ça signifie concrètement pour quelqu'un qui veut acheter
4. TON VERDICT: Acheter maintenant ou attendre?
5. {cta_instruction}
6. Conclusion avec "La fenêtre de tir se referme."

RÈGLES MAILLAGE INTERNE (IMPORTANT):
- Si tu parles de "calculer sa capacité", mets un lien vers [calculer ta capacité](/calculateur)
- Si tu parles du PTZ, mets un lien vers [PTZ 2025](/ptz-pret-taux-zero)
- Si tu parles de rénovation/DPE, mets un lien vers [aides rénovation](/aides-renovation)

Écris en Markdown avec liens internes.
"""

PROMPT_EVENING = PERSONA_BASE + """
MISSION: Écris le RÉCAP DU SOIR (500-600 mots).

ARTICLES DE LA JOURNÉE:
{news_data}

DONNÉES TAUX:
{rates_data}

{trends_section}

{official_section}

FORMAT ATTENDU:
1. Titre H2 accrocheur style newsletter
2. Résumé de la journée en 3 points clés
3. L'info que les médias mainstream ont "oublié" de mentionner
4. UN conseil actionnable (ex: "Renégocie ton assurance MAINTENANT")
5. Prédiction pour demain (monte ou descend?)
6. {cta_instruction}
7. Conclusion avec "La fenêtre de tir se referme."

RÈGLES MAILLAGE INTERNE (IMPORTANT):
- Insère au moins 2 liens internes vers les pages du site
- [calculer ta capacité](/calculateur)
- [simulation prêt](/calculateur)
- [PTZ 2025](/ptz-pret-taux-zero)

Écris en Markdown avec liens internes.
"""


def load_data():
    """Charge toutes les données scrapées (V3 avec forums + prix)"""
    data = {
        "rates": {},
        "news": [],
        "trends": {},
        "official": [],
        "forums": {},
        "city_prices": {},
        "auctions": {}
    }

    files_map = {
        "rates": "rates.json",
        "news": "news.json",
        "trends": "trends.json",
        "official": "official.json",
        "forums": "forums.json",
        "city_prices": "city_prices.json",
        "auctions": "auctions.json"
    }

    for key, filename in files_map.items():
        filepath = DATA_DIR / filename
        if filepath.exists():
            try:
                data[key] = json.loads(filepath.read_text())
            except:
                pass

    return data


def get_rate_trend(rates):
    """Détermine la tendance générale des taux (hausse/baisse/stable)"""
    oat = rates.get("oat_10y", {})
    direction = oat.get("direction", "stable")
    change = oat.get("change", 0)

    if direction == "up" or change > 0.02:
        return "hausse"
    elif direction == "down" or change < -0.02:
        return "baisse"
    return "stable"


def get_dynamic_cta(trend):
    """Génère l'instruction CTA selon la tendance"""
    cta_instructions = {
        "hausse": """IMPORTANT - CTA URGENCE:
Insère cette phrase: "⚠️ **Les taux montent.** [Calcule ta capacité d'emprunt MAINTENANT](/calculateur) avant de perdre 10 000€ de pouvoir d'achat."
Ton message: FONCE, ne laisse pas passer cette fenêtre.""",

        "baisse": """IMPORTANT - CTA RENÉGOCIATION:
Insère cette phrase: "📉 **Les taux baissent.** C'est le moment de [renégocier ton prêt](/calculateur) ou de faire jouer la concurrence."
Ton message: Les banques ne t'appelleront pas, c'est à TOI de bouger.""",

        "stable": """IMPORTANT - CTA PRÉPARATION:
Insère cette phrase: "⏳ **Taux stables... pour l'instant.** [Prépare ton dossier](/calculateur) MAINTENANT pour être prêt quand ça bougera."
Ton message: Le calme avant la tempête. Prépare-toi."""
    }
    return cta_instructions.get(trend, cta_instructions["stable"])


def format_rates_for_prompt(rates):
    """Formate les taux pour le prompt"""
    lines = []
    for key, data in rates.items():
        if key == "updated_at":
            continue
        if isinstance(data, dict):
            arrow = "↑" if data.get("direction") == "up" else ("↓" if data.get("direction") == "down" else "→")
            lines.append(f"- {data.get('name', key)}: {data.get('value')}% ({arrow} {data.get('change', 0):+.2f})")
    return "\n".join(lines)


def format_news_for_prompt(news):
    """Formate les news pour le prompt"""
    lines = []
    for i, article in enumerate(news[:5], 1):
        lines.append(f"{i}. {article.get('title', 'Sans titre')}")
        if article.get('summary'):
            # Nettoyer le HTML
            summary = article['summary'][:200].replace('<', '').replace('>', '')
            lines.append(f"   Résumé: {summary}...")
    return "\n".join(lines)


def format_trends_for_prompt(trends):
    """Formate les Google Trends pour le prompt"""
    if not trends or not trends.get("trending"):
        return ""

    lines = ["🔥 GOOGLE TRENDS (mots-clés qui explosent):"]

    for t in trends.get("trending", [])[:3]:
        status = "🚀 BREAKOUT" if t.get("rising") else ""
        lines.append(f"- \"{t.get('keyword')}\": score {t.get('score')} ({t.get('change'):+d}) {status}")

    if trends.get("breakout"):
        lines.append(f"\n⚡ MOT-CLÉ BREAKOUT: \"{trends['breakout']}\" - INCLUS CE SUJET DANS TON ARTICLE!")

    return "\n".join(lines)


def format_official_for_prompt(official):
    """Formate les news officielles pour le prompt"""
    if not official:
        return ""

    lines = ["🏛️ SOURCES OFFICIELLES (Service-Public, ANIL):"]
    for article in official[:2]:
        lines.append(f"- {article.get('title', 'Sans titre')}")

    return "\n".join(lines)


def format_forums_for_prompt(forums):
    """Formate les questions des forums pour le prompt"""
    if not forums or not forums.get("questions"):
        return ""

    lines = ["💬 QUESTIONS RÉELLES DES FORUMS (utilise-les pour une section FAQ):"]
    for q in forums.get("questions", [])[:5]:
        lines.append(f"- \"{q.get('question', '')}\"")

    lines.append("\n👉 INTÈGRE AU MOINS 2 DE CES QUESTIONS DANS TON ARTICLE (section FAQ ou dans le texte)")

    return "\n".join(lines)


def format_city_prices_for_prompt(city_prices):
    """Formate les prix par ville pour le prompt"""
    if not city_prices or not city_prices.get("cities"):
        return ""

    lines = ["🏠 TENDANCES PRIX PAR VILLE (mentionne 1-2 villes):"]

    # Top baisse (opportunité)
    if city_prices.get("top_baisse"):
        top = city_prices["top_baisse"]
        lines.append(f"📉 BAISSE: {top.get('city', 'N/A')} ({top.get('trend_percent', 0):.1f}%) - Lien: [{top.get('city')}]({top.get('url', '/courtier-immobilier')})")

    # Top hausse
    if city_prices.get("top_hausse"):
        top = city_prices["top_hausse"]
        lines.append(f"📈 HAUSSE: {top.get('city', 'N/A')} ({top.get('trend_percent', 0):+.1f}%)")

    # Opportunités
    opps = city_prices.get("opportunities", [])[:3]
    if opps:
        lines.append(f"🔥 OPPORTUNITÉS ({len(opps)} villes en baisse >2%): {', '.join([o.get('city', '') for o in opps])}")

    return "\n".join(lines)


def format_auctions_for_prompt(auctions):
    """Formate les enchères pour le prompt"""
    if not auctions or not auctions.get("auctions"):
        return ""

    lines = ["⚖️ ENCHÈRES JUDICIAIRES (pour les investisseurs):"]
    for auction in auctions.get("auctions", [])[:2]:
        lines.append(f"- {auction.get('title', 'Bien')} - {auction.get('location', '')} - {auction.get('price', 'NC')}")

    lines.append("👉 Mentionne les enchères comme opportunité pour investisseurs avertis")

    return "\n".join(lines)


def generate_article(mode="morning"):
    """Génère un article avec Gemini (V2 avec CTA dynamique + trends)"""
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY non définie!")
        return None

    # Nouvelle API Google GenAI
    client = genai.Client(api_key=GEMINI_API_KEY)

    # Charger TOUTES les données
    rates, news, trends, official = load_data()

    # Formater pour le prompt
    rates_str = format_rates_for_prompt(rates)
    news_str = format_news_for_prompt(news)
    trends_str = format_trends_for_prompt(trends)
    official_str = format_official_for_prompt(official)

    # Déterminer la tendance et le CTA dynamique
    trend = get_rate_trend(rates)
    cta_instruction = get_dynamic_cta(trend)

    print(f"📊 Tendance détectée: {trend.upper()}")
    if trends.get("breakout"):
        print(f"🔥 Breakout keyword: {trends['breakout']}")

    # Construire le prompt
    prompt = PROMPT_MORNING if mode == "morning" else PROMPT_EVENING
    prompt = prompt.format(
        rates_data=rates_str,
        news_data=news_str,
        trends_section=trends_str,
        official_section=official_str,
        cta_instruction=cta_instruction
    )

    print(f"🤖 Génération article ({mode})...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


def add_internal_links(content):
    """Ajoute des liens internes automatiquement si manquants"""
    for keyword, link in INTERNAL_LINKS.items():
        # Ne pas doubler les liens existants
        if f"({link})" not in content and keyword.lower() in content.lower():
            # Remplacer la première occurrence
            import re
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            match = pattern.search(content)
            if match:
                original = match.group()
                content = content.replace(original, f"[{original}]({link})", 1)
                break  # Un seul lien auto par keyword
    return content


def save_article(content, mode="morning", trend="stable"):
    """Sauvegarde l'article en Markdown avec métadonnées enrichies"""
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_suffix = "am" if mode == "morning" else "pm"
    filename = f"{date_str}-{time_suffix}.md"

    # Ajouter des liens internes si nécessaire
    content = add_internal_links(content)

    # Extraire le titre du contenu (première ligne ## ou # )
    lines = content.strip().split('\n')
    title = lines[0].replace('#', '').strip() if lines else "Flash Marché"
    # Nettoyer le titre des caractères spéciaux pour YAML
    title = title.replace('"', "'")

    # Frontmatter YAML enrichi
    frontmatter = f"""---
title: "{title}"
date: "{now.isoformat()}"
type: "{mode}"
author: "L'Insider"
trend: "{trend}"
image: "/images/charts/oat-30-jours.png"
---

"""

    filepath = CONTENT_DIR / filename
    filepath.write_text(frontmatter + content, encoding='utf-8')
    print(f"✅ Article sauvegardé: {filepath}")
    return filepath


def main():
    parser = argparse.ArgumentParser(description="Rewriter Gemini - L'Insider V2")
    parser.add_argument("--mode", choices=["morning", "evening"], required=True)
    args = parser.parse_args()

    print(f"🔔 L'ALERTE IMMO - Génération {args.mode.upper()}")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    # Charger les données pour déterminer la tendance
    rates, _, _, _ = load_data()
    trend = get_rate_trend(rates)

    print(f"📈 Tendance actuelle: {trend.upper()}")
    print("-" * 50)

    content = generate_article(args.mode)

    if content:
        save_article(content, args.mode, trend)
        print("-" * 50)
        print("✅ Génération terminée!")
        print(f"📊 CTA adapté à la tendance: {trend}")
    else:
        print("❌ Échec de la génération")
        exit(1)


if __name__ == "__main__":
    main()

