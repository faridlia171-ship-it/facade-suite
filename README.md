# Facade Suite

**Gestion professionnelle de chantiers de façade – SaaS B2B**

Version: 1.0.0  
Développé par: El Bennouni Farid pour SARL Plein Sud Crépis

---

## 📋 Description

Facade Suite est une application SaaS B2B complète pour la gestion professionnelle de chantiers de façade, incluant:

- ✅ **Multi-tenant** strict par entreprise
- ✅ **Authentification JWT** Supabase sécurisée
- ✅ **Métrage photo** avec correction perspective
- ✅ **Devis temps réel** avec versioning (V1/V2/V3...)
- ✅ **Génération PDF serveur** avec anti-triche
- ✅ **PWA ready** pour utilisation mobile chantier
- ✅ **Row-Level Security** sur 100% des données
- ✅ **Audit logs** complets
- ✅ **Plans d'abonnement** (TRIAL, PRO, ENTREPRISE)

---

## 🏗️ Architecture

### Monorepo Structure

```
/
├── backend/           # FastAPI (Python 3.11)
│   ├── app/
│   ├── alembic/       # Migrations DB
│   └── requirements.txt
│
├── frontend/          # React + Vite + TypeScript
│   ├── src/
│   ├── public/
│   └── package.json
│
├── docs/              # Documentation complète
│   ├── ARCHITECTURE.md
│   ├── DB_SCHEMA.md
│   ├── API.md
│   ├── SECURITY.md
│   └── DEPLOY_RENDER.md
│
├── render.yaml        # Config déploiement Render
├── README.md
└── RAPPORT.md         # Compte-rendu livraison
```

### Stack Technique

**Backend**:
- FastAPI
- SQLAlchemy + Alembic
- PostgreSQL (Supabase)
- JWT Supabase
- ReportLab (PDF)

**Frontend**:
- React 18 + TypeScript
- Vite
- Tailwind CSS + shadcn/ui
- React Query
- PWA ready

**Infrastructure**:
- Supabase (DB + Auth + Storage)
- Render (Backend + Frontend hosting)
- GitHub (Repository privé)

---

## 🚀 Démarrage Rapide

### Prérequis

- **Python 3.11+**
- **Node.js 18+**
- **Compte Supabase** (gratuit)
- **Compte Render** (gratuit)

### Installation Locale

#### 1. Cloner le repo
```bash
git clone https://github.com/faridlia171-ship-it/facade-suite.git
cd facade-suite
```

#### 2. Configuration Backend

```bash
cd backend

# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer dépendances
pip install -r requirements.txt

# Configurer .env
cp .env.example .env
# Éditer .env avec vos secrets Supabase

# Migrations
alembic upgrade head

# Lancer serveur
uvicorn app.main:app --reload
```

Backend accessible sur: `http://localhost:8000`

#### 3. Configuration Frontend

```bash
cd frontend

# Installer dépendances
npm install

# Configurer .env
cp .env.example .env
# Éditer .env avec URL Supabase et API backend

# Lancer dev server
npm run dev
```

Frontend accessible sur: `http://localhost:5173`

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Architecture technique détaillée |
| [DB_SCHEMA.md](docs/DB_SCHEMA.md) | Schéma de base de données + RLS |
| [API.md](docs/API.md) | Documentation API complète |
| [SECURITY.md](docs/SECURITY.md) | Stratégie de sécurité |
| [DEPLOY_RENDER.md](docs/DEPLOY_RENDER.md) | Guide de déploiement Render |
| [RAPPORT.md](RAPPORT.md) | Compte-rendu de livraison |

---

## 🔐 Sécurité

### Multi-tenant Isolation
- **company_id** sur toutes les tables
- **Row-Level Security (RLS)** PostgreSQL
- Vérification systématique backend

### Authentification
- JWT Supabase vérifié côté backend
- Pas de secrets côté client
- Rate limiting (60 req/min)

### Storage
- Buckets privés Supabase
- Signed URLs avec expiration
- Organisation par `company_id/project_id`

### PDF Anti-triche
- Génération serveur uniquement
- Hash unique SHA256
- Page publique de vérification

---

## 🎯 Fonctionnalités Principales

### 1. Gestion Clients
- CRUD complet
- Coordonnées + ville
- Historique chantiers

### 2. Gestion Chantiers
- Création avec client associé
- Statuts (draft, in_progress, completed)
- Devis auto-créé

### 3. Métrage Photo
- Upload photos façades
- Référence agglo 20×50 ou custom
- Correction perspective simple
- Calcul surfaces automatique
- Déduction ouvertures

### 4. Devis Temps Réel
- Versioning V1/V2/V3
- Lignes prestations
- Ajout vocal/texte
- Négociation client
- Génération PDF serveur

### 5. Plans d'Abonnement
| Plan | Projets | Utilisateurs | Prix |
|------|---------|--------------|------|
| **TRIAL** | 1 | 1 | Gratuit 14j |
| **PRO** | Illimité | 1 | 29€/mois |
| **ENTREPRISE** | Illimité | 5 | 79€/mois |

---

## 🌍 Déploiement Production

### Render (Recommandé)

1. **Supabase**: Créer projet + exécuter SQL schema
2. **Render Backend**: Web Service Python
3. **Render Frontend**: Static Site
4. **Variables d'env**: Configurer secrets
5. **Custom Domain**: Optionnel

Voir [DEPLOY_RENDER.md](docs/DEPLOY_RENDER.md) pour guide complet.

### Infrastructure

- **Repository GitHub**: https://github.com/faridlia171-ship-it/facade-suite.git
- **Supabase Project**: https://yrsiurdgigqjgycqujmd.supabase.co
- **Déploiement**: Render (backend + frontend)

### Coûts Estimés
- **Gratuit**: Backend Starter + Supabase Free = 0€/mois (avec limitations)
- **Production**: Backend Standard + Supabase Pro = ~32€/mois
- **Scaling**: Backend Pro + Monitoring = ~76€/mois

---

## 🧪 Tests

### Backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend
npm run test
```

*(À implémenter)*

---

## 🤝 Contribution

Ce projet est propriétaire et développé pour SARL Plein Sud Crépis.

### Contact
- **Email**: gsmfarid@hotmail.fr
- **Entreprise**: SARL Plein Sud Crépis
- **RCS**: 50113927300020

---

## 📄 Licence

© 2024 SARL Plein Sud Crépis - Tous droits réservés

Développé par El Bennouni Farid

---

## 🆘 Support

Pour toute question ou problème:
1. Consulter la [documentation](docs/)
2. Vérifier les [logs Render](https://dashboard.render.com)
3. Contacter: **gsmfarid@hotmail.fr**

---

## 🔄 Roadmap

### Phase 1 (MVP) ✅
- Auth + multi-tenant
- CRUD clients/chantiers
- Structure backend/frontend

### Phase 2 (En cours) 🚧
- Métrage photo complet
- Correction perspective avancée
- Qualité photo (vert/orange/rouge)

### Phase 3
- Devis temps réel
- Versioning
- Vocal input

### Phase 4
- PDF serveur
- Anti-triche
- Page vérification publique

### Phase 5
- Mode offline PWA
- Sync auto
- Notifications

### Phase 6
- Analytics
- Monitoring Sentry
- Tests E2E

---

## 📊 État du Projet

- **Version**: 1.0.0
- **Statut**: MVP Livré (Livraison progressive)
- **Dernière mise à jour**: Décembre 2024
- **Environnement**: Développement local + Déploiement Render ready

---

**Fait avec ❤️ pour les professionnels de la façade**
