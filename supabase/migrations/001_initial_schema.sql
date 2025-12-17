-- =====================================================
-- FACADE SUITE - SUPABASE DATABASE SCHEMA
-- Version: 1.0.0
-- Date: 2025-12-16
-- Description: Complete schema with RLS for SaaS B2B
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- TABLE 1: companies
-- =====================================================
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS on companies
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own company"
    ON companies FOR SELECT
    USING (id IN (
        SELECT company_id FROM profiles WHERE id = auth.uid()
    ));

CREATE POLICY "Users can update their own company"
    ON companies FOR UPDATE
    USING (id IN (
        SELECT company_id FROM profiles WHERE id = auth.uid() AND role = 'OWNER'
    ));

-- =====================================================
-- TABLE 2: profiles (lié à auth.users)
-- =====================================================
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id),
    role TEXT NOT NULL CHECK (role IN ('OWNER', 'USER')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS on profiles
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own profile"
    ON profiles FOR SELECT
    USING (id = auth.uid());

CREATE POLICY "Users can view profiles in their company"
    ON profiles FOR SELECT
    USING (company_id IN (
        SELECT company_id FROM profiles WHERE id = auth.uid()
    ));

CREATE POLICY "Owners can update profiles in their company"
    ON profiles FOR UPDATE
    USING (company_id IN (
        SELECT company_id FROM profiles WHERE id = auth.uid() AND role = 'OWNER'
    ));

CREATE POLICY "Owners can insert profiles in their company"
    ON profiles FOR INSERT
    WITH CHECK (company_id IN (
        SELECT company_id FROM profiles WHERE id = auth.uid() AND role = 'OWNER'
    ));

-- =====================================================
-- TABLE 3: customers
-- =====================================================
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL,
    name TEXT,
    email TEXT,
    phone TEXT,
    city TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS on customers
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view customers in their company"
    ON customers FOR SELECT
    USING (company_id IN (
        SELECT company_id FROM profiles WHERE id = auth.uid()
    ));

CREATE POLICY "Users can insert customers in their company"
    ON customers FOR INSERT
    WITH CHECK (company_id IN (
        SELECT company_id FROM profiles WHERE id = auth.uid()
    ));

CREATE POLICY "Users can update customers in their company"
    ON customers FOR UPDATE
    USING (company_id IN (
        SELECT company_id FROM profiles WHERE id = auth.uid()
    ));

CREATE POLICY "Users can delete customers in their company"
    ON customers FOR DELETE
    USING (company_id IN (
        SELECT company_id FROM profiles WHERE id = auth.uid()
    ));

-- =====================================================
-- TABLE 4: projects (chantiers)
-- =====================================================
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL,
    customer_id UUID NOT NULL REFERENCES customers(id),
    name TEXT,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS on projects
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view projects in their company"
    ON projects FOR SELECT
    USING (company_id IN (
        SELECT company_id FROM profiles WHERE id = auth.uid()
    ));

CREATE POLICY "Users can insert projects in their company"
    ON projects FOR INSERT
    WITH CHECK (company_id IN (
        SELECT company_id FROM profiles WHERE id = auth.uid()
    ));

CREATE POLICY "Users can update projects in their company"
    ON projects FOR UPDATE
    USING (company_id IN (
        SELECT company_id FROM profiles WHERE id = auth.uid()
    ));

CREATE POLICY "Users can delete projects in their company"
    ON projects FOR DELETE
    USING (company_id IN (
        SELECT company_id FROM profiles WHERE id = auth.uid()
    ));

-- =====================================================
-- TABLE 5: facades
-- =====================================================
CREATE TABLE facades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id),
    code TEXT, -- A, B, C, D
    duplicated_from UUID REFERENCES facades(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS on facades
ALTER TABLE facades ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view facades in their company projects"
    ON facades FOR SELECT
    USING (project_id IN (
        SELECT id FROM projects WHERE company_id IN (
            SELECT company_id FROM profiles WHERE id = auth.uid()
        )
    ));

CREATE POLICY "Users can insert facades in their company projects"
    ON facades FOR INSERT
    WITH CHECK (project_id IN (
        SELECT id FROM projects WHERE company_id IN (
            SELECT company_id FROM profiles WHERE id = auth.uid()
        )
    ));

CREATE POLICY "Users can update facades in their company projects"
    ON facades FOR UPDATE
    USING (project_id IN (
        SELECT id FROM projects WHERE company_id IN (
            SELECT company_id FROM profiles WHERE id = auth.uid()
        )
    ));

CREATE POLICY "Users can delete facades in their company projects"
    ON facades FOR DELETE
    USING (project_id IN (
        SELECT id FROM projects WHERE company_id IN (
            SELECT company_id FROM profiles WHERE id = auth.uid()
        )
    ));

-- =====================================================
-- TABLE 6: photos
-- =====================================================
CREATE TABLE photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    facade_id UUID NOT NULL REFERENCES facades(id),
    storage_path TEXT NOT NULL,
    quality TEXT CHECK (quality IN ('green', 'orange', 'red')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS on photos
ALTER TABLE photos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view photos in their company facades"
    ON photos FOR SELECT
    USING (facade_id IN (
        SELECT f.id FROM facades f
        INNER JOIN projects p ON f.project_id = p.id
        WHERE p.company_id IN (
            SELECT company_id FROM profiles WHERE id = auth.uid()
        )
    ));

CREATE POLICY "Users can insert photos in their company facades"
    ON photos FOR INSERT
    WITH CHECK (facade_id IN (
        SELECT f.id FROM facades f
        INNER JOIN projects p ON f.project_id = p.id
        WHERE p.company_id IN (
            SELECT company_id FROM profiles WHERE id = auth.uid()
        )
    ));

CREATE POLICY "Users can update photos in their company facades"
    ON photos FOR UPDATE
    USING (facade_id IN (
        SELECT f.id FROM facades f
        INNER JOIN projects p ON f.project_id = p.id
        WHERE p.company_id IN (
            SELECT company_id FROM profiles WHERE id = auth.uid()
        )
    ));

CREATE POLICY "Users can delete photos in their company facades"
    ON photos FOR DELETE
    USING (facade_id IN (
        SELECT f.id FROM facades f
        INNER JOIN projects p ON f.project_id = p.id
        WHERE p.company_id IN (
            SELECT company_id FROM profiles WHERE id = auth.uid()
        )
    ));

-- =====================================================
-- TABLE 7: metrage_refs
-- =====================================================
CREATE TABLE metrage_refs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id),
    type TEXT, -- agglo, custom
    width_cm NUMERIC,
    height_cm NUMERIC
);

