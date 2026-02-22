import sys
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlmodel import Session

from app.services.seeders import bank_extern_create
from app.settings.schemas import Transaction
from app.settings.database import create_db_and_tables, get_session, engine
from routes.transactions import router as transactions_router
from routes.beneficiaires import router as beneficiaires_router
from routes.auth import router as authentification_router
from routes.bank_account import router as bank_account_router
from routes.users import router as users_router
from fastapi.middleware.cors import CORSMiddleware
from app.settings.config import SECRET_KEY, IS_PROD

# ── Rate limiting ────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

app = FastAPI(redirect_slashes=False)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── /health — public, registered BEFORE auth middleware ──────────────────────
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

# ── Security headers middleware ───────────────────────────────────────────────
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if IS_PROD:
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
    return response

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://banque-republic.micdev.fr", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(authentification_router)
app.include_router(transactions_router)
app.include_router(bank_account_router)
app.include_router(beneficiaires_router)
app.include_router(users_router)

# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    if not SECRET_KEY:
        print("FATAL: SECRET_KEY manquant", file=sys.stderr)
        sys.exit(1)
    session = next(get_session())
    create_db_and_tables()
    bank_extern_create(session)

# ── Global error handler ──────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if not IS_PROD:
        import traceback
        traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"error": "Erreur interne du serveur"},
    )
