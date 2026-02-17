from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# Import all routers
from fastapi import FastAPI, APIRouter

from app.routes import user_routes
from app.routes import category_routes
from app.routes import subcategory_routes
from app.routes import cut_type_routes
from app.routes import finish_routes
from app.routes import paper_type_routes
from app.routes import product_image_routes
from app.routes import product_routes
from app.routes import product_variant_routes
from app.routes import sheet_template_routes
from app.routes import product_type_routes



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
api_router.include_router(category_routes.router, prefix="/auth", tags=["Auth"])
api_router.include_router(subcategory_routes.router, prefix="/auth", tags=["Auth"])
api_router.include_router(product_routes.router, prefix="/auth", tags=["Auth"])
api_router.include_router(product_type_routes.router, prefix="/auth", tags=["Auth"])
api_router.include_router(product_variant_routes.router, prefix="/auth", tags=["Auth"])
api_router.include_router(paper_type_routes.router, prefix="/auth", tags=["Auth"])
api_router.include_router(product_image_routes.router, prefix="/auth", tags=["Auth"])
api_router.include_router(finish_routes.router, prefix="/auth", tags=["Auth"])
api_router.include_router(cut_type_routes.router, prefix="/auth", tags=["Auth"])
api_router.include_router(sheet_template_routes.router, prefix="/auth", tags=["Auth"])



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
