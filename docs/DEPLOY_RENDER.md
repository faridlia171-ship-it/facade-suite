# Déploiement sur Render

## Prérequis

1. **Compte Render**: [https://render.com](https://render.com)
2. **Compte Supabase**: [https://supabase.com](https://supabase.com)
3. **Repository GitHub**: Code pushé sur GitHub

## Architecture Déploiement

```
GitHub Repo (monorepo)
    ↓
Render Dashboard
    ├── Web Service (Backend FastAPI)
    ├── Static Site (Frontend React)
    └── PostgreSQL (ou externe Supabase)
```

## Étape 1: Configuration Supabase

### 1.1 Créer le projet Supabase

1. Aller sur [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Cliquer "New Project"
3. Nom: `facade-suite-prod`
4. Region: EU West (Paris) recommandé
5. Mot de passe DB: **Noter précieusement**

### 1.2 Exécuter le schéma SQL

Dans SQL Editor Supabase:

```sql
-- Copier/coller tout le contenu de docs/DB_SCHEMA.md
-- Section "Tables Détaillées"
```

### 1.3 Configurer Auth

Settings → Auth:
- Email confirmations: **Disabled** (ou configuré avec SMTP)
- Email templates: Personnaliser si besoin

### 1.4 Créer le bucket Storage

Storage → New Bucket:
- Nom: `facade-suite-private`
- Public: **Non**
- RLS: **Activé**

Appliquer les policies RLS (voir DB_SCHEMA.md).

### 1.5 Noter les secrets

Settings → API:
- `SUPABASE_URL`: https://xxxxx.supabase.co
- `SUPABASE_ANON_KEY`: eyJhbGc...
- `SUPABASE_SERVICE_KEY`: eyJhbGc... (SECRET)

Settings → Auth → JWT Secret:
- `SUPABASE_JWT_SECRET`: your-jwt-secret

Settings → Database:
- `DATABASE_URL`: postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres

## Étape 2: Déploiement Backend (FastAPI)

### 2.1 Créer le Web Service

1. Dashboard Render → "New +" → "Web Service"
2. Connect GitHub repository
3. Configuration:
   - **Name**: `facade-suite-api`
   - **Region**: Frankfurt (proche Paris)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt && alembic upgrade head`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Starter (gratuit) ou Standard

### 2.2 Variables d'environnement

Ajouter dans Environment:

```bash
# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_KEY=eyJhbGc...
SUPABASE_JWT_SECRET=your-jwt-secret

# Database
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres

# Security
SECRET_KEY=[GÉNÉRER AVEC: openssl rand -hex 32]
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (mettre l'URL frontend Render)
CORS_ORIGINS=["https://facade-suite.onrender.com"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Storage
STORAGE_BUCKET=facade-suite-private

# PDF
PDF_WATERMARK_TEXT=TRIAL - Facade Suite

# Debug
DEBUG=False
```

### 2.3 Déployer

1. Cliquer "Create Web Service"
2. Attendre le déploiement (5-10 min)
3. URL: `https://facade-suite-api.onrender.com`
4. Tester: `https://facade-suite-api.onrender.com/health`

### 2.4 Configuration Alembic

Si erreur migrations:
1. Shell Render → `alembic upgrade head`
2. Vérifier DATABASE_URL correct

## Étape 3: Déploiement Frontend (React)

### 3.1 Créer le Static Site

1. Dashboard Render → "New +" → "Static Site"
2. Connect GitHub repository
3. Configuration:
   - **Name**: `facade-suite`
   - **Branch**: `main`
   - **Root Directory**: `frontend` (ou `/` si déjà dans frontend)
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

### 3.2 Variables d'environnement

Ajouter dans Environment:

```bash
# Supabase (PUBLIC - OK)
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGc...

# API Backend (URL Render backend)
VITE_API_BASE_URL=https://facade-suite-api.onrender.com
```

### 3.3 Déployer

1. Cliquer "Create Static Site"
2. Attendre le déploiement (3-5 min)
3. URL: `https://facade-suite.onrender.com`
4. Tester l'app

### 3.4 Mise à jour CORS Backend

Retourner dans Backend Environment Variables:
```bash
CORS_ORIGINS=["https://facade-suite.onrender.com"]
```

Redéployer le backend (manual deploy).

## Étape 4: Configuration render.yaml (Optionnel)

Créer `render.yaml` à la racine du monorepo pour déploiement automatisé:

```yaml
services:
  # Backend API
  - type: web
    name: facade-suite-api
    runtime: python
    region: frankfurt
    plan: starter
    buildCommand: "cd backend && pip install -r requirements.txt && alembic upgrade head"
    startCommand: "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_ANON_KEY
        sync: false
      - key: SUPABASE_SERVICE_KEY
        sync: false
      - key: SUPABASE_JWT_SECRET
        sync: false
      - key: DATABASE_URL
        sync: false
      - key: SECRET_KEY
        generateValue: true
      - key: ALGORITHM
        value: HS256
      - key: CORS_ORIGINS
        value: '["https://facade-suite.onrender.com"]'
      - key: RATE_LIMIT_PER_MINUTE
        value: "60"
      - key: STORAGE_BUCKET
        value: facade-suite-private
      - key: DEBUG
        value: "False"
  
  # Frontend Static Site
  - type: web
    name: facade-suite
    runtime: static
    region: frankfurt
    plan: starter
    buildCommand: "cd frontend && npm install && npm run build"
    staticPublishPath: frontend/dist
    envVars:
      - key: VITE_SUPABASE_URL
        sync: false
      - key: VITE_SUPABASE_ANON_KEY
        sync: false
      - key: VITE_API_BASE_URL
        value: https://facade-suite-api.onrender.com
```

**Note**: `sync: false` = Variables à remplir manuellement dans Dashboard.

## Étape 5: Custom Domain (Optionnel)

### Backend
1. Settings → Custom Domain
2. Ajouter: `api.facade-suite.com`
3. DNS:
   - Type: `CNAME`
   - Name: `api`
   - Value: `facade-suite-api.onrender.com`

### Frontend
1. Settings → Custom Domain
2. Ajouter: `facade-suite.com` et `www.facade-suite.com`
3. DNS:
   - Type: `A`
   - Name: `@`
   - Value: IP fournie par Render
   - Type: `CNAME`
   - Name: `www`
   - Value: `facade-suite.onrender.com`

## Étape 6: Monitoring

### Logs Backend
Dashboard → Logs → Voir en temps réel

### Logs Frontend
Browser console (erreurs JS)

### Uptime
Activer Render Uptime Monitoring (payant) ou UptimeRobot (gratuit).

### Sentry (Recommandé)
1. Créer projet Sentry
2. Ajouter SDK backend + frontend
3. Configurer DSN en variable d'environnement

## Étape 7: CI/CD Auto

Render déploie automatiquement à chaque push sur `main`.

Pour staging:
1. Créer branche `staging`
2. Dupliquer services Render pointant sur `staging`
3. Tester avant merge dans `main`

## Étape 8: Backup & Rollback

### Backup Supabase
Automatique quotidien. Point-in-time recovery (plan payant).

### Rollback Render
Dashboard → Deployments → Rollback to previous

## Étape 9: Scale

### Backend
Settings → Instance Type:
- **Starter**: Gratuit (limité)
- **Standard**: $7/mois (2 CPU, 2 GB RAM)
- **Pro**: $25/mois (4 CPU, 4 GB RAM)

Auto-scaling: Disponible sur plans Pro+.

### Frontend
Scaling automatique (CDN).

## Étape 10: Maintenance

### Mises à jour
1. Push code sur GitHub
2. Render auto-déploie
3. Vérifier logs

### Migrations DB
```bash
# Local
alembic revision -m "Add field"
alembic upgrade head

# Push to GitHub
git push

# Render auto-applique via build command
```

### Secrets Rotation
1. Générer nouveau secret
2. Mettre à jour Render Environment
3. Redéployer
4. Révoquer ancien secret

## Troubleshooting

### Build Failed
- Vérifier `requirements.txt` complet
- Vérifier Python version (3.11)
- Logs → Identifier l'erreur

### Runtime Error
- Vérifier variables d'environnement
- Tester DATABASE_URL
- Vérifier CORS

### 502 Bad Gateway
- Backend down → Vérifier logs
- Timeout → Augmenter instance type

### JWT Invalid
- Vérifier SUPABASE_JWT_SECRET
- Vérifier token côté frontend

## Coûts Estimés

### Plan Gratuit
- Backend: Starter (gratuit, sleep après 15min inactivité)
- Frontend: Gratuit
- Supabase: Gratuit (500 MB DB, 1 GB storage)
- **Total**: 0€/mois

### Plan Production
- Backend: Standard ($7/mois)
- Frontend: Gratuit
- Supabase: Pro ($25/mois, sans sleep)
- **Total**: ~32€/mois

### Plan Scaling
- Backend: Pro ($25/mois)
- Frontend: Gratuit
- Supabase: Pro ($25/mois)
- Monitoring: Sentry ($26/mois)
- **Total**: ~76€/mois

## Support

- **Render Docs**: [https://render.com/docs](https://render.com/docs)
- **Supabase Docs**: [https://supabase.com/docs](https://supabase.com/docs)
- **Support Facade Suite**: gsmfarid@hotmail.fr
