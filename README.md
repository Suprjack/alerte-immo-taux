# 🔔 L'Alerte Immo & Taux

> **Le Financial Insider** - Média automatisé sur l'immobilier et les taux de crédit en France

[![Netlify Status](https://api.netlify.com/api/v1/badges/YOUR-BADGE/deploy-status)](https://app.netlify.com/)
[![GitHub Actions](https://github.com/Suprjack/alerte-immo-taux/actions/workflows/morning-flash.yml/badge.svg)](https://github.com/Suprjack/alerte-immo-taux/actions)

---

## 🎯 C'est quoi ?

Un site d'actualités **100% automatisé** qui :
- 📊 Scrape les taux (OAT, Euribor) et news immobilier **2x/jour**
- 🤖 Génère des articles via **Gemini 2.5 Flash** avec le persona "L'Insider"
- 📈 Crée des graphiques automatiquement
- 🎯 Adapte les CTA selon la tendance du marché (hausse/baisse)
- 🔗 Ajoute du maillage interne automatique pour le SEO

**Coût de fonctionnement : 0€** 💰

---

## 🚀 Quick Start

### 1. Cloner le repo
```bash
git clone https://github.com/Suprjack/alerte-immo-taux.git
cd alerte-immo-taux
```

### 2. Installer les dépendances
```bash
# Frontend
npm install

# Backend (Python)
pip install -r scripts/requirements.txt
```

### 3. Configurer les secrets
Ajouter dans GitHub → Settings → Secrets :
```
GEMINI_API_KEY = "AIza..."
```

### 4. Lancer en local
```bash
npm run dev
```

---

## 📁 Structure

```
├── 📂 .github/workflows/    # Automatisation (08h + 19h)
├── 📂 scripts/              # Python (scraper, rewriter, charts)
├── 📂 src/app/              # Next.js 14 frontend
├── 📂 content/              # Articles Markdown générés
├── 📂 data/                 # JSON (rates, news, trends)
├── 📂 docs/                 # Documentation projet
└── 📂 public/               # Assets statiques
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [📋 VISION](docs/VISION.md) | Objectifs business et KPIs |
| [🗺️ ROADMAP](docs/ROADMAP.md) | Plan de développement |
| [🏗️ ARCHITECTURE](docs/ARCHITECTURE.md) | Architecture technique |
| [⚙️ WORKFLOW](docs/WORKFLOW.md) | Comment ça marche |

---

## ⚡ Stack Technique

| Composant | Technologie |
|-----------|-------------|
| Frontend | Next.js 14 + Tailwind CSS |
| AI | Google Gemini 2.5 Flash |
| Scraping | Python + feedparser + pytrends |
| Charts | matplotlib |
| CI/CD | GitHub Actions |
| Hosting | Netlify (gratuit) |

---

## 🔄 Workflow Automatique

```
08h00 Paris → Flash Matin
19h00 Paris → Récap Soir

Scraper → Gemini → Commit → Netlify Deploy
```

---

## 📊 Statut

- ✅ Phase 1 : Infrastructure & Automatisation
- 🔄 Phase 2 : SEO & Contenu (en cours)
- ⬜ Phase 3 : Lead Generation
- ⬜ Phase 4 : Monétisation

---

## 📝 License

MIT

---

**Made with 🔥 by [Suprjack](https://github.com/Suprjack)**

