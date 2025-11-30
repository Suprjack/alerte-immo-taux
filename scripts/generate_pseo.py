#!/usr/bin/env python3
"""
Générateur de pages pSEO pour L'Alerte Immo & Taux
Génère des pages locales: taux-immobilier-{ville}, courtier-{ville}, etc.
"""

import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
PSEO_DIR = BASE_DIR / "content" / "pseo"
APP_DIR = BASE_DIR / "src" / "app"

# Top 50 villes françaises pour le SEO
VILLES = [
    "paris", "marseille", "lyon", "toulouse", "nice", "nantes", "strasbourg",
    "montpellier", "bordeaux", "lille", "rennes", "reims", "le-havre", "saint-etienne",
    "toulon", "grenoble", "dijon", "angers", "nimes", "villeurbanne", "clermont-ferrand",
    "le-mans", "aix-en-provence", "brest", "tours", "amiens", "limoges", "perpignan",
    "metz", "besancon", "orleans", "rouen", "mulhouse", "caen", "nancy", "argenteuil",
    "saint-denis", "roubaix", "tourcoing", "montreuil", "avignon", "dunkerque",
    "asnieres-sur-seine", "versailles", "colombes", "saint-paul", "aubervilliers",
    "vitry-sur-seine", "aulnay-sous-bois", "creteil"
]

# Templates de pages pSEO
TEMPLATES = {
    "taux-immobilier": {
        "title": "Taux Immobilier {ville_cap} - Meilleurs Taux Crédit 2024",
        "description": "Comparez les taux immobiliers à {ville_cap}. Taux actuels, évolution, et conseils d'experts.",
        "h1": "Taux Immobilier à {ville_cap}",
        "keywords": ["taux immobilier {ville}", "crédit immobilier {ville}", "prêt immobilier {ville}"]
    },
    "courtier": {
        "title": "Courtier Immobilier {ville_cap} - Comparatif 2024",
        "description": "Trouvez le meilleur courtier immobilier à {ville_cap}. Comparez les offres et économisez.",
        "h1": "Meilleur Courtier Immobilier à {ville_cap}",
        "keywords": ["courtier {ville}", "courtier immobilier {ville}", "courtier crédit {ville}"]
    },
    "rachat-credit": {
        "title": "Rachat de Crédit {ville_cap} - Simulation Gratuite",
        "description": "Simulez votre rachat de crédit à {ville_cap}. Réduisez vos mensualités jusqu'à 60%.",
        "h1": "Rachat de Crédit à {ville_cap}",
        "keywords": ["rachat crédit {ville}", "regroupement crédit {ville}"]
    }
}


def generate_page_content(template_type, ville):
    """Génère le contenu d'une page pSEO"""
    template = TEMPLATES[template_type]
    ville_cap = ville.replace("-", " ").title()
    
    content = f"""---
title: "{template['title'].format(ville_cap=ville_cap)}"
description: "{template['description'].format(ville_cap=ville_cap)}"
ville: "{ville}"
type: "pseo"
template: "{template_type}"
---

# {template['h1'].format(ville_cap=ville_cap)}

## Les taux actuels à {ville_cap}

Les taux immobiliers à {ville_cap} évoluent quotidiennement. Voici les dernières tendances :

| Durée | Taux moyen | Tendance |
|-------|------------|----------|
| 15 ans | 3.45% | ↗️ |
| 20 ans | 3.65% | ↗️ |
| 25 ans | 3.85% | → |

*Mis à jour automatiquement - Données indicatives*

## Pourquoi les taux varient à {ville_cap} ?

Le marché immobilier de {ville_cap} a ses spécificités. Les banques locales...

<div class="alert-cta">
  <h3>⚠️ Vérifiez VOTRE taux personnalisé</h3>
  <p>Chaque profil est unique. Simulez gratuitement.</p>
  <a href="/calculateur" class="btn">CALCULER MON TAUX →</a>
</div>

## L'avis de l'Insider sur {ville_cap}

> "{ville_cap} reste un marché tendu. Si tu attends que les taux baissent, tu risques de voir les prix remonter. La fenêtre de tir se referme."

---

📰 **Dernières alertes taux** *(flux automatique)*
"""
    return content


def generate_nextjs_page(template_type, ville):
    """Génère la structure Next.js pour la page dynamique"""
    # On utilise des pages dynamiques Next.js plutôt que des fichiers statiques
    pass


def main():
    print("🏗️ Génération des pages pSEO...")
    print(f"📍 {len(VILLES)} villes × {len(TEMPLATES)} templates = {len(VILLES) * len(TEMPLATES)} pages")
    
    PSEO_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    
    for template_type in TEMPLATES:
        for ville in VILLES:
            filename = f"{template_type}-{ville}.md"
            filepath = PSEO_DIR / filename
            
            content = generate_page_content(template_type, ville)
            filepath.write_text(content, encoding='utf-8')
            count += 1
    
    print(f"✅ {count} pages générées dans {PSEO_DIR}")
    
    # Générer un index JSON pour Next.js
    index = {
        "templates": list(TEMPLATES.keys()),
        "villes": VILLES,
        "total_pages": count
    }
    index_file = PSEO_DIR / "index.json"
    index_file.write_text(json.dumps(index, indent=2, ensure_ascii=False))
    print(f"✅ Index créé: {index_file}")


if __name__ == "__main__":
    main()

