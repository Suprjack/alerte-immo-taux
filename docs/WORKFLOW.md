# ⚙️ WORKFLOW - Comment ça Marche

## 🔄 Cycle Automatique Quotidien

```
        06:00 UTC                              17:00 UTC
        (08:00 Paris)                          (19:00 Paris)
            │                                      │
            ▼                                      ▼
    ┌───────────────┐                      ┌───────────────┐
    │  FLASH MATIN  │                      │  RÉCAP SOIR   │
    │   morning     │                      │   evening     │
    └───────┬───────┘                      └───────┬───────┘
            │                                      │
            ▼                                      ▼
    ┌─────────────────────────────────────────────────────┐
    │                   PIPELINE                           │
    │                                                      │
    │  1. 📥 Checkout repo                                │
    │  2. 🐍 Setup Python 3.11                            │
    │  3. 📦 Install dependencies                         │
    │  4. 🔍 Run scraper.py                               │
    │  5. 📊 Run chart_generator.py                       │
    │  6. 🤖 Run rewriter.py (Gemini)                     │
    │  7. 📤 Git commit & push                            │
    └─────────────────────────────────────────────────────┘
            │
            ▼
    ┌───────────────┐
    │   NETLIFY     │ ← Auto-rebuild déclenché
    │   DEPLOY      │
    └───────────────┘
            │
            ▼
    🌐 Site mis à jour !
```

---

## 📥 Étape 1 : Scraping (`scraper.py`)

### Sources de Données

| Source | Type | Données | Fichier Output |
|--------|------|---------|----------------|
| Google News | RSS | Actualités immo/crédit | `news.json` |
| APIs Taux | HTTP | OAT 10Y, Euribor 3M | `rates.json` |
| Google Trends | API | Keywords trending | `trends.json` |
| Service-Public | RSS | PTZ, aides, DPE | `official.json` |
| ANIL | RSS | Infos logement | `official.json` |

### Flux RSS Google News
```python
RSS_FEEDS = [
    "taux+immobilier",
    "crédit+immobilier", 
    "BCE+taux",
    "prix+immobilier+France"
]
```

### Keywords Google Trends
```python
TRENDS_KEYWORDS = [
    "taux immobilier",
    "crédit immobilier",
    "PTZ 2025",
    "taux usure",
    "refus prêt immobilier",
    "MaPrimeRénov",
    "DPE"
]
```

---

## 📊 Étape 2 : Graphiques (`chart_generator.py`)

### Graphiques Générés
1. **oat-30-jours.png** - Courbe OAT 10 ans sur 30 jours
2. **taux-comparaison.png** - OAT vs Euribor

### Style
- Thème sombre (fond #1a1a2e)
- Couleurs : rouge (#e94560), vert (#4ecca3)
- Format : 1200x630px (optimal réseaux sociaux)

---

## 🤖 Étape 3 : Génération IA (`rewriter.py`)

### Persona "L'Insider"
```
Tu es L'Insider, un analyste financier qui a quitté une grande banque 
pour révéler les vérités que le système cache. Tu parles cash, tu es 
cynique mais juste. Tu donnes des conseils actionnables.
```

### CTA Dynamique

| Tendance | Message |
|----------|---------|
| **HAUSSE** ↑ | "⚠️ Les taux montent. Calcule ta capacité MAINTENANT avant de perdre 10k€" |
| **BAISSE** ↓ | "📉 Les taux baissent. C'est le moment de renégocier ton prêt" |
| **STABLE** → | "⏳ Taux stables... pour l'instant. Prépare ton dossier" |

### Maillage Interne Auto
```python
INTERNAL_LINKS = {
    "calculer": "/calculateur",
    "PTZ": "/ptz-pret-taux-zero",
    "Paris": "/taux-immobilier-paris",
    # ...
}
```

---

## 📤 Étape 4 : Publication

### Commit Automatique
```bash
git add .
git commit -m "🌅 Flash Matin - 2024-11-30"
git push
```

### Déclenchement Netlify
- Webhook sur push → rebuild automatique
- Build : `npm run build`
- Deploy : `/out/` folder
- CDN : distribution mondiale

---

## 🛠️ Commandes Manuelles

### Lancer le scraper localement
```bash
cd scripts
pip install -r requirements.txt
python scraper.py --mode morning
```

### Générer un article localement
```bash
export GEMINI_API_KEY="AIza..."
python rewriter.py --mode morning
```

### Build le site localement
```bash
npm run build
npm run start
```

### Déclencher le workflow manuellement
1. GitHub → Actions → "🌅 Flash Matin"
2. Cliquer "Run workflow"
3. Sélectionner branche `main`
4. Cliquer "Run workflow"

---

## 🐛 Troubleshooting

| Problème | Solution |
|----------|----------|
| Workflow échoue | Vérifier `GEMINI_API_KEY` dans Secrets |
| Pas de commit | Normal si aucun changement détecté |
| Graphique manquant | Vérifier `public/images/charts/` existe |
| Build Netlify fail | Vérifier `out/` dans publish directory |

---

*Dernière mise à jour: 30/11/2024*

