# Sécurité Facade Suite

## Vue d'ensemble

Facade Suite implémente une stratégie de sécurité **defense-in-depth** avec plusieurs couches de protection.

## 1. Authentification

### JWT Supabase
- **Provider**: Supabase Auth
- **Algorithme**: HS256
- **Expiration**: 1 heure (auto-refresh)
- **Vérification**: Côté backend systématique

### Flow Auth
```
1. User → Supabase Auth (email/password)
2. Supabase → JWT Token (signed)
3. Frontend → Store token (localStorage)
4. API Request → Header Authorization: Bearer <token>
5. Backend → Verify JWT with Supabase secret
6. Backend → Extract user_id + load profile
7. Backend → Check company_id for multi-tenant
```

### Implémentation Backend
```python
async def verify_supabase_token(token: str) -> dict:
    payload = jwt.decode(
        token,
        settings.SUPABASE_JWT_SECRET,
        algorithms=[settings.ALGORITHM],
        audience="authenticated"
    )
    return payload
```

## 2. Multi-tenant Isolation

### Principe
**Chaque ressource appartient à une entreprise (company_id)**.

### Niveaux de Protection

#### Niveau 1: Database (RLS)
Row-Level Security sur toutes les tables:
```sql
CREATE POLICY "Customers are isolated by company"
ON customers
USING (company_id IN (
  SELECT company_id FROM profiles WHERE id = auth.uid()
));
```

#### Niveau 2: Backend (Application)
Vérification systématique:
```python
def check_company_access(resource_company_id: str, user_company_id: str):
    if resource_company_id != user_company_id:
        raise HTTPException(status_code=403, detail="Accès refusé")
```

#### Niveau 3: Frontend (UX)
Filtrage côté client (non fiable seul, mais UX).

### Test Multi-tenant
```python
# Test: User A ne peut pas accéder aux données de User B
assert get_project(user_a_token, user_b_project_id) == 403
```

## 3. Authorization (RBAC)

### Rôles

| Rôle | Permissions |
|------|-------------|
| **OWNER** | Tout (lecture, écriture, suppression, gestion utilisateurs) |
| **USER** | Lecture + écriture (pas de suppression, pas de gestion users) |

### Implémentation
```python
async def require_owner(current_user: AuthUser = Depends(get_current_user)):
    if not current_user.is_owner():
        raise HTTPException(status_code=403, detail="Accès réservé aux propriétaires")
    return current_user
```

### Matrice d'autorisation

| Action | OWNER | USER |
|--------|-------|------|
| Créer client | ✅ | ✅ |
| Créer chantier | ✅ | ✅ |
| Upload photo | ✅ | ✅ |
| Créer devis | ✅ | ✅ |
| Envoyer devis | ✅ | Configurable |
| Supprimer chantier | ✅ | ❌ |
| Gérer utilisateurs | ✅ | ❌ |
| Voir audit logs | ✅ | ❌ |
| Changer plan | ✅ | ❌ |

## 4. Rate Limiting

### Implémentation
- **Bibliothèque**: slowapi
- **Stratégie**: Par IP + par user
- **Limite**: 60 req/min (configurable)

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60/minute"]
)
```

### Headers
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1234567890
```

### Bypass (À implémenter)
- Whitelist IP pour tests automatisés
- Rate limit plus élevé pour plans PRO/ENTREPRISE

## 5. Storage Sécurisé

### Supabase Storage
- **Buckets**: Privés par défaut
- **Accès**: Signed URLs uniquement
- **Expiration**: 1 heure

### Organisation
```
facade-suite-private/
  {company_id}/
    {project_id}/
      {facade_id}/
        photo1.jpg
        photo2.jpg
```

### RLS Storage
```sql
CREATE POLICY "Users can upload to their company folder"
ON storage.objects FOR INSERT
WITH CHECK (
  bucket_id = 'facade-suite-private' AND
  (storage.foldername(name))[1] IN (
    SELECT company_id::text FROM profiles WHERE id = auth.uid()
  )
);
```

### Signed URLs
```python
async with httpx.AsyncClient() as client:
    response = await client.post(
        f"{SUPABASE_URL}/storage/v1/object/sign/{bucket}/{path}",
        headers={"Authorization": f"Bearer {SERVICE_KEY}"},
        json={"expiresIn": 3600}
    )
```

## 6. Secrets Management

### Variables d'environnement
**❌ Jamais en clair dans le code**  
**✅ Variables d'environnement uniquement**

### Backend (.env)
```bash
# Supabase - Service Role (BACKEND ONLY)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...  # ❌ SECRET - Jamais côté client
SUPABASE_JWT_SECRET=your-jwt-secret

# Database
DATABASE_URL=postgresql://...

# Security
SECRET_KEY=your-secret-key-change-me-in-production
```

### Frontend (.env)
```bash
# Supabase - Anonymous Key (PUBLIC - OK)
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGc...  # ✅ PUBLIC - OK d'exposer
VITE_API_URL=http://localhost:8000
```

### Render
Variables stockées dans Dashboard Render (chiffrées).

### 🚨 Règles d'or

