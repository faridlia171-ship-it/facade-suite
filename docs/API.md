# Documentation API Facade Suite

## Base URL

**Local**: `http://localhost:8000`  
**Production**: `https://api.facade-suite.render.com`

## Authentification

Toutes les routes (sauf `/` et `/health`) nécessitent un JWT Supabase dans le header:

```
Authorization: Bearer <jwt_token>
```

## Routes

### Santé

#### `GET /`
Racine de l'API.

**Réponse**:
```json
{
  "app": "Facade Suite",
  "version": "1.0.0",
  "status": "ok"
}
```

#### `GET /health`
Health check.

**Réponse**:
```json
{
  "status": "healthy"
}
```

---

### Authentification

#### `POST /api/auth/onboarding`
Création entreprise + profil après inscription Supabase.

**Body**:
```json
{
  "company_name": "Ma Société",
  "accepted_terms": true,
  "user_id": "uuid-from-supabase"
}
```

**Réponse** `200`:
```json
{
  "message": "Onboarding réussi",
  "company_id": "uuid",
  "profile_id": "uuid"
}
```

**Erreurs**:
- `400`: Conditions non acceptées ou profil déjà existant

#### `GET /api/auth/me`
Récupère le profil de l'utilisateur courant.

**Réponse** `200`:
```json
{
  "user_id": "uuid",
  "company_id": "uuid",
  "company_name": "Ma Société",
  "role": "OWNER",
  "plan_id": "TRIAL",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### Clients

#### `POST /api/customers`
Crée un nouveau client.

**Body**:
```json
{
  "name": "Jean Dupont",
  "email": "jean@example.com",
  "phone": "0612345678",
  "city": "Paris"
}
```

**Réponse** `200`:
```json
{
  "id": "uuid",
  "company_id": "uuid",
  "name": "Jean Dupont",
  "email": "jean@example.com",
  "phone": "0612345678",
  "city": "Paris"
}
```

#### `GET /api/customers`
Liste tous les clients de l'entreprise.

**Réponse** `200`:
```json
[
  {
    "id": "uuid",
    "company_id": "uuid",
    "name": "Jean Dupont",
    "email": "jean@example.com",
    "phone": "0612345678",
    "city": "Paris"
  }
]
```

#### `GET /api/customers/{customer_id}`
Récupère un client par ID.

**Réponse** `200`: Même structure que POST.

**Erreurs**:
- `404`: Client non trouvé
- `403`: Client d'une autre entreprise

---

### Chantiers

#### `POST /api/projects`
Crée un nouveau chantier (+ devis auto).

**Body**:
```json
{
  "customer_id": "uuid",
  "name": "Rénovation façade rue de la Paix"
}
```

**Réponse** `200`:
```json
{
  "id": "uuid",
  "company_id": "uuid",
  "customer_id": "uuid",
  "customer_name": "Jean Dupont",
  "name": "Rénovation façade rue de la Paix",
  "status": "draft"
}
```

#### `GET /api/projects`
Liste tous les chantiers de l'entreprise.

**Réponse** `200`: Array de projets.

#### `GET /api/projects/{project_id}`
Récupère un chantier par ID.

**Réponse** `200`: Même structure que POST.

---

### Façades

#### `POST /api/facades`
Crée une façade pour un chantier.

**Body**:
```json
{
  "project_id": "uuid",
  "code": "A"
}
```

**Réponse** `200`:
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "code": "A",
  "duplicated_from": null
}
```

#### `POST /api/facades/duplicate`
Duplique une façade (opposée).

**Body**:
```json
{
  "source_facade_id": "uuid",
  "target_code": "C"
}
```

