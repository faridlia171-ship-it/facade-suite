# 🚀 INSTRUCTIONS DE DÉPLOIEMENT FACADE SUITE

## ✅ État Actuel

**Backend complet**: ✅ Implémenté  
**Base de données**: ✅ 13 tables avec RLS  
**API FastAPI**: ✅ Endpoints CRUD opérationnels  
**Frontend**: ✅ Interface complète  
**Portabilité**: ✅ 100% externe (Supabase + GitHub)

---

## 📋 ÉTAPE 1 : CONFIGURATION SUPABASE

### 1.1 Créer les tables

**Option A : Via Dashboard Supabase**

1. Aller sur https://yrsiurdgigqjgycqujmd.supabase.co
2. Ouvrir **SQL Editor**
3. Copier le contenu de `supabase/migrations/001_initial_schema.sql`
4. Exécuter le script SQL

**Option B : Via CLI Supabase** (si configuré localement)

```bash
supabase db push
```

### 1.2 Créer le bucket Storage

1. Aller sur **Storage** dans le dashboard
2. Créer un nouveau bucket:
   - **Nom**: `facade-suite-private`
   - **Public**: ❌ Non (privé)
   - **Taille max**: 10MB par fichier
   - **Types autorisés**: image/jpeg, image/png, application/pdf

### 1.3 Récupérer les clés

Dans **Settings → API**:

- ✅ `SUPABASE_URL`: https://yrsiurdgigqjgycqujmd.supabase.co
- ✅ `SUPABASE_ANON_KEY`: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (clé publique)
- ⚠️ `SUPABASE_SERVICE_ROLE_KEY`: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (SECRET!)

Dans **Settings → API → JWT Settings**:

- ⚠️ `SUPABASE_JWT_SECRET`: votre-secret-jwt (SECRET!)

Dans **Settings → Database**:

- ⚠️ `DATABASE_URL`: postgresql://postgres:[PASSWORD]@db.yrsiurdgigqjgycqujmd.supabase.co:5432/postgres

---

## 📋 ÉTAPE 2 : DÉPLOIEMENT BACKEND SUR RENDER

### 2.1 Créer le service backend

1. Aller sur https://render.com
2. Cliquer **New → Web Service**
3. Connecter le repository GitHub: `https://github.com/faridlia171-ship-it/facade-suite.git`
4. Configurer:

| Paramètre | Valeur |
|-----------|--------|
| **Name** | `facade-suite-api` |
| **Region** | Frankfurt |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

### 2.2 Ajouter les variables d'environnement

Dans **Environment → Environment Variables**:

```env
# Supabase
SUPABASE_URL=https://yrsiurdgigqjgycqujmd.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_JWT_SECRET=votre-secret-jwt

# Database
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.yrsiurdgigqjgycqujmd.supabase.co:5432/postgres

# Security
SECRET_KEY=votre-cle-secrete-aleatoire
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (Mettre l'URL frontend Render après déploiement)
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

### 2.3 Déployer

1. Cliquer **Create Web Service**
2. Attendre le build (~3-5 min)
3. Vérifier le health check: https://facade-suite-api.onrender.com/health

**Réponse attendue**:
```json
{"status": "healthy"}
```

---

## 📋 ÉTAPE 3 : DÉPLOIEMENT FRONTEND SUR RENDER

### 3.1 Créer le service frontend

1. Aller sur https://render.com
2. Cliquer **New → Static Site**
3. Connecter le même repository: `https://github.com/faridlia171-ship-it/facade-suite.git`
4. Configurer:

| Paramètre | Valeur |
|-----------|--------|
| **Name** | `facade-suite` |
| **Region** | Frankfurt |
| **Branch** | `main` |
| **Root Directory** | *(vide - racine du projet)* |
| **Build Command** | `npm install && npm run build` |
| **Publish Directory** | `dist` |

### 3.2 Ajouter les variables d'environnement

Dans **Environment → Environment Variables**:

```env
# Supabase (Public - OK pour frontend)
VITE_SUPABASE_URL=https://yrsiurdgigqjgycqujmd.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Backend API (URL Render backend)
VITE_API_BASE_URL=https://facade-suite-api.onrender.com
```

### 3.3 Configurer les redirects (pour React Router)

Dans **Settings → Redirects/Rewrites**:

| Source | Destination | Type |
|--------|-------------|------|
| `/*` | `/index.html` | Rewrite |

**OU** ajouter un fichier `public/_redirects`:
```
/*    /index.html   200
```

### 3.4 Déployer

1. Cliquer **Create Static Site**
2. Attendre le build (~2-3 min)
3. Accéder à l'URL: https://facade-suite.onrender.com

---

## 📋 ÉTAPE 4 : VÉRIFICATION FINALE

### 4.1 Tests Backend

