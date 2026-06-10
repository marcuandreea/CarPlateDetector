from pathlib import Path
import sys

# Configuram path-ul absolut inainte de orice alt import
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(BASE_DIR.parent) not in sys.path:
    sys.path.insert(0, str(BASE_DIR.parent))

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware


# Initializare FastAPI app
app = FastAPI(
    title="Parking Management API",
    version="1.0.0",
    description="FastAPI backend pentru aplicatia de parcare",
)

# Middleware pentru CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from auth.rate_limiter import RateLimitMiddleware
from auth.api_key import require_api_key
from routes.health import router as health_router
from routes.users import router as users_router
from routes.parking import router as parking_router
from routes.subscriptions import router as subscriptions_router
from services.user_service import ensure_users_table_exists
from db.db import ensure_subscriptions_table_exists

# Middleware pentru rate limiting
app.add_middleware(
    RateLimitMiddleware,
    requests_per_window=60,
    window_seconds=60,
)

app.include_router(health_router)
app.include_router(users_router, dependencies=[Depends(require_api_key)])
app.include_router(parking_router, dependencies=[Depends(require_api_key)])
app.include_router(subscriptions_router, dependencies=[Depends(require_api_key)])


@app.on_event("startup")
def startup_event():
    ensure_users_table_exists()
    ensure_subscriptions_table_exists()
