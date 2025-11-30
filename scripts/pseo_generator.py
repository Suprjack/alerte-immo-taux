#!/usr/bin/env python3
"""
Générateur pSEO Local - Multi-Crédit
Génère des pages optimisées SEO pour chaque ville × type de crédit
"""

import os
import json
from pathlib import Path
from datetime import datetime

# Configuration
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CONTENT_DIR = BASE_DIR / "content" / "pseo"

CURRENT_YEAR = datetime.now().year


def load_cities():
    """Charge la liste des villes"""
    cities_file = DATA_DIR / "cities.json"
    if cities_file.exists():
        data = json.loads(cities_file.read_text(encoding='utf-8'))
        return data.get("cities", [])
    return []


def load_credit_types():
    """Charge les types de crédit"""
    types_file = DATA_DIR / "credit_types.json"
    if types_file.exists():
        data = json.loads(types_file.read_text(encoding='utf-8'))
        return data.get("credit_types", []), data.get("affiliates", {})
    return [], {}


def generate_page_content(city, credit_type, affiliates):
    """Génère le contenu d'une page pSEO"""
    
    city_name = city["name"]
    city_slug = city["slug"]
    department = city["department"]
    region = city["region"]
    population = city.get("population", 0)
    
    ct = credit_type
    ct_id = ct["id"]
    
    # Remplacer les variables dans les templates
    title = ct["title_template"].format(city=city_name, year=CURRENT_YEAR)
    h1 = ct["h1_template"].format(city=city_name, year=CURRENT_YEAR)
    meta_desc = ct["meta_description"].format(city=city_name, year=CURRENT_YEAR)
    
    # Générer le contenu Markdown
    content = generate_markdown_content(city, credit_type, affiliates)
    
    # Frontmatter YAML
    frontmatter = f"""---
title: "{title}"
description: "{meta_desc}"
city: "{city_name}"
city_slug: "{city_slug}"
department: "{department}"
region: "{region}"
population: {population}
credit_type: "{ct_id}"
credit_name: "{ct['name']}"
cta_text: "{ct['cta_text']}"
cta_url: "{ct['cta_url']}"
icon: "{ct['icon']}"
date: "{datetime.now().strftime('%Y-%m-%d')}"
---

"""
    
    return frontmatter + content


def generate_markdown_content(city, credit_type, affiliates):
    """Génère le contenu Markdown de la page"""
    
    city_name = city["name"]
    region = city["region"]
    ct = credit_type
    icon = ct["icon"]
    
    # Contenu différent selon le type de crédit
    if ct["id"] == "courtier-immobilier":
        return generate_courtier_immo_content(city, ct, affiliates)
    elif ct["id"] == "rachat-credit":
        return generate_rachat_credit_content(city, ct, affiliates)
    elif ct["id"] == "credit-auto":
        return generate_credit_auto_content(city, ct, affiliates)
    elif ct["id"] == "pret-travaux":
        return generate_pret_travaux_content(city, ct, affiliates)
    elif ct["id"] == "credit-professionnel":
        return generate_credit_pro_content(city, ct, affiliates)
    elif ct["id"] == "assurance-pret":
        return generate_assurance_pret_content(city, ct, affiliates)
    
    return f"# {ct['name']} à {city_name}\n\nContenu à venir."