**Réponse** `200`:
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "code": "C",
  "duplicated_from": "source-uuid"
}
```

#### `GET /api/facades/project/{project_id}`
Liste les façades d'un chantier.

**Réponse** `200`: Array de façades.

---

### Photos

#### `POST /api/photos/upload`
Upload une photo de façade.

**Form Data**:
- `facade_id`: UUID
- `file`: Image (multipart/form-data)

**Réponse** `200`:
```json
{
  "id": "uuid",
  "facade_id": "uuid",
  "storage_path": "company/project/facade/photo.jpg",
  "signed_url": "https://...",
  "quality": null
}
```

**Erreurs**:
- `404`: Façade non trouvée
- `403`: Façade d'une autre entreprise
- `500`: Erreur upload Supabase

#### `GET /api/photos/facade/{facade_id}`
Liste les photos d'une façade.

**Réponse** `200`:
```json
[
  {
    "id": "uuid",
    "facade_id": "uuid",
    "storage_path": "...",
    "quality": "green"
  }
]
```

---

### Métrage

#### `POST /api/metrage/ref`
Crée une référence de métrage.

**Body**:
```json
{
  "project_id": "uuid",
  "type": "agglo",
  "width_cm": 50.0,
  "height_cm": 20.0
}
```

**Réponse** `200`:
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "type": "agglo",
  "width_cm": 50.0,
  "height_cm": 20.0
}
```

#### `POST /api/metrage/calculate`
Calcule le métrage d'une façade.

**Body**:
```json
{
  "photo_id": "uuid",
  "ref_width_px": 100,
  "ref_height_px": 40,
  "facade_width_px": 800,
  "facade_height_px": 600,
  "openings": [
    {
      "width_px": 150,
      "height_px": 200
    }
  ]
}
```

**Réponse** `200`:
```json
{
  "surface_m2": 48.5,
  "width_m": 8.5,
  "height_m": 5.7,
  "openings_m2": 2.1,
  "net_surface_m2": 46.4
}
```

---

### Devis

#### `GET /api/quotes/project/{project_id}`
Récupère le devis d'un chantier.

**Réponse** `200`:
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "status": "draft",
  "current_version": 1
}
```

#### `GET /api/quotes/version/{version_id}`
Récupère une version de devis.

**Réponse** `200`:
```json
{
  "id": "uuid",
  "quote_id": "uuid",
  "version": 1,
  "total": 12500.50,
  "lines": [
    {
      "id": "uuid",
      "label": "Ravalement façade",
      "quantity": 45.0,
      "unit_price": 250.0,
      "total": 11250.0
    }
  ],
  "pdf_path": null
}
```

#### `POST /api/quotes/{quote_id}/lines`
Ajoute une ligne au devis.

**Body**:
```json
{
  "label": "Ravalement façade",
  "quantity": 45.0,
  "unit_price": 250.0
}
```

**Réponse** `200`:
```json
{
  "id": "uuid",
  "label": "Ravalement façade",
  "quantity": 45.0,
  "unit_price": 250.0,
  "total": 11250.0
}
```

#### `POST /api/quotes/{quote_id}/new-version`
Crée une nouvelle version du devis.

**Réponse** `200`:
```json
{
  "message": "Nouvelle version créée",
  "version": 2
}
```

---

### PDF

#### `POST /api/pdf/generate`
Génère un PDF pour une version de devis.

**Body**:
```json
{
  "quote_version_id": "uuid"
}
```

**Réponse** `200`:
```json
{
  "pdf_path": "pdfs/company/quote/v1.pdf",
  "verification_hash": "sha256...",
  "verification_url": "/public/verify/sha256..."
}
```

**Notes**:
- PDF généré côté serveur
- Filigrane TRIAL si plan gratuit
- Hash unique pour anti-triche

#### `GET /api/pdf/verify/{hash}`
Page publique de vérification PDF.

**Réponse** `200`:
```json
{
  "valid": true,
  "message": "PDF authentique généré par Facade Suite"
}
```

---

## Codes d'Erreur

| Code | Description |
|------|-------------|
| `400` | Bad Request (données invalides) |
| `401` | Unauthorized (JWT manquant/invalide) |
| `403` | Forbidden (accès multi-tenant refusé) |
| `404` | Not Found (ressource inexistante) |
| `429` | Too Many Requests (rate limit) |
| `500` | Internal Server Error |

## Rate Limiting

- **Limite**: 60 requêtes/minute par IP
- **Header**: `X-RateLimit-Remaining`

## CORS

**Origines autorisées**:
- `http://localhost:5173` (dev)
- `https://your-domain.com` (prod)

## Pagination

Non implémentée dans la V1. À venir:
```
GET /api/projects?page=1&limit=20
```

## Filtering

Non implémenté dans la V1. À venir:
```
GET /api/projects?status=active&customer_id=uuid
```

## Webhooks

Non disponible dans la V1. Prévu pour notifications:
- Devis accepté
- Paiement reçu
- Chantier terminé