-- RLS on metrage_refs
ALTER TABLE metrage_refs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view metrage_refs in their company projects"
    ON metrage_refs FOR SELECT
    USING (project_id IN (
        SELECT id FROM projects WHERE company_id IN (
            SELECT company_id FROM profiles WHERE id = auth.uid()
        )
    ));

CREATE POLICY "Users can insert metrage_refs in their company projects"
    ON metrage_refs FOR INSERT
    WITH CHECK (project_id IN (
        SELECT id FROM projects WHERE company_id IN (
            SELECT company_id FROM profiles WHERE id = auth.uid()
        )
    ));

CREATE POLICY "Users can update metrage_refs in their company projects"
    ON metrage_refs FOR UPDATE
    USING (project_id IN (
        SELECT id FROM projects WHERE company_id IN (
            SELECT company_id FROM profiles WHERE id = auth.uid()
        )
    ));

CREATE POLICY "Users can delete metrage_refs in their company projects"
    ON metrage_refs FOR DELETE
    USING (project_id IN (
        SELECT id FROM projects WHERE company_id IN (
            SELECT company_id FROM profiles WHERE id = auth.uid()
        )
    ));

-- =====================================================
-- TABLE 8: quotes
-- =====================================================
CREATE TABLE quotes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id),
    status TEXT,
    current_version INT DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS on quotes
ALTER TABLE quotes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view quotes in their company projects"
    ON quotes FOR SELECT
    USING (project_id IN (
        SELECT id FROM projects WHERE company_id IN (
            SELECT company_id FROM profiles WHERE id = auth.uid()
        )
    ));

CREATE POLICY "Users can insert quotes in their company projects"
    ON quotes FOR INSERT
    WITH CHECK (project_id IN (
        SELECT id FROM projects WHERE company_id IN (
            SELECT company_id FROM profiles WHERE id = auth.uid()
        )
    ));

CREATE POLICY "Users can update quotes in their company projects"
    ON quotes FOR UPDATE
    USING (project_id IN (
        SELECT id FROM projects WHERE company_id IN (
            SELECT company_id FROM profiles WHERE id = auth.uid()
        )
    ));