def generate_courtier_immo_content(city, ct, affiliates):
    """Contenu spécifique courtier immobilier"""
    name = city["name"]
    dept = city["department"]
    region = city["region"]
    pop = city.get("population", 0)
    year = CURRENT_YEAR
    
    return f"""## {ct['icon']} Trouvez le Meilleur Courtier Immobilier à {name}

Vous cherchez à **acheter un bien immobilier à {name}** ({dept}) ? Un courtier immobilier peut vous faire économiser des milliers d'euros sur votre crédit.

### Pourquoi passer par un courtier à {name} ?

| Avantage | Détail |
|----------|--------|
| 💰 **Économies** | Jusqu'à 0.3% de moins sur votre taux |
| ⏱️ **Gain de temps** | Il négocie avec 20+ banques pour vous |
| 📋 **Expertise** | Dossier optimisé = meilleur taux |
| 🆓 **Gratuit** | Commission payée par la banque |

### Les Taux Immobiliers à {name} en {year}

Les taux actuels en {region} :

| Durée | Taux moyen | Meilleur taux |
|-------|------------|---------------|
| 15 ans | 3.45% | 3.15% |
| 20 ans | 3.55% | 3.25% |
| 25 ans | 3.70% | 3.40% |

*Taux indicatifs mis à jour régulièrement*

### 🎯 Simulation Gratuite

Calculez votre capacité d'emprunt en 2 minutes :

[👉 **{ct['cta_text']}** 👈]({ct['cta_url']})

### Marché Immobilier à {name}

{name} ({pop:,} habitants) offre un marché immobilier dynamique en {region}. Que vous cherchiez un appartement en centre-ville ou une maison en périphérie, un courtier local connaît les spécificités du marché.

### FAQ - Courtier Immobilier {name}

**Combien coûte un courtier immobilier à {name} ?**
La plupart des courtiers sont gratuits pour l'emprunteur. Ils sont rémunérés par la banque qui accorde le prêt.

**Quel est le meilleur courtier immobilier à {name} ?**
Comparez plusieurs courtiers via notre simulateur pour trouver celui qui obtient les meilleurs taux.

**Combien puis-je emprunter à {name} ?**
Utilisez notre [calculateur de capacité d'emprunt](/calculateur) pour le savoir en 2 minutes.

---

📍 *Page mise à jour pour {name} ({dept}) - {region}*
"""


def generate_rachat_credit_content(city, ct, affiliates):
    """Contenu spécifique rachat de crédit"""
    name = city["name"]
    dept = city["department"]
    region = city["region"]
    year = CURRENT_YEAR

    return f"""## {ct['icon']} Rachat de Crédit à {name} - Réduisez vos Mensualités

Vous avez **plusieurs crédits en cours** et vos mensualités pèsent trop lourd ? Le rachat de crédit à {name} peut vous aider à retrouver du pouvoir d'achat.

### Qu'est-ce que le Rachat de Crédit ?

Le rachat de crédit (ou regroupement de crédits) consiste à **fusionner tous vos prêts** en un seul, avec :
- ✅ **Une seule mensualité** (au lieu de 3, 4 ou 5)
- ✅ **Un taux renégocié** (souvent plus bas)
- ✅ **Une durée adaptée** à votre budget

### Exemple Concret à {name}

| Situation Avant | Après Rachat |
|-----------------|--------------|
| Crédit immo : 800€/mois | |
| Crédit auto : 250€/mois | **Une seule mensualité** |
| Crédit conso : 150€/mois | **750€/mois** |
| **Total : 1200€/mois** | **Économie : 450€/mois** |

### 🎯 Simulation Gratuite en 2 Minutes

Découvrez combien vous pouvez économiser :

[👉 **{ct['cta_text']}** 👈]({ct['cta_url']})

### Qui Peut Bénéficier d'un Rachat de Crédit à {name} ?

- ✅ Propriétaires (rachat hypothécaire)
- ✅ Locataires (rachat consommation)
- ✅ Personnes en CDI, CDD, indépendants
- ✅ Retraités

### FAQ - Rachat de Crédit {name}

**Le rachat de crédit est-il intéressant ?**
Oui si vous avez au moins 2 crédits et que vos mensualités dépassent 33% de vos revenus.

**Combien coûte un rachat de crédit ?**
Des frais de dossier s'appliquent (1-2% du montant), mais l'économie mensuelle compense largement.

**Puis-je inclure un nouveau projet ?**
Oui ! Vous pouvez ajouter une trésorerie pour financer un nouveau projet (travaux, voiture...).

---

📍 *Rachat de crédit disponible à {name} ({dept}) - {region}*
"""


