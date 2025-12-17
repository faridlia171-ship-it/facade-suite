"""Point d'entrée principal de l'API FastAPI."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .settings import settings
from .security.rate_limit import limiter
from .api import auth, projects, customers, facades, photos, metrage, quotes, pdf

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API SaaS B2B pour gestion de chantiers de façade"
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Route racine."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "ok"
    }


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy"}


# Inclusion des routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(facades.router, prefix="/api/facades", tags=["facades"])
app.include_router(photos.router, prefix="/api/photos", tags=["photos"])
app.include_router(metrage.router, prefix="/api/metrage", tags=["metrage"])
app.include_router(quotes.router, prefix="/api/quotes", tags=["quotes"])
app.include_router(pdf.router, prefix="/api/pdf", tags=["pdf"])

# Import companies router
from .api import companies
app.include_router(companies.router, prefix="/api/companies", tags=["companies"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
