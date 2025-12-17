# Configuration Supabase – Facade Suite

## 🔒 Vue d'ensemble de sécurité

Ce document explique comment configurer et utiliser Supabase de manière sécurisée dans Facade Suite.

### Architecture de sécurité

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                     │
│  - VITE_SUPABASE_URL ✅ Public                              │
│  - VITE_SUPABASE_ANON_KEY ✅ Public (clé anonyme)           │
│  - Lecture/Write avec RLS                                   │
└────────────────────┬────────────────────────────────────────┘
                     │ (Requêtes SQL, Auth, Storage)
┌────────────────────▼────────────────────────────────────────┐
│                  Supabase PostgreSQL                         │
│  - Row Level Security (RLS) enforced on all tables          │
│  - Policies by company_id (multi-tenant)                    │
└────────────────────┬────────────────────────────────────────┘
                     │ (Opérations sensibles)
┌────────────────────▼────────────────────────────────────────┐
│                   Backend FastAPI                            │
│  - SUPABASE_SERVICE_ROLE_KEY ❌ Secret (backend only)       │
│  - Admin operations, webhooks, batch updates               │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Configuration initiale

### 1. Récupérer les clés Supabase

1. Accéder au [Dashboard Supabase](https://app.supabase.com)
2. Sélectionner votre projet
3. Aller à **Settings** → **API**
4. Copier:
   - `Project URL` (ex: `https://yrsiurdgigqjgycqujmd.supabase.co`)
   - `anon public` key (clé anonyme, 150+ caractères)
   - `service_role secret` (⚠️ JAMAIS côté client)

### 2. Configurer le frontend

Ajouter à `.env.local`:

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**⚠️ Jamais ajouter à `.env.example` les vraies clés!**

### 3. Configurer le backend

Ajouter à `backend/.env`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 🔐 Gestion des clés – Les règles d'or

### ✅ BON – Clé anonyme (public)

```typescript
// ✅ OK: Utilisable côté frontend
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY
```

**Permissions:**
- Lecture/écriture sur les tables avec RLS
- Authentification (signup, login)
- Upload de fichiers publics

### ❌ MAUVAIS – Service role key (secret)

```typescript
// ❌ JAMAIS côté client
const supabaseServiceKey = import.meta.env.VITE_SUPABASE_SERVICE_ROLE_KEY
```

**Pourquoi:**
- ⚠️ Contourne RLS
- ⚠️ Accès admin illimité
- ⚠️ Peut supprimer toute la DB
- ⚠️ Si exposée, compromission totale

**Où l'utiliser:**
- Backend FastAPI uniquement
- Opérations d'administration
- Batch processing
- Webhooks

## 📝 Client Supabase – Implémentation

### Fichier: `src/lib/supabase.ts`

```typescript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

// Validation obligatoire
if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase credentials')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    storageKey: 'facade-suite-auth',
    storage: window.localStorage,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
})
```

### Utilisation dans les composants

```typescript
import { supabase } from '../lib/supabase'

// Récupérer les données
const { data, error } = await supabase
  .from('projects')
  .select('*')
  .eq('company_id', companyId)

// Insérer
const { data, error } = await supabase
  .from('projects')
  .insert([{ name: 'Nouveau projet', company_id: companyId }])

// S'authentifier
const { user, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'password123',
})
```

## 🔒 Row Level Security (RLS) – Structure obligatoire

### Politique de base: Lire ses propres données

```sql
-- Table: projects
-- Politique: SELECT pour les utilisateurs de la même company

CREATE POLICY "Select own company projects" ON projects
  FOR SELECT
  USING (
    company_id IN (
      SELECT company_id FROM profiles 
      WHERE id = auth.uid()
    )
  );
```

### Politique d'écriture

```sql
CREATE POLICY "Insert in own company" ON projects
  FOR INSERT
  WITH CHECK (
    company_id IN (
      SELECT company_id FROM profiles 
      WHERE id = auth.uid()
    )
  );
```

### Vérifier les RLS

```sql
-- Lister toutes les politiques
SELECT * FROM pg_policies WHERE schemaname = 'public';

-- Vérifier qu'une table a RLS activé
SELECT relname, relrowsecurity 
FROM pg_class 
WHERE relname IN ('projects', 'quotes', 'facades');
```

## 🛡️ Checklist de déploiement

- [ ] RLS activé sur **100%** des tables
- [ ] Pas de clés secrètes en .env.example
- [ ] Service role key stockée **backend uniquement**
- [ ] Clé anonyme testée côté frontend
- [ ] Politique d'authentification configurée (Email, Google, GitHub)
- [ ] Bucket Storage privés par défaut
- [ ] Signed URLs pour les fichiers sensibles
- [ ] JWT verification côté backend
- [ ] Rate limiting activé
- [ ] Audit logs configurés

## 🚨 En cas de compromission

Si une clé est exposée:

1. **Clé anonyme compromise:**
   - Regénérer dans Supabase Dashboard > Settings > API > Regenerate
   - Mettre à jour `.env` et redéployer
   - Vérifier les logs pour accès suspects

2. **Service role compromise (backend):**
   - 🚨 **CRITIQUE**: Regénérer immédiatement
   - Vérifier l'audit log pour modifications
   - Rouler DB backup si nécessaire
   - Changer tous les tokens

## 📚 Références

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [JWT Security](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