def generate_credit_auto_content(city, ct, affiliates):
    """Contenu spécifique crédit auto"""
    name = city["name"]
    dept = city["department"]
    region = city["region"]
    year = CURRENT_YEAR

    return f"""## {ct['icon']} Crédit Auto à {name} - Financez votre Véhicule

Vous souhaitez **acheter une voiture à {name}** ? Comparez les offres de crédit auto pour obtenir le meilleur taux.

### Taux Crédit Auto {year} à {name}

| Type de véhicule | Taux moyen | Meilleur taux |
|------------------|------------|---------------|
| Voiture neuve | 4.5% | 3.9% |
| Voiture occasion | 5.2% | 4.5% |
| Véhicule électrique | 3.9% | 2.9% |

### LOA, LLD ou Crédit Auto ?

| Solution | Avantage | Idéal pour |
|----------|----------|------------|
| **Crédit auto** | Vous êtes propriétaire | Garder le véhicule |
| **LOA** | Option d'achat à la fin | Changer souvent |
| **LLD** | Tout inclus (entretien) | Entreprises |

### 🎯 Simulation Gratuite

[👉 **{ct['cta_text']}** 👈]({ct['cta_url']})

### Conseils pour votre Crédit Auto à {name}

1. **Comparez les offres** - Ne prenez pas le crédit du concessionnaire sans comparer
2. **Négociez le prix** - Un prix plus bas = un crédit plus petit
3. **Apport personnel** - 10-20% d'apport = meilleur taux

---

📍 *Crédit auto disponible à {name} ({dept}) - {region}*
"""


def generate_pret_travaux_content(city, ct, affiliates):
    """Contenu spécifique prêt travaux"""
    name = city["name"]
    dept = city["department"]
    region = city["region"]
    year = CURRENT_YEAR

    return f"""## {ct['icon']} Prêt Travaux à {name} - Financez vos Rénovations

Vous avez un **projet de rénovation à {name}** ? Découvrez les meilleures solutions de financement.

### Types de Travaux Finançables

- 🏠 Rénovation énergétique (isolation, chauffage)
- 🛁 Salle de bain, cuisine
- 🏗️ Extension, surélévation
- 🌳 Aménagement extérieur
- 🔌 Mise aux normes électriques

### Prêt Travaux vs Éco-PTZ

| Solution | Montant max | Taux | Avantage |
|----------|-------------|------|----------|
| Prêt travaux classique | 75 000€ | 4-6% | Rapide, tous travaux |
| Éco-PTZ | 50 000€ | **0%** | Gratuit, travaux énergie |
| MaPrimeRénov + Prêt | Variable | Réduit | Cumul des aides |

### 🎯 Simulation Gratuite

[👉 **{ct['cta_text']}** 👈]({ct['cta_url']})

### Aides Disponibles à {name} ({region})

En plus du prêt, vous pouvez bénéficier de :
- ✅ MaPrimeRénov (jusqu'à 20 000€)
- ✅ Éco-PTZ (prêt à taux zéro)
- ✅ Aides locales {region}
- ✅ TVA réduite 5.5%

[Voir toutes les aides rénovation](/aides-renovation)

---

📍 *Prêt travaux disponible à {name} ({dept}) - {region}*
"""


def generate_credit_pro_content(city, ct, affiliates):
    """Contenu spécifique crédit professionnel"""
    name = city["name"]
    dept = city["department"]
    region = city["region"]

    return f"""## {ct['icon']} Crédit Professionnel à {name}

Vous êtes **entrepreneur, artisan ou commerçant à {name}** ? Trouvez le financement adapté à votre activité.

### Types de Financement Pro

| Besoin | Solution | Montant |
|--------|----------|---------|
| Trésorerie | Crédit court terme | 5-50K€ |
| Équipement | Crédit-bail / Leasing | 10-500K€ |
| Immobilier pro | Prêt immobilier pro | 50K-2M€ |
| Création | Prêt création entreprise | 10-100K€ |

### 🎯 Demande de Financement

[👉 **{ct['cta_text']}** 👈]({ct['cta_url']})

### Aides aux Entreprises à {name}

- France Num (digitalisation)
- BPI France (garanties)
- Aides régionales {region}

---

📍 *Crédit professionnel à {name} ({dept}) - {region}*
"""


