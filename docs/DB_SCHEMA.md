# Schéma de Base de Données

## Vue d'ensemble

Base de données PostgreSQL hébergée sur Supabase. Toutes les tables implémentent le multi-tenant via `company_id` avec Row-Level Security (RLS).

## Diagramme ERD

```
auth.users (Supabase)
    ↓
profiles → companies
    ↑           ↓
    |      customers
    |           ↓
    |      projects
    |       ↙   ↓
    | facades  quotes
    |    ↓       ↓
    | photos  quote_versions
    |             ↓
    |        quote_lines
    |
    └── audit_logs

subscriptions ← plans
    ↓
companies
```

## Tables Détaillées

### companies
Entreprise cliente (tenant racine).

```sql
CREATE TABLE companies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Companies are viewable by members"
ON companies FOR SELECT
USING (id IN (
  SELECT company_id FROM profiles WHERE id = auth.uid()
));
```

### profiles
Profil utilisateur lié à auth.users de Supabase.

```sql
CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  company_id UUID REFERENCES companies(id) NOT NULL,
  role TEXT CHECK (role IN ('OWNER', 'USER')) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Profiles are viewable by same company"
ON profiles FOR SELECT
USING (company_id IN (
  SELECT company_id FROM profiles WHERE id = auth.uid()
));
```

### customers
Clients des chantiers.

```sql
CREATE TABLE customers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL,
  name TEXT,
  email TEXT,
  phone TEXT,
  city TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX idx_customers_company ON customers(company_id);

-- RLS
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Customers are isolated by company"
ON customers
USING (company_id IN (
  SELECT company_id FROM profiles WHERE id = auth.uid()
));
```

### projects
Chantiers de façade.

```sql
CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL,
  customer_id UUID REFERENCES customers(id) NOT NULL,
  name TEXT,
  status TEXT DEFAULT 'draft',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX idx_projects_company ON projects(company_id);
CREATE INDEX idx_projects_customer ON projects(customer_id);

-- RLS
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Projects are isolated by company"
ON projects
USING (company_id IN (
  SELECT company_id FROM profiles WHERE id = auth.uid()
));
```

### facades
Façades d'un chantier (A, B, C, D).

```sql
CREATE TABLE facades (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id) NOT NULL,
  code TEXT, -- A, B, C, D
  duplicated_from UUID REFERENCES facades(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX idx_facades_project ON facades(project_id);

-- RLS via project
ALTER TABLE facades ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Facades are isolated by company"
ON facades
USING (project_id IN (
  SELECT id FROM projects WHERE company_id IN (
    SELECT company_id FROM profiles WHERE id = auth.uid()
  )
));
```

### photos
Photos de façades stockées dans Supabase Storage.

```sql
CREATE TABLE photos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  facade_id UUID REFERENCES facades(id) NOT NULL,
  storage_path TEXT NOT NULL,
  quality TEXT CHECK (quality IN ('green', 'orange', 'red')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX idx_photos_facade ON photos(facade_id);

-- RLS via facade → project
ALTER TABLE photos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Photos are isolated by company"
ON photos
USING (facade_id IN (
  SELECT id FROM facades WHERE project_id IN (
    SELECT id FROM projects WHERE company_id IN (
      SELECT company_id FROM profiles WHERE id = auth.uid()
    )
  )
));
```

### metrage_refs
Références de métrage (agglo 20×50 ou custom).

```sql
CREATE TABLE metrage_refs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id) NOT NULL,
  type TEXT, -- 'agglo', 'custom'
  width_cm NUMERIC,
  height_cm NUMERIC
);

-- Index
CREATE INDEX idx_metrage_refs_project ON metrage_refs(project_id);

-- RLS via project
ALTER TABLE metrage_refs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Metrage refs are isolated by company"
ON metrage_refs
USING (project_id IN (
  SELECT id FROM projects WHERE company_id IN (
    SELECT company_id FROM profiles WHERE id = auth.uid()
  )
));
```

### quotes
Devis (1 par projet, auto-créé).

```sql
CREATE TABLE quotes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id) NOT NULL,
  status TEXT,
  current_version INT DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX idx_quotes_project ON quotes(project_id);

-- RLS via project
ALTER TABLE quotes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Quotes are isolated by company"
ON quotes
USING (project_id IN (
  SELECT id FROM projects WHERE company_id IN (
    SELECT company_id FROM profiles WHERE id = auth.uid()
  )
));
```

### quote_versions
Versions d'un devis (V1, V2, V3...).

