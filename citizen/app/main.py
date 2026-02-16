from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# Import all routers
from fastapi import FastAPI, APIRouter

from app.routes import user_routes


app = FastAPI(
    title="E-Commerce API",
    description="FastAPI backend for e-commerce with async SQLAlchemy ORM",
    version="1.0.0"
)

# -------------------------
# CORS middleware
# -------------------------
# Allow frontend access (adjust origin in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")

# -------------------------
# Include Routers
# -------------------------
api_router.include_router(user_routes.router, prefix="/auth", tags=["Auth"])

app.include_router(api_router)

# -------------------------
# Root endpoint
# -------------------------
@app.get("/", tags=["Root"])
async def root():
    return {"message": "E-Commerce API is running"}

# -------------------------
# Optional: Health check
# -------------------------
@app.get("/health", tags=["Root"])
async def health_check():
    return {"status": "OK"}