CREATE POLICY "Users can delete quotes in their company projects"
    ON quotes FOR DELETE
    USING (project_id IN (
        SELECT id FROM projects WHERE company_id IN (
            SELECT company_id FROM profiles WHERE id = auth.uid()
        )
    ));

-- =====================================================
-- TABLE 9: quote_versions
-- =====================================================
CREATE TABLE quote_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quote_id UUID NOT NULL REFERENCES quotes(id),
    version INT NOT NULL,
    total NUMERIC,
    pdf_path TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS on quote_versions
ALTER TABLE quote_versions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view quote_versions in their company quotes"
    ON quote_versions FOR SELECT
    USING (quote_id IN (
        SELECT q.id FROM quotes q
        INNER JOIN projects p ON q.project_id = p.id
        WHERE p.company_id IN (
            SELECT company_id FROM profiles WHERE id = auth.uid()
        )
    ));

CREATE POLICY "Users can insert quote_versions in their company quotes"
    ON quote_versions FOR INSERT
    WITH CHECK (quote_id IN (
        SELECT q.id FROM quotes q
        INNER JOIN projects p ON q.project_id = p.id
        WHERE p.company_id IN (
            SELECT company_id FROM profiles WHERE id = auth.uid()
        )
    ));

CREATE POLICY "Users can update quote_versions in their company quotes"
    ON quote_versions FOR UPDATE
    USING (quote_id IN (
        SELECT q.id FROM quotes q
        INNER JOIN projects p ON q.project_id = p.id
        WHERE p.company_id IN (
            SELECT company_id FROM profiles WHERE id = auth.uid()
        )
    ));

CREATE POLICY "Users can delete quote_versions in their company quotes"
    ON quote_versions FOR DELETE
    USING (quote_id IN (
        SELECT q.id FROM quotes q
        INNER JOIN projects p ON q.project_id = p.id
        WHERE p.company_id IN (
            SELECT company_id FROM profiles WHERE id = auth.uid()
        )
    ));

-- =====================================================
-- TABLE 10: quote_lines
-- =====================================================
CREATE TABLE quote_lines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quote_version_id UUID NOT NULL REFERENCES quote_versions(id),
    label TEXT,
    quantity NUMERIC,
    unit_price NUMERIC,
    total NUMERIC
);

-- RLS on quote_lines
ALTER TABLE quote_lines ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view quote_lines in their company quote_versions"
    ON quote_lines FOR SELECT
    USING (quote_version_id IN (
        SELECT qv.id FROM quote_versions qv
        INNER JOIN quotes q ON qv.quote_id = q.id
        INNER JOIN projects p ON q.project_id = p.id
        WHERE p.company_id IN (
            SELECT company_id FROM profiles WHERE id = auth.uid()
        )
    ));

CREATE POLICY "Users can insert quote_lines in their company quote_versions"
    ON quote_lines FOR INSERT
    WITH CHECK (quote_version_id IN (
        SELECT qv.id FROM quote_versions qv
        INNER JOIN quotes q ON qv.quote_id = q.id
        INNER JOIN projects p ON q.project_id = p.id
        WHERE p.company_id IN (
            SELECT company_id FROM profiles WHERE id = auth.uid()
        )
    ));

CREATE POLICY "Users can update quote_lines in their company quote_versions"
    ON quote_lines FOR UPDATE
    USING (quote_version_id IN (
        SELECT qv.id FROM quote_versions qv
        INNER JOIN quotes q ON qv.quote_id = q.id
        INNER JOIN projects p ON q.project_id = p.id
        WHERE p.company_id IN (
            SELECT company_id FROM profiles WHERE id = auth.uid()
        )
    ));

CREATE POLICY "Users can delete quote_lines in their company quote_versions"
    ON quote_lines FOR DELETE
    USING (quote_version_id IN (
        SELECT qv.id FROM quote_versions qv
        INNER JOIN quotes q ON qv.quote_id = q.id
        INNER JOIN projects p ON q.project_id = p.id
        WHERE p.company_id IN (
            SELECT company_id FROM profiles WHERE id = auth.uid()
        )
    ));

-- =====================================================
-- TABLE 11: plans
-- =====================================================
CREATE TABLE plans (
    id TEXT PRIMARY KEY,
    max_projects INT,
    max_users INT
);

