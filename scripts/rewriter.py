#!/usr/bin/env python3
"""
Rewriter Gemini pour L'Alerte Immo & Taux
Persona: "L'Insider Whistleblower" - Expert financier rebelle et cynique
"""

import os
import json
import argparse
from datetime import datetime
from pathlib import Path

import google.generativeai as genai

# Configuration
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CONTENT_DIR = BASE_DIR / "content" / "articles"

# Clé API Gemini (depuis variable d'environnement)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

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
MISSION: Écris le FLASH MARCHÉ du matin (300 mots max).

DONNÉES DU JOUR:
{rates_data}

DERNIÈRES NEWS:
{news_data}

FORMAT ATTENDU:
1. Un titre clickbait intelligent (ex: "Les taux s'envolent: ta banque ne t'appellera pas")
2. Analyse des chiffres (ça monte ou ça baisse? Pourquoi?)
3. Ce que ça signifie concrètement pour quelqu'un qui veut acheter
4. TON VERDICT: Acheter maintenant ou attendre?
5. Conclusion avec "La fenêtre de tir se referme."

Écris en Markdown.
"""

PROMPT_EVENING = PERSONA_BASE + """
MISSION: Écris le RÉCAP DU SOIR (500 mots max).

ARTICLES DE LA JOURNÉE:
{news_data}

DONNÉES TAUX:
{rates_data}

FORMAT ATTENDU:
1. Titre accrocheur style newsletter
2. Résumé de la journée en 3 points clés
3. L'info que les médias mainstream ont "oublié" de mentionner
4. UN conseil actionnable (ex: "Renégocie ton assurance MAINTENANT")
5. Prédiction pour demain (monte ou descend?)
6. Conclusion avec "La fenêtre de tir se referme."

Écris en Markdown.
"""


def load_data():
    """Charge les données scrapées"""
    rates = {}
    news = []
    
    rates_file = DATA_DIR / "rates.json"
    if rates_file.exists():
        rates = json.loads(rates_file.read_text())
    
    news_file = DATA_DIR / "news.json"
    if news_file.exists():
        news = json.loads(news_file.read_text())
    
    return rates, news


def format_rates_for_prompt(rates):
    """Formate les taux pour le prompt"""
    lines = []
    for key, data in rates.items():
        if key == "updated_at":
            continue
        arrow = "↑" if data.get("direction") == "up" else ("↓" if data.get("direction") == "down" else "→")
        lines.append(f"- {data.get('name', key)}: {data.get('value')}% ({arrow} {data.get('change', 0):+.2f})")
    return "\n".join(lines)


def format_news_for_prompt(news):
    """Formate les news pour le prompt"""
    lines = []
    for i, article in enumerate(news[:5], 1):
        lines.append(f"{i}. {article.get('title', 'Sans titre')}")
        if article.get('summary'):
            lines.append(f"   Résumé: {article['summary'][:200]}...")
    return "\n".join(lines)


def generate_article(mode="morning"):
    """Génère un article avec Gemini"""
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY non définie!")
        return None
    
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    rates, news = load_data()
    rates_str = format_rates_for_prompt(rates)
    news_str = format_news_for_prompt(news)
    
    prompt = PROMPT_MORNING if mode == "morning" else PROMPT_EVENING
    prompt = prompt.format(rates_data=rates_str, news_data=news_str)
    
    print(f"🤖 Génération article ({mode})...")
    response = model.generate_content(prompt)
    
    return response.text


def save_article(content, mode="morning"):
    """Sauvegarde l'article en Markdown"""
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_suffix = "am" if mode == "morning" else "pm"
    filename = f"{date_str}-{time_suffix}.md"
    
    # Extraire le titre du contenu (première ligne # )
    lines = content.strip().split('\n')
    title = lines[0].replace('#', '').strip() if lines else "Flash Marché"
    
    # Frontmatter YAML
    frontmatter = f"""---
title: "{title}"
date: "{now.isoformat()}"
type: "{mode}"
author: "L'Insider"
---

"""
    
    filepath = CONTENT_DIR / filename
    filepath.write_text(frontmatter + content, encoding='utf-8')
    print(f"✅ Article sauvegardé: {filepath}")
    return filepath


def main():
    parser = argparse.ArgumentParser(description="Rewriter Gemini - L'Insider")
    parser.add_argument("--mode", choices=["morning", "evening"], required=True)
    args = parser.parse_args()

    print(f"🔔 L'ALERTE IMMO - Génération {args.mode.upper()}")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("-" * 40)

    content = generate_article(args.mode)
    
    if content:
        save_article(content, args.mode)
        print("-" * 40)
        print("✅ Génération terminée!")
    else:
        print("❌ Échec de la génération")


if __name__ == "__main__":
    main()

