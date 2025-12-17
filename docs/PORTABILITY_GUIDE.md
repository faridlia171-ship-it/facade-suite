# Guide de Portabilité – Facade Suite

## 🎯 Objectif

Ce projet est **100% portable** et peut être déployé **indépendamment de toute infrastructure Blink**. Il utilise exclusivement des ressources externes GitHub et Supabase.

---

## 📦 Ressources Externes Uniques

### Repository GitHub
```
https://github.com/faridlia171-ship-it/facade-suite.git
```

**Branches**:
- `main` : Production
- `staging` : Pre-production (optionnel)
- `dev` : Développement (optionnel)

### Projet Supabase
```
URL: https://yrsiurdgigqjgycqujmd.supabase.co
Project ID: yrsiurdgigqjgycqujmd
Region: EU West (Ireland)
```

**Clés API** (depuis Dashboard > Settings > API):
- **Anon Key** (publique) : `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlyc2l1cmRnaWdxamd5Y3F1am1kIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU5MDM1MzUsImV4cCI6MjA4MTQ3OTUzNX0.Q_ZxAcr58N7rChrU58O7gp1H4uD2ymgeBITRY86Ot1o`
- **Service Role Key** (privée) : `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlyc2l1cmRnaWdxamd5Y3F1am1kIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NTkwMzUzNSwiZXhwIjoyMDgxNDc5NTM1fQ.k3d7xrcyZlpuGsrrzA9dzWlYXZVOESPRGv_ZE2SUdsk`
- **JWT Secret** : Voir Dashboard > Settings > API

**Database URL**:
```
postgresql://postgres:[YOUR_DB_PASSWORD]@db.yrsiurdgigqjgycqujmd.supabase.co:5432/postgres
```

---

## 🔐 Aucune Dépendance Interne Blink

### ✅ Ce qui est utilisé (externe)
- **GitHub** : Repository privé `faridlia171-ship-it/facade-suite`
- **Supabase** : Projet `yrsiurdgigqjgycqujmd` (PostgreSQL + Auth + Storage)
- **Render** : Hosting backend (FastAPI) + frontend (React static)

### ❌ Ce qui n'est PAS utilisé (interne Blink)
- ❌ Blink SDK Auth
- ❌ Blink SDK Database
- ❌ Blink SDK Storage
- ❌ Blink Edge Functions
- ❌ Blink secrets vault
- ❌ Blink GitHub organization

---

## 📂 Structure du Repository

```
facade-suite/
├── backend/              # FastAPI Python 3.11
│   ├── app/
│   ├── alembic/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/             # React + Vite + TypeScript
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── .env.example
│
├── docs/                 # Documentation complète
│   ├── ARCHITECTURE.md
│   ├── DB_SCHEMA.md
│   ├── API.md
│   ├── SECURITY.md
│   ├── DEPLOY_RENDER.md
│   └── PORTABILITY_GUIDE.md (ce fichier)
│
├── render.yaml           # Configuration Render
├── README.md
└── RAPPORT.md
```

---

## 🚀 Déploiement sur Render (Sans Blink)

### Prérequis

1. Compte GitHub avec accès au repository : `faridlia171-ship-it/facade-suite`
2. Compte Render : https://render.com (gratuit ou payant)
3. Accès au projet Supabase : `yrsiurdgigqjgycqujmd`

### Étape 1 : Cloner le Repository

```bash
git clone https://github.com/faridlia171-ship-it/facade-suite.git
cd facade-suite
```

### Étape 2 : Configuration Backend sur Render

#### A. Créer le Web Service

1. Dashboard Render → **New +** → **Web Service**
2. **Connect Repository**: Sélectionner `faridlia171-ship-it/facade-suite`
3. Configuration :
   - **Name** : `facade-suite-api`
   - **Region** : Frankfurt (ou autre proche)
   - **Branch** : `main`
   - **Root Directory** : `backend`
   - **Runtime** : Python 3.11
   - **Build Command** : 
     ```bash
     pip install -r requirements.txt && alembic upgrade head
     ```
   - **Start Command** : 
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```

#### B. Variables d'Environnement Backend

Ajouter dans **Environment** :

```bash
# Supabase
SUPABASE_URL=https://yrsiurdgigqjgycqujmd.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlyc2l1cmRnaWdxamd5Y3F1am1kIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU5MDM1MzUsImV4cCI6MjA4MTQ3OTUzNX0.Q_ZxAcr58N7rChrU58O7gp1H4uD2ymgeBITRY86Ot1o
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlyc2l1cmRnaWdxamd5Y3F1am1kIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NTkwMzUzNSwiZXhwIjoyMDgxNDc5NTM1fQ.k3d7xrcyZlpuGsrrzA9dzWlYXZVOESPRGv_ZE2SUdsk
SUPABASE_JWT_SECRET=[VOIR DASHBOARD SUPABASE > SETTINGS > API]

# Database
DATABASE_URL=postgresql://postgres:[YOUR_DB_PASSWORD]@db.yrsiurdgigqjgycqujmd.supabase.co:5432/postgres