```sql
CREATE TABLE quote_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  quote_id UUID REFERENCES quotes(id) NOT NULL,
  version INT NOT NULL,
  total NUMERIC,
  pdf_path TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(quote_id, version)
);

-- Index
CREATE INDEX idx_quote_versions_quote ON quote_versions(quote_id);

-- RLS via quote → project
ALTER TABLE quote_versions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Quote versions are isolated by company"
ON quote_versions
USING (quote_id IN (
  SELECT id FROM quotes WHERE project_id IN (
    SELECT id FROM projects WHERE company_id IN (
      SELECT company_id FROM profiles WHERE id = auth.uid()
    )
  )
));
```

### quote_lines
Lignes d'une version de devis.

```sql
CREATE TABLE quote_lines (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  quote_version_id UUID REFERENCES quote_versions(id) NOT NULL,
  label TEXT,
  quantity NUMERIC,
  unit_price NUMERIC,
  total NUMERIC
);

-- Index
CREATE INDEX idx_quote_lines_version ON quote_lines(quote_version_id);

-- RLS via quote_version → quote → project
ALTER TABLE quote_lines ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Quote lines are isolated by company"
ON quote_lines
USING (quote_version_id IN (
  SELECT id FROM quote_versions WHERE quote_id IN (
    SELECT id FROM quotes WHERE project_id IN (
      SELECT id FROM projects WHERE company_id IN (
        SELECT company_id FROM profiles WHERE id = auth.uid()
      )
    )
  )
));
```

### plans
Plans d'abonnement (TRIAL, PRO, ENTREPRISE).

```sql
CREATE TABLE plans (
  id TEXT PRIMARY KEY, -- 'TRIAL', 'PRO', 'ENTREPRISE'
  max_projects INT,
  max_users INT
);

-- Données de référence
INSERT INTO plans (id, max_projects, max_users) VALUES
  ('TRIAL', 1, 1),
  ('PRO', -1, 1),    -- -1 = illimité
  ('ENTREPRISE', -1, 5);

-- Pas de RLS (lecture publique)
```

### subscriptions
Abonnements des entreprises.

```sql
CREATE TABLE subscriptions (
  company_id UUID PRIMARY KEY REFERENCES companies(id),
  plan_id TEXT REFERENCES plans(id),
  status TEXT,
  started_at TIMESTAMPTZ
);

-- RLS
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Subscriptions are viewable by company members"
ON subscriptions FOR SELECT
USING (company_id IN (
  SELECT company_id FROM profiles WHERE id = auth.uid()
));
```

### audit_logs
Logs d'audit pour traçabilité.

```sql
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID REFERENCES companies(id),
  user_id UUID REFERENCES profiles(id),
  action TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX idx_audit_logs_company ON audit_logs(company_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);

-- RLS
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Audit logs are isolated by company"
ON audit_logs FOR SELECT
USING (company_id IN (
  SELECT company_id FROM profiles WHERE id = auth.uid()
));

-- Seuls les OWNER peuvent voir les logs
CREATE POLICY "Only owners can view audit logs"
ON audit_logs FOR SELECT
USING (
  company_id IN (
    SELECT company_id FROM profiles 
    WHERE id = auth.uid() AND role = 'OWNER'
  )
);
```

## Règles Métier

### 1. Multi-tenant Strict
- **company_id** présent sur toutes les tables racines
- RLS activé sur 100% des tables
- Vérification côté backend en plus

### 2. Cascade Deletes
- Pas de suppression en prod (soft delete recommandé)
- Si suppression: CASCADE sur relations

### 3. Versioning Devis
- Immutable: une fois créée, une version n'est jamais modifiée
- Nouvelle version = copie + modifications

### 4. Storage
- Structure: `{bucket}/{company_id}/{project_id}/{facade_id}/{filename}`
- Signed URLs avec expiration 1h
- Nettoyage périodique (à implémenter)

## Migrations

Utiliser Alembic pour toutes les modifications:

```bash
# Créer une migration
cd backend
alembic revision -m "Add new field"

# Appliquer
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Backup

Supabase gère les backups automatiques:
- Point-in-time recovery 7 jours (plan payant)
- Snapshots quotidiens

## Optimisations

### Index Composites (À ajouter si besoin)
```sql
CREATE INDEX idx_projects_company_status ON projects(company_id, status);
CREATE INDEX idx_quotes_project_status ON quotes(project_id, status);
```

### Partitioning (Futur)
Si volume important, partitionner par company_id ou par date.

## Contraintes Supplémentaires

### Limite TRIAL
```sql
-- Trigger pour limiter les projets en TRIAL (à implémenter)
CREATE OR REPLACE FUNCTION check_trial_limit()
RETURNS TRIGGER AS $$
BEGIN
  -- Vérifier le nombre de projets si plan = TRIAL
  -- Bloquer si limite atteinte
END;
$$ LANGUAGE plpgsql;
```
