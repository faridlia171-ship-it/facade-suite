# Architecture Facade Suite

## Vue d'ensemble

Facade Suite est une application SaaS B2B multi-tenant pour la gestion professionnelle de chantiers de façade. L'architecture suit le pattern **monorepo** avec séparation backend/frontend stricte.

## Stack Technique

### Backend
- **Framework**: FastAPI (Python 3.11)
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Base de données**: PostgreSQL (Supabase)
- **Authentification**: JWT Supabase
- **Storage**: Supabase Storage
- **PDF**: ReportLab

### Frontend
- **Framework**: React 18 + TypeScript
- **Build**: Vite
- **Routing**: React Router
- **UI**: shadcn/ui + Tailwind CSS
- **État**: React Query
- **Auth**: Supabase Auth Client
- **PWA**: Manifest + Service Worker ready

## Architecture Monorepo

```
/
├── backend/
│   ├── app/
│   │   ├── main.py           # Point d'entrée FastAPI
│   │   ├── settings.py       # Configuration centralisée
│   │   ├── api/              # Routes API
│   │   │   ├── auth.py
│   │   │   ├── customers.py
│   │   │   ├── projects.py
│   │   │   ├── facades.py
│   │   │   ├── photos.py
│   │   │   ├── metrage.py
│   │   │   ├── quotes.py
│   │   │   └── pdf.py
│   │   ├── db/
│   │   │   ├── database.py   # Configuration DB
│   │   │   └── models.py     # Modèles SQLAlchemy
│   │   ├── security/
│   │   │   ├── auth.py       # Vérification JWT
│   │   │   └── rate_limit.py
│   │   ├── metrage/          # Logique métrage photo
│   │   ├── pdf/
│   │   │   └── generator.py  # Génération PDF
│   │   └── utils/
│   ├── alembic/              # Migrations DB
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx
│   │   ├── components/
│   │   │   ├── auth/
│   │   │   └── ui/
│   │   ├── pages/
│   │   │   ├── AuthPage.tsx
│   │   │   └── DashboardPage.tsx
│   │   ├── lib/
│   │   │   └── supabase.ts
│   │   └── types/
│   ├── public/
│   │   ├── manifest.json     # PWA manifest
│   │   └── icons/
│   └── package.json
│
├── docs/
│   ├── ARCHITECTURE.md       # Ce fichier
│   ├── DB_SCHEMA.md          # Schéma de données
│   ├── API.md                # Documentation API
│   ├── SECURITY.md           # Sécurité
│   └── DEPLOY_RENDER.md      # Déploiement
│
├── render.yaml               # Configuration Render
├── README.md
└── RAPPORT.md                # Compte-rendu livraison
```

## Flux de Données

### 1. Authentification
```
User → Supabase Auth → JWT Token → Backend API
                    ↓
              Profile + Company
                    ↓
              Dashboard Access
```

### 2. Multi-tenant
Toutes les requêtes sont filtrées par `company_id`:
```
JWT Token → Extract user_id → Load Profile → Get company_id → Filter data
```

### 3. Métrage Photo
```
Mobile → Photo Upload → Supabase Storage → Backend Processing
                                              ↓
                                    Perspective Correction
                                              ↓
                                    Surface Calculation
                                              ↓
                                    Store Results → DB
```

### 4. Génération Devis
```
Frontend → API /quotes → Backend Business Logic
                              ↓
                        Version Management
                              ↓
                        Line Calculation
                              ↓
                        PDF Generation (Server)
                              ↓
                        Upload → Storage
                              ↓
                        Return signed URL
```

## Sécurité

### Multi-tenant Isolation
- **company_id** sur toutes les tables
- **Row-Level Security (RLS)** Supabase
- Vérification systématique dans les API endpoints

### Authentification
- JWT Supabase vérifié côté backend
- Pas de secrets en client
- Tokens auto-renouvelés

### Rate Limiting
- slowapi avec limite configurable
- Par IP + par utilisateur authentifié

### Storage
- Buckets privés
- Signed URLs avec expiration
- Organisation par `company_id/project_id/facade_id`

## Patterns Backend

### Dependency Injection
```python
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> AuthUser:
    # Vérification JWT + chargement profile
```

### Multi-tenant Check
```python
def check_company_access(resource_company_id: str, user_company_id: str):
    if resource_company_id != user_company_id:
        raise HTTPException(status_code=403, detail="Accès refusé")
```

### Atomic Operations
Utilisation de transactions SQLAlchemy pour garantir la cohérence:
```python
db.add(project)
db.flush()
db.add(quote)
db.commit()
```

## Patterns Frontend

### Context API
- `AuthContext`: état global auth + profile
- Évite prop drilling
- Centralise la logique auth

### Protected Routes
```tsx
<PrivateRoute>
  <DashboardPage />
</PrivateRoute>
```

### API Calls
Helper `authenticatedFetch` qui attache automatiquement le JWT:
```typescript
await authenticatedFetch('/api/projects', { method: 'POST', body: ... })
```

## Responsive & Mobile

### Mobile-First
- Design responsive Tailwind
- PWA pour installation mobile
- Offline partiel (photos en cache)

### Touch-Friendly
- Boutons minimum 44x44px
- Espaces tactiles généreux
- Swipe gestures (à venir)

## Performance

### Backend
- Connection pooling PostgreSQL
- Caching (à implémenter avec Redis)
- Compression gzip

### Frontend
- Code splitting Vite
- Lazy loading routes
- React Query caching

## Évolutivité

### Horizontal Scaling
- Backend stateless (JWT)
- Sessions en DB (Supabase)
- Storage distribué (Supabase)

### Database
- Index sur company_id
- Index composites pour queries fréquentes
- Partitioning futur si besoin

## Monitoring (À implémenter)

### Backend
- Logging structuré
- Sentry pour erreurs
- Metrics Prometheus

### Frontend
- Sentry pour erreurs JS
- Analytics privacy-first
- Performance monitoring

## Tests (À implémenter)

### Backend
- Pytest pour unit tests
- Tests d'intégration API
- Tests multi-tenant isolation

### Frontend
- Vitest pour unit tests
- Playwright pour E2E
- Tests a11y

## CI/CD

### GitHub Actions (À configurer)
```yaml
- Lint
- Tests
- Build
- Deploy Render (auto si main)
```

## Next Steps

1. **Phase 1 (MVP)**: Auth + CRUD Projects/Customers ✅
2. **Phase 2**: Métrage photo + Correction perspective
3. **Phase 3**: Devis temps réel + Versioning
4. **Phase 4**: PDF serveur + Anti-triche
5. **Phase 5**: Offline mode + PWA complet
6. **Phase 6**: Analytics + Monitoring
