# 🏠 Alerte Immo & Taux - Status Projet

> Dernière mise à jour : 30 Novembre 2024

## 📋 Résumé du Projet

**Objectif** : Site de génération de leads pour crédit immobilier, rachat de crédit, crédit auto, etc.
**Stratégie** : pSEO Local "Rank & Rent" - 1446 pages locales (241 villes × 6 types de crédit)
**Monétisation** : Revente de leads aux courtiers locaux (300-500€/mois par ville)

---

## ✅ Ce qui est FAIT

### 1. Pages pSEO (1446 pages)
- **241 villes françaises** générées
- **6 types de crédit** : courtier-immobilier, rachat-credit, credit-auto, pret-travaux, credit-professionnel, assurance-pret
- **Routes** : `/[creditType]/[city]` (ex: `/courtier-immobilier/paris`)
- **Sitemap** : `public/sitemap-pseo.xml`

### 2. Formulaire de Leads
- **Champs** : Montant, Prénom, Nom, Email, Téléphone
- **Envoi vers** : Supabase (BDD) + Formspree (email backup)
- **Tracking** : UTM params capturés, localStorage backup

### 3. Supabase - Base de données
- **Projet** : `alerte-immo-taux`
- **ID** : `rhsrzffbeiqpciqanjvi`
- **Region** : eu-west-3
- **URL** : `https://rhsrzffbeiqpciqanjvi.supabase.co`
- **Table** : `leads` avec RLS activé (insertion publique)
- **Mot de passe DB** : `AlerteImmo2024Secure!`

### 4. Dashboard Admin
- **URL** : `/admin`
- **Mot de passe** : `admin2024`
- **Fonctionnalités** : Stats, liste leads, changement de status

### 5. Scraper V3 (scripts/)
- **Google Trends** : Détection des breakouts
- **News** : Google News multi-thèmes, Service-Public, ANIL
- **Forums** : MoneyVox, ForumConstruire (questions réelles)
- **Prix par ville** : MeilleursAgents
- **Enchères** : Licitor

### 6. Rewriter V3
- **Persona** : "L'Insider" (style cynique/rebelle)
- **CTA dynamiques** : Selon tendance hausse/baisse
- **Maillage interne** : Liens automatiques vers /calculateur, /ptz, etc.

### 7. GitHub Actions
- `morning-flash.yml` : Flash marché 7h
- `evening-recap.yml` : Récap soir 19h

---

## ⚠️ À CONFIGURER (Netlify Environment Variables)

| Variable | Valeur | Status |
|----------|--------|--------|
| `NEXT_PUBLIC_FORMSPREE_ID` | `xpwzgvpd` (ou ton ID) | ✅ Fait |
| `NEXT_PUBLIC_GA_ID` | `G-XXXXXXXXXX` | ❌ À faire |
| `OPENAI_API_KEY` | Ta clé OpenAI | ❌ À vérifier |

---

## ❌ À FAIRE - Prochaines étapes

### Priorité 1 - Domaine
Acheter un domaine .fr parmi ces recommandations :

| Domaine | Pourquoi |
|---------|----------|
| **alertetaux.fr** | ⭐ Court, keyword "taux", urgence |
| **moncourtier.fr** | ⭐ Confiance, perso, keyword exact |
| **creditmalin.fr** | ⭐ Brandable, positif |
| tauxalert.fr | Keyword first, SEO |
| comparataux.fr | Action + keyword |
| lecreditfacile.fr | Rassure, promesse |
| courtier-local.fr | Angle pSEO local |
| meilleur-taux-credit.fr | Longue traîne |
| financement-immo.fr | Pro, B2B |
| insider-credit.fr | Match persona |

**Où acheter** : OVH ou Gandi (~7€/an pour .fr)

### Priorité 2 - Google Analytics
1. Aller sur https://analytics.google.com/
2. Créer propriété GA4 avec URL du site
3. Récupérer ID `G-XXXXXXXX`
4. Ajouter dans Netlify : `NEXT_PUBLIC_GA_ID`
5. Redeploy