# Security
SECRET_KEY=[GÉNÉRER: openssl rand -hex 32]
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (à ajuster après déploiement frontend)
CORS_ORIGINS=["https://facade-suite.onrender.com","http://localhost:5173"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Storage
STORAGE_BUCKET=facade-suite-private

# PDF
PDF_WATERMARK_TEXT=TRIAL - Facade Suite

# Debug
DEBUG=False
```

#### C. Déployer

Cliquer **Create Web Service** → Attendre déploiement (5-10 min)

URL backend : `https://facade-suite-api.onrender.com`

### Étape 3 : Configuration Frontend sur Render

#### A. Créer le Static Site

1. Dashboard Render → **New +** → **Static Site**
2. **Connect Repository**: Sélectionner `faridlia171-ship-it/facade-suite`
3. Configuration :
   - **Name** : `facade-suite`
   - **Branch** : `main`
   - **Root Directory** : `/` (ou `frontend` si séparé)
   - **Build Command** : 
     ```bash
     npm install && npm run build
     ```
   - **Publish Directory** : `dist`

#### B. Variables d'Environnement Frontend

Ajouter dans **Environment** :

```bash
# Supabase (PUBLIC - OK)
VITE_SUPABASE_URL=https://yrsiurdgigqjgycqujmd.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlyc2l1cmRnaWdxamd5Y3F1am1kIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU5MDM1MzUsImV4cCI6MjA4MTQ3OTUzNX0.Q_ZxAcr58N7rChrU58O7gp1H4uD2ymgeBITRY86Ot1o

# API Backend
VITE_API_BASE_URL=https://facade-suite-api.onrender.com
```

#### C. Déployer

Cliquer **Create Static Site** → Attendre déploiement (3-5 min)

URL frontend : `https://facade-suite.onrender.com`

### Étape 4 : Finalisation

#### Mettre à jour CORS Backend

Retourner dans Backend Environment Variables :
```bash
CORS_ORIGINS=["https://facade-suite.onrender.com"]
```

Redéployer manuellement le backend.

#### Tester l'application

1. Ouvrir `https://facade-suite.onrender.com`
2. Créer un compte utilisateur
3. Tester création client/chantier
4. Vérifier logs Render pour erreurs

---

## 🔧 Développement Local (Sans Blink)

### Backend

```bash
cd backend

# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer dépendances
pip install -r requirements.txt

# Copier et configurer .env
cp .env.example .env
# Éditer .env avec les bonnes valeurs Supabase

# Migrations
alembic upgrade head

# Lancer serveur
uvicorn app.main:app --reload
```

Backend accessible : `http://localhost:8000`

### Frontend

```bash
cd frontend  # ou root si pas de sous-dossier

# Installer dépendances
npm install

# Copier et configurer .env
cp .env.example .env
# Éditer .env

# Lancer dev server
npm run dev
```

Frontend accessible : `http://localhost:5173`

---

## 🔄 CI/CD Automatique

### Déploiement Automatique

Render redéploie automatiquement à chaque push sur `main` :

```bash
git add .
git commit -m "Update feature X"
git push origin main
```

→ Render détecte le push et redéploie backend + frontend automatiquement

### Branches de Staging (Optionnel)

1. Créer branche `staging` :
   ```bash
   git checkout -b staging
   git push origin staging
   ```

2. Dupliquer les services Render :
   - `facade-suite-api-staging` (branche: `staging`)
   - `facade-suite-staging` (branche: `staging`)

3. Tester en staging avant merge dans `main`

---

## 📊 Monitoring Indépendant

### Logs Render

- Backend : Dashboard → Logs (temps réel)
- Frontend : Browser Console (erreurs JS)

### Uptime Monitoring

**UptimeRobot** (gratuit, externe) :
1. S'inscrire : https://uptimerobot.com
2. Ajouter monitor HTTP :
   - URL : `https://facade-suite-api.onrender.com/health`
   - Interval : 5 minutes
   - Alert : Email si down

### Error Tracking

**Sentry** (optionnel, externe) :
1. Créer projet : https://sentry.io
2. Installer SDK :
   ```bash
   # Backend
   pip install sentry-sdk[fastapi]
   
   # Frontend
   npm install @sentry/react
   ```
3. Configurer DSN en variable d'environnement

---

## 🔒 Sécurité

### Secrets Management

**Tous les secrets sont dans Render Environment Variables** :
- ✅ Secrets backend : Jamais exposés au client
- ✅ Secrets frontend : Uniquement clés publiques (VITE_SUPABASE_ANON_KEY)
- ❌ Aucun secret hardcodé dans le code
- ❌ Aucune dépendance sur Blink vault

### Rotation des Secrets

1. Générer nouveau secret Supabase
2. Mettre à jour dans Render Environment
3. Redéployer
4. Révoquer ancien secret

### Backup

**Supabase** : Backup automatique quotidien (plan gratuit)

**Code** : GitHub repository (historique complet)

---

## ✅ Checklist de Portabilité

- [x] Repository GitHub externe : `faridlia171-ship-it/facade-suite`
- [x] Projet Supabase externe : `yrsiurdgigqjgycqujmd`
- [x] Aucune référence interne Blink
- [x] Variables d'environnement documentées
- [x] Déploiement Render sans dépendance Blink
- [x] CI/CD automatique via GitHub + Render
- [x] Documentation complète (README, DEPLOY_RENDER, PORTABILITY_GUIDE)
- [x] Code 100% portable et réutilisable

---

## 📞 Support

Pour toute question sur la portabilité :

- **Email** : gsmfarid@hotmail.fr
- **Repository Issues** : https://github.com/faridlia171-ship-it/facade-suite/issues
- **Documentation** : `docs/` folder

---

**Fait avec ❤️ pour être 100% portable et indépendant**
