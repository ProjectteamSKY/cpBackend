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
from app.routes import print_type_routes
from app.routes import size_routes


from app.routes import product_image_routes
from app.routes import product_routes
from app.routes import product_variant_routes
from app.routes import product_discount_routes

from app.routes import product_variant_price_routes
from app.routes import productsetup_routes

from app.routes import sheet_template_routes
from app.routes import product_type_routes
from app.routes import custom_shape_routes
from fastapi.staticfiles import StaticFiles

# from app.core.init_db import init_db  # import the function, not the module



app = FastAPI(
    title="E-Commerce API",
    description="FastAPI backend for e-commerce with async SQLAlchemy ORM",
    version="1.0.0"
)


# @app.on_event("startup")
# async def on_startup():
#     await init_db()
#     print("🟢 Database initialized on startup - main.py:42")

# # -------------------------
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
# api_router.include_router(user_routes.router, prefix="/auth", tags=["Auth"])
api_router.include_router(category_routes.router, prefix="/category", tags=["category"])
api_router.include_router(subcategory_routes.router, prefix="/subcategory", tags=["subcategory"])
api_router.include_router(product_routes.router, prefix="/product", tags=["product"])
# api_router.include_router(product_type_routes.router, prefix="/product_type", tags=["product_type"])
api_router.include_router(product_variant_routes.router, prefix="/product_variant", tags=["product_variant"])
api_router.include_router(product_discount_routes.router, prefix="/product_discount", tags=["product_discount_routes"])


api_router.include_router(product_variant_price_routes.router, prefix="/product-variant-prices", tags=["Product Variant Prices"])

api_router.include_router(productsetup_routes.router, prefix="/productsetup", tags=["product setup"])

api_router.include_router(paper_type_routes.router, prefix="/paper_type", tags=["paper_type"])
api_router.include_router(print_type_routes.router, prefix="/print_type", tags=["print_type"])

# api_router.include_router(custom_shape_routes.router,prefix="/custom-shapes", tags=["CustomShapes"])

# api_router.include_router(product_image_routes.router, prefix="/product_image", tags=["product_image"])
# api_router.include_router(product_image_routes.router, prefix="/product_related_image", tags=["product_related_image"])


# # api_router.include_router(finish_routes.router, prefix="/finish", tags=["finish"])
api_router.include_router(cut_type_routes.router, prefix="/cut_type", tags=["cut_type"])
api_router.include_router(cut_type_routes.router, prefix="/cut_type", tags=["cut_type"])
api_router.include_router(size_routes.router, prefix="/size", tags=["size"])


# api_router.include_router(sheet_template_routes.router, prefix="/sheet_template", tags=["sheet_template"])


app.mount("/media", StaticFiles(directory="media"), name="media")

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