### Priorité 3 - SEO & Indexation
1. Soumettre sitemap à Google Search Console
2. Soumettre sitemap à Bing Webmaster Tools
3. Créer profil Google Business (si possible)

### Priorité 4 - Monétisation
1. Contacter courtiers locaux pour Rank & Rent
2. Configurer liens affiliation (Pretto, Solutis, Younited)
3. Tracker revenus par lead dans Supabase

---

## 🔗 URLs importantes

| Ressource | URL |
|-----------|-----|
| **Site (Netlify)** | https://alerte-immo-taux.netlify.app |
| **Dashboard Admin** | https://alerte-immo-taux.netlify.app/admin |
| **GitHub Repo** | https://github.com/Suprjack/alerte-immo-taux |
| **Supabase Dashboard** | https://supabase.com/dashboard/project/rhsrzffbeiqpciqanjvi |
| **Netlify Dashboard** | https://app.netlify.com/sites/alerte-immo-taux |

---

## 📁 Structure des fichiers clés

```
alerte_immo_taux/
├── src/
│   ├── app/
│   │   ├── [creditType]/[city]/page.js  # Pages pSEO
│   │   ├── admin/page.js                 # Dashboard admin
│   │   ├── layout.js                     # Layout + GA
│   │   └── calculateur/page.js           # Calculateur
│   └── components/
│       └── LeadForm.js                   # Formulaire leads
├── scripts/
│   ├── scraper.py                        # Scraper V3
│   ├── rewriter.py                       # Rewriter V3
│   ├── chart_generator.py                # Graphiques
│   └── pseo_generator.py                 # Génération pages
├── data/
│   ├── cities.json                       # 241 villes
│   └── credit_types.json                 # 6 types crédit
├── content/pseo/                         # Pages MD générées
└── public/
    └── sitemap-pseo.xml                  # Sitemap 1446 URLs
```

---

## 🔑 Credentials (À SÉCURISER)

### Supabase
- **Anon Key** : `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJoc3J6ZmZiZWlxcGNpcWFuanZpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ0MTU4NzYsImV4cCI6MjA3OTk5MTg3Nn0.-yZ8puHc-9wznPfd_3TxbF6fjitgcPX9hhnkzTkV2dA`
- **Service Role** : `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJoc3J6ZmZiZWlxcGNpcWFuanZpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDQxNTg3NiwiZXhwIjoyMDc5OTkxODc2fQ.sFoI0AmSahc_Yyt2LPHXmhrYDq_0D6Wkam_U68INI9Q`

---

## 📊 Métriques à suivre

| Métrique | Objectif | Outil |
|----------|----------|-------|
| Pages indexées | 1446 | Google Search Console |
| Leads/mois | 50+ | Supabase Dashboard |
| Taux conversion | 2-5% | Google Analytics |
| Revenu/lead | 10-30€ | Supabase (champ revenue) |
| Coût/lead | 0€ (SEO organique) | - |

---

## 🚨 Points d'attention

1. **YMYL** : Google est strict sur les sites finance. Ajouter pages "À propos", "Mentions légales", "CGU"
2. **Backlinks** : Faire du guest posting sur blogs immo/finance
3. **Contenu frais** : Les GitHub Actions publient 2x/jour, vérifier que ça marche
4. **Mobile** : Tester responsive sur toutes les pages

---

## 📞 Support

- **Repo GitHub** : https://github.com/Suprjack/alerte-immo-taux
- **Issues** : Créer une issue sur GitHub pour tout problème

---

## 💡 Idées futures

- [ ] Authentification Supabase pour admin (remplacer mot de passe simple)
- [ ] Notifications email quand nouveau lead
- [ ] API webhook pour envoyer leads vers CRM
- [ ] A/B testing sur les CTA
- [ ] Chatbot IA pour qualifier les leads
- [ ] Pages comparatif banques par ville