| Type de clé | Frontend | Backend | Exposé |
|-------------|----------|---------|--------|
| **VITE_SUPABASE_URL** | ✅ Oui | ✅ Oui | ✅ OUI (public) |
| **VITE_SUPABASE_ANON_KEY** | ✅ Oui | ❌ Non | ✅ OUI (public) |
| **SUPABASE_SERVICE_ROLE_KEY** | ❌ Non | ✅ Oui | ❌ NON (secret) |
| **SUPABASE_JWT_SECRET** | ❌ Non | ✅ Oui | ❌ NON (secret) |

### Voir: `docs/SUPABASE_SETUP.md` pour détails complets

## 7. Audit Logs

### Traçabilité
Toutes les actions sensibles sont loggées:
- Création/suppression chantier
- Envoi devis
- Changement de plan
- Ajout/suppression utilisateur

### Structure
```sql
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY,
  company_id UUID,
  user_id UUID,
  action TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Exemple
```python
def log_action(db: Session, company_id: str, user_id: str, action: str):
    log = AuditLog(
        company_id=company_id,
        user_id=user_id,
        action=action
    )
    db.add(log)
    db.commit()
```

### Consultation
Réservée aux OWNER uniquement.

## 8. PDF Anti-triche

### Génération Serveur
**❌ Jamais côté client** (manipulable)  
**✅ Backend uniquement**

### Hash Unique
Chaque PDF a un hash unique SHA256:
```python
hash_content = f"{version_id}-{timestamp}-{pdf_data[:100]}"
verification_hash = hashlib.sha256(hash_content.encode()).hexdigest()
```

### Page de Vérification
```
https://facade-suite.com/public/verify/{hash}
```
→ Affiche si le PDF est authentique.

### Filigrane TRIAL
```python
if subscription.plan_id == "TRIAL":
    pdf.drawString(x, y, "TRIAL - Document non contractuel")
```

## 9. CORS

### Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Whitelist
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Production
```python
CORS_ORIGINS = [
    "https://facade-suite.com",
    "https://www.facade-suite.com"
]
```

## 10. HTTPS Only

### Render
- HTTPS automatique
- Redirect HTTP → HTTPS
- Certificat SSL auto-renouvelé (Let's Encrypt)

### Headers Sécurité
```python
# À ajouter dans FastAPI
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response
```

## 11. Input Validation

### Pydantic Models
Validation automatique des données:
```python
class CustomerCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None  # Validation email
    phone: Optional[str] = None
    city: Optional[str] = None
```

### SQL Injection
**Protection native SQLAlchemy** (requêtes paramétrées):
```python
# ✅ Safe
db.query(Customer).filter(Customer.id == customer_id)

# ❌ Dangereux (à ne jamais faire)
db.execute(f"SELECT * FROM customers WHERE id = '{customer_id}'")
```

## 12. Backup & Disaster Recovery

### Supabase
- **Backup quotidien**: Automatique
- **Point-in-time recovery**: 7 jours (plan payant)
- **Réplication**: Multi-région

### Stratégie
1. **RTO** (Recovery Time Objective): < 1h
2. **RPO** (Recovery Point Objective): < 24h
3. **Backup test**: Mensuel

## 13. Compliance

### RGPD
- ✅ Consentement clause métrage (stocké en DB)
- ✅ Droit d'accès (export données)
- ✅ Droit à l'oubli (suppression compte + données)
- ✅ Portabilité (export JSON)

### Données Personnelles
| Donnée | Finalité | Base légale |
|--------|----------|-------------|
| Email | Auth + contact | Exécution contrat |
| Nom/prénom client | Gestion chantier | Exécution contrat |
| Photos façades | Métrage | Exécution contrat |

### Responsable Traitement
- **Nom**: SARL Plein Sud Crépis
- **RCS**: 50113927300020
- **Contact**: gsmfarid@hotmail.fr

## 14. Monitoring

### À Implémenter
- **Sentry**: Erreurs backend + frontend
- **Logs centralisés**: Logtail ou Papertrail
- **Alertes**: Email si erreur critique
- **Uptime monitoring**: UptimeRobot

## 15. Checklist Sécurité

Avant production:

- [ ] JWT Supabase vérifié backend
- [ ] RLS activé sur toutes les tables
- [ ] Multi-tenant testé (isolation)
- [ ] Rate limiting configuré
- [ ] Secrets en variables d'environnement
- [ ] CORS configuré (whitelist)
- [ ] HTTPS only
- [ ] Headers sécurité
- [ ] Audit logs en place
- [ ] Backup testé
- [ ] Monitoring configuré
- [ ] Plan incident response documenté

## 16. Incident Response

### Scénarios

#### 1. Fuite Token
1. Révoquer token Supabase
2. Forcer logout utilisateur
3. Notifier utilisateur
4. Changer secrets si nécessaire

#### 2. Accès Non Autorisé
1. Identifier la brèche (logs)
2. Bloquer IP si applicable
3. Audit complet des accès
4. Notification utilisateurs impactés

#### 3. Attaque DDoS
1. Activer Cloudflare
2. Rate limiting agressif
3. Bloquer IPs malveillantes
4. Scaler infrastructure

### Contact Urgence
- **Email**: gsmfarid@hotmail.fr
- **Phone**: [À configurer]