```bash
# Health check
curl https://facade-suite-api.onrender.com/health

# API docs (OpenAPI)
https://facade-suite-api.onrender.com/docs
```

### 4.2 Tests Frontend

1. Ouvrir https://facade-suite.onrender.com
2. Vérifier que la page se charge
3. Tester la navigation (Dashboard, Clients, Chantiers)

### 4.3 Tests d'intégration (après implémentation auth)

1. Créer un compte
2. Se connecter
3. Créer un client
4. Créer un chantier
5. Uploader une photo
6. Créer un devis

---

## 🐛 TROUBLESHOOTING

### Backend ne démarre pas

**Erreur: DATABASE_URL invalide**

Vérifier que `DATABASE_URL` contient le bon mot de passe Supabase.

**Erreur: SUPABASE_JWT_SECRET invalide**

1. Aller sur Supabase Dashboard → Settings → API → JWT Settings
2. Copier exactement la valeur de `JWT Secret`

### Frontend ne se connecte pas au backend

**Erreur CORS**

Mettre à jour `CORS_ORIGINS` dans le backend avec l'URL exacte du frontend Render:

```env
CORS_ORIGINS=["https://facade-suite.onrender.com"]
```

### Photos ne s'uploadent pas

**Vérifier le bucket**:
1. Dashboard Supabase → Storage
2. Bucket `facade-suite-private` existe et est privé
3. Taille max: 10MB

---

## 📊 ENDPOINTS API DISPONIBLES

Une fois déployé, l'API est accessible sur `https://facade-suite-api.onrender.com`

### Documentation OpenAPI

https://facade-suite-api.onrender.com/docs

### Endpoints implémentés

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/companies/me` | GET | Info société |
| `/api/companies/me` | PUT | Modifier société (OWNER) |
| `/api/companies/subscription` | GET | Abonnement |
| `/api/customers/` | GET | Liste clients |
| `/api/customers/` | POST | Créer client |
| `/api/customers/{id}` | GET | Détails client |
| `/api/customers/{id}` | PUT | Modifier client |
| `/api/customers/{id}` | DELETE | Supprimer client |
| `/api/projects/` | GET | Liste chantiers |
| `/api/projects/` | POST | Créer chantier |
| `/api/projects/{id}` | GET | Détails chantier |
| `/api/projects/{id}` | PUT | Modifier chantier |
| `/api/projects/{id}` | DELETE | Supprimer chantier |
| `/api/photos/{facade_id}/upload` | POST | Upload photo |
| `/api/photos/facade/{facade_id}` | GET | Liste photos |
| `/api/photos/{photo_id}` | DELETE | Supprimer photo |
| `/api/quotes/{project_id}` | GET | Devis complet |
| `/api/quotes/{project_id}/version` | POST | Créer version V2/V3 |
| `/api/quotes/{quote_id}/status` | PUT | Changer statut |

---

## 🔐 SÉCURITÉ

### Secrets à JAMAIS exposer

- ❌ `SUPABASE_SERVICE_KEY` - Backend uniquement
- ❌ `SUPABASE_JWT_SECRET` - Backend uniquement  
- ❌ `DATABASE_URL` - Backend uniquement (contient password)
- ❌ `SECRET_KEY` - Backend uniquement

### Clés publiques (OK pour frontend)

- ✅ `SUPABASE_URL` - URL du serveur
- ✅ `SUPABASE_ANON_KEY` - Clé publique (protégée par RLS)

---

## 📞 SUPPORT

**Développé par**: El Bennouni Farid  
**Email**: gsmfarid@hotmail.fr  
**GitHub**: https://github.com/faridlia171-ship-it/facade-suite

---

## ✅ CHECKLIST DE DÉPLOIEMENT

### Base de données
- [ ] Tables créées sur Supabase
- [ ] RLS activé sur toutes les tables
- [ ] Plans insérés (TRIAL, PRO, ENTREPRISE)
- [ ] Bucket Storage créé (facade-suite-private)

### Backend
- [ ] Service Render créé
- [ ] Variables d'environnement configurées
- [ ] Build réussi
- [ ] Health check fonctionne
- [ ] API docs accessibles

### Frontend
- [ ] Static site Render créé
- [ ] Variables d'environnement configurées
- [ ] Build réussi
- [ ] Redirects configurés
- [ ] Site accessible

### Intégration
- [ ] Frontend se connecte au backend
- [ ] CORS configuré correctement
- [ ] Authentification fonctionne
- [ ] CRUD clients fonctionne
- [ ] CRUD chantiers fonctionne
- [ ] Upload photos fonctionne
- [ ] Création devis fonctionne

---

**Date**: 16 décembre 2024  
**Version**: 1.0.0  
**Statut**: ✅ Prêt pour déploiement