def generate_assurance_pret_content(city, ct, affiliates):
    """Contenu spécifique assurance prêt"""
    name = city["name"]
    dept = city["department"]
    region = city["region"]

    return f"""## {ct['icon']} Assurance Prêt Immobilier à {name}

Vous avez un **crédit immobilier à {name}** ? Vous pouvez économiser jusqu'à 15 000€ en changeant d'assurance emprunteur.

### Pourquoi Changer d'Assurance ?

Depuis la **loi Lemoine (2022)**, vous pouvez changer d'assurance emprunteur **à tout moment**, sans frais.

| Assurance banque | Assurance externe |
|------------------|-------------------|
| 0.35% du capital | **0.10%** du capital |
| 250€/mois | **80€/mois** |
| Sur 20 ans : 60 000€ | Sur 20 ans : **19 200€** |

**💰 Économie potentielle : 40 800€**

### 🎯 Comparez les Assurances

[👉 **{ct['cta_text']}** 👈]({ct['cta_url']})

### Comment Changer d'Assurance à {name} ?

1. **Comparez** les offres (2 minutes)
2. **Choisissez** une assurance avec garanties équivalentes
3. **Envoyez** la demande de substitution
4. **Économisez** dès le mois suivant

---

📍 *Assurance prêt à {name} ({dept}) - {region}*
"""


def save_page(content, credit_type_id, city_slug):
    """Sauvegarde une page pSEO"""
    # Créer le dossier du type de crédit
    type_dir = CONTENT_DIR / credit_type_id
    type_dir.mkdir(parents=True, exist_ok=True)

    # Nom du fichier
    filename = f"{city_slug}.md"
    filepath = type_dir / filename

    filepath.write_text(content, encoding='utf-8')
    return filepath


def generate_all_pages(limit=None):
    """Génère toutes les pages pSEO"""
    cities = load_cities()
    credit_types, affiliates = load_credit_types()

    if limit:
        cities = cities[:limit]

    total_pages = len(cities) * len(credit_types)
    generated = 0

    print(f"🚀 Génération de {total_pages} pages pSEO")
    print(f"   {len(cities)} villes × {len(credit_types)} types de crédit")
    print("-" * 50)

    for city in cities:
        for ct in credit_types:
            content = generate_page_content(city, ct, affiliates)
            filepath = save_page(content, ct["id"], city["slug"])
            generated += 1

            if generated % 100 == 0:
                print(f"   ✅ {generated}/{total_pages} pages générées...")

    print("-" * 50)
    print(f"✅ {generated} pages générées avec succès!")
    return generated


def generate_sitemap():
    """Génère le sitemap.xml pour les pages pSEO"""
    cities = load_cities()
    credit_types, _ = load_credit_types()

    urls = []
    base_url = "https://alerte-immo-taux.netlify.app"

    for city in cities:
        for ct in credit_types:
            url = f"{base_url}/{ct['id']}/{city['slug']}"
            urls.append(url)

    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for url in urls:
        sitemap += f"  <url>\n"
        sitemap += f"    <loc>{url}</loc>\n"
        sitemap += f"    <changefreq>weekly</changefreq>\n"
        sitemap += f"    <priority>0.8</priority>\n"
        sitemap += f"  </url>\n"

    sitemap += '</urlset>'

    sitemap_path = BASE_DIR / "public" / "sitemap-pseo.xml"
    sitemap_path.parent.mkdir(parents=True, exist_ok=True)
    sitemap_path.write_text(sitemap, encoding='utf-8')

    print(f"✅ Sitemap généré: {sitemap_path}")
    print(f"   {len(urls)} URLs")
    return sitemap_path


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Générateur pSEO Local Multi-Crédit")
    parser.add_argument("--limit", type=int, help="Limiter le nombre de villes")
    parser.add_argument("--sitemap", action="store_true", help="Générer aussi le sitemap")
    args = parser.parse_args()

    print("=" * 50)
    print("🏙️ GÉNÉRATEUR pSEO LOCAL - MULTI-CRÉDIT")
    print("=" * 50)

    # Générer les pages
    generate_all_pages(limit=args.limit)

    # Générer le sitemap si demandé
    if args.sitemap:
        print()
        generate_sitemap()


if __name__ == "__main__":
    main()