-- RLS on plans (lecture publique pour tous les users authentifiés)
ALTER TABLE plans ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authenticated users can view plans"
    ON plans FOR SELECT
    USING (auth.uid() IS NOT NULL);

-- Insert default plans
INSERT INTO plans (id, max_projects, max_users) VALUES
    ('TRIAL', 1, 1),
    ('PRO', NULL, 1),
    ('ENTREPRISE', NULL, 5);

-- =====================================================
-- TABLE 12: subscriptions
-- =====================================================
CREATE TABLE subscriptions (
    company_id UUID PRIMARY KEY REFERENCES companies(id),
    plan_id TEXT REFERENCES plans(id),
    status TEXT,
    started_at TIMESTAMPTZ
);

-- RLS on subscriptions
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their company subscription"
    ON subscriptions FOR SELECT
    USING (company_id IN (
        SELECT company_id FROM profiles WHERE id = auth.uid()
    ));

CREATE POLICY "Owners can update their company subscription"
    ON subscriptions FOR UPDATE
    USING (company_id IN (
        SELECT company_id FROM profiles WHERE id = auth.uid() AND role = 'OWNER'
    ));

CREATE POLICY "Owners can insert their company subscription"
    ON subscriptions FOR INSERT
    WITH CHECK (company_id IN (
        SELECT company_id FROM profiles WHERE id = auth.uid() AND role = 'OWNER'
    ));

-- =====================================================
-- TABLE 13: audit_logs
-- =====================================================
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    user_id UUID REFERENCES profiles(id),
    action TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS on audit_logs
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view audit_logs in their company"
    ON audit_logs FOR SELECT
    USING (company_id IN (
        SELECT company_id FROM profiles WHERE id = auth.uid()
    ));

CREATE POLICY "System can insert audit_logs"
    ON audit_logs FOR INSERT
    WITH CHECK (true); -- Allow inserts from backend

-- =====================================================
-- STORAGE BUCKET CONFIGURATION
-- =====================================================
-- Run this in Supabase Storage UI or via API:
-- Bucket name: facade-suite-private
-- Public: false
-- File size limit: 10MB
-- Allowed MIME types: image/jpeg, image/png, application/pdf

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================
CREATE INDEX idx_profiles_company_id ON profiles(company_id);
CREATE INDEX idx_customers_company_id ON customers(company_id);
CREATE INDEX idx_projects_company_id ON projects(company_id);
CREATE INDEX idx_projects_customer_id ON projects(customer_id);
CREATE INDEX idx_facades_project_id ON facades(project_id);
CREATE INDEX idx_photos_facade_id ON photos(facade_id);
CREATE INDEX idx_metrage_refs_project_id ON metrage_refs(project_id);
CREATE INDEX idx_quotes_project_id ON quotes(project_id);
CREATE INDEX idx_quote_versions_quote_id ON quote_versions(quote_id);
CREATE INDEX idx_quote_lines_quote_version_id ON quote_lines(quote_version_id);
CREATE INDEX idx_audit_logs_company_id ON audit_logs(company_id);

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================
COMMENT ON TABLE companies IS 'Entreprises clientes (tenants multi-entreprise)';
COMMENT ON TABLE profiles IS 'Profils utilisateurs liés à auth.users avec rôles OWNER/USER';
COMMENT ON TABLE customers IS 'Clients finaux des chantiers';
COMMENT ON TABLE projects IS 'Chantiers de façade';
COMMENT ON TABLE facades IS 'Façades d''un chantier (A, B, C, D)';
COMMENT ON TABLE photos IS 'Photos de façades avec qualité (green/orange/red)';
COMMENT ON TABLE metrage_refs IS 'Références de métrage (agglo 20x50 ou custom)';
COMMENT ON TABLE quotes IS 'Devis avec versioning';
COMMENT ON TABLE quote_versions IS 'Versions successives d''un devis (V1, V2, V3)';
COMMENT ON TABLE quote_lines IS 'Lignes de prestations d''un devis';
COMMENT ON TABLE plans IS 'Plans d''abonnement (TRIAL, PRO, ENTREPRISE)';
COMMENT ON TABLE subscriptions IS 'Abonnements des entreprises';
COMMENT ON TABLE audit_logs IS 'Logs d''audit pour traçabilité';

-- =====================================================
-- END OF SCHEMA
-- =====================================================
