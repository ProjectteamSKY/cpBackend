from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

# Import all routers
from fastapi import FastAPI, APIRouter
from fastapi.openapi.utils import get_openapi 

from app.routes import user_routes
from app.routes import category_routes
from app.routes import subcategory_routes
from app.routes import cut_type_routes
from app.routes import paper_type_routes
from app.routes import print_type_routes
from app.routes import size_routes


from app.routes import product_routes
from app.routes import product_variant_routes
from app.routes import product_discount_routes

from app.routes import product_variant_price_routes
from app.routes import productsetup_routes

from app.routes import cart_routes
from app.routes import cart_item_routes
from app.routes import user_addresses_routes
from app.routes import orders_routes
from app.routes import order_items_routes
from app.routes import shipping_router
from app.routes import payment_routes
from app.routes import wishlist_routes
from app.routes.bank import vpa_routes
from app.routes.bank import vpa_inquiry_routes
from app.routes.bank import vpa_deactivation_routes
from app.routes.bank import vpa_deactivation_inquiry_routes
from app.routes.bank import verify_vpa_routes
from app.routes.bank import qr_generation_routes
from app.routes.bank import transaction_status_routes
from app.routes.bank import transaction_status_extid_routes
from app.routes.bank import qr_callback_routes
from app.routes.bank import qr_statement_routes
from app.routes.bank import oauth_routes
from app.routes import review_routes
from app.routes import faq_router

from app.routes import customer_erp





from fastapi.staticfiles import StaticFiles

from app.routes import permission_routes, resource_routes, role_permission_routes, role_routes, user_role_routes
from app.core.auth_middleware import AuthMiddleware
from app.core.rbac_middleware import RBACMiddleware
# from app.core.init_db import init_db  # import the function, not the module



app = FastAPI(
    title="E-Commerce API",
    description="FastAPI backend for e-commerce with async SQLAlchemy ORM",
    version="1.0.0"
)


# @app.on_event("startup")
# async def on_startup():
#     await init_db()
#     print("🟢 Database initialized on startup - main.py:69")

# # -------------------------
# CORS middleware
# -------------------------

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="E-Commerce API",
        version="1.0.0",
        description="FastAPI backend for e-commerce with async SQLAlchemy ORM",
        routes=app.routes,
    )
    

    openapi_schema["openapi"] = "3.0.3"

    # Ensure components exists
    openapi_schema.setdefault("components", {})

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "Token",
            "description": "Enter your bearer token from POST /users/login"
        }
    }
    
    # Apply security globally
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    # ============ PUBLIC ENDPOINTS (NO AUTH REQUIRED) ============
    public_endpoints = [
        # Root
        "/",
        
        # User Management
        "/api/users/login",
        "/api/users/",                  # Create user
        "/api/users/{user_id}",         # Get/Delete user
        
        # Role Management
        "/api/roles/create",
        "/api/roles/",                  # List roles
        "/api/roles/delete",
        
        # User-Role Assignment
        "/api/user-roles/assign",
        "/api/user-roles/{user_id}",    # Get user roles
        "/api/user-roles/remove",
        "/api/user-roles/users-withroles",
        
        
        # Resource Management
        "/api/resources/",              # Create/List resources
        "/api/resources/{resource_id}", # Get/Update/Delete resource
        
        # Permission Management
        "/api/permissions/create",
        "/api/permissions/",            # List permissions
        "/api/permissions/delete",
        
        # Role-Permission Assignment
        "/api/role-permissions/assign",
        "/api/role-permissions/{role_id}", 
        "/api/role-permissions/remove",
        "/api/clubs/{club_id}/assign-player",
        "/api/clubs/{club_id}/assign-admin",

        # Customer Api - ERP system
        "/api/customers/search",
        "/api/customers/{customer_code}",
        "/api/customers/{customer_code}/history", 
    ]
    
    # Remove security for public endpoints
    for path, methods in openapi_schema["paths"].items():
        if path in public_endpoints:
            for method in methods.values():
                if isinstance(method, dict):
                    method["security"] = []
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Allow frontend access (adjust origin in production)
# 1️⃣ CORS first
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",  # allows all origins
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://citizenprints.s3-website.ap-south-1.amazonaws.com",
        "http://citizenprints-erp.s3-website-ap-southeast-2.amazonaws.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2️⃣ Then your RBAC and Auth
app.add_middleware(RBACMiddleware)
app.add_middleware(AuthMiddleware)

api_router = APIRouter(prefix="/api")


api_router.include_router(resource_routes.router)
api_router.include_router(user_routes.router)
api_router.include_router(role_routes.router)
api_router.include_router(user_role_routes.router)
api_router.include_router(permission_routes.router)
api_router.include_router(role_permission_routes.router)
# -------------------------
# Include Routers
# -------------------------
api_router.include_router(category_routes.router, prefix="/category", tags=["category"])
api_router.include_router(subcategory_routes.router, prefix="/subcategory", tags=["subcategory"])
api_router.include_router(product_routes.router, prefix="/product", tags=["product"])
api_router.include_router(product_variant_routes.router, prefix="/product_variant", tags=["product_variant"])
api_router.include_router(product_discount_routes.router, prefix="/product_discount", tags=["product_discount_routes"])


api_router.include_router(product_variant_price_routes.router, prefix="/product_variant_price", tags=["Product Variant Prices"])

api_router.include_router(productsetup_routes.router, prefix="/productsetup", tags=["product setup"])

api_router.include_router(paper_type_routes.router, prefix="/paper_type", tags=["paper_type"])
api_router.include_router(print_type_routes.router, prefix="/print_type", tags=["print_type"])

api_router.include_router(cut_type_routes.router, prefix="/cut_type", tags=["cut_type"])
api_router.include_router(cut_type_routes.router, prefix="/cut_type", tags=["cut_type"])
api_router.include_router(size_routes.router, prefix="/size", tags=["size"])
api_router.include_router(cart_routes.router, prefix="/cart", tags=["cart"])
api_router.include_router(cart_item_routes.router, prefix="/cartitems", tags=["cartitems"])

api_router.include_router(user_addresses_routes.router, prefix="/user_address", tags=["user_addresses"])
api_router.include_router(orders_routes.router, prefix="/orders_routes", tags=["orders_routes"])
api_router.include_router(order_items_routes.router, prefix="/order_items_routes", tags=["order_items_routes"])

api_router.include_router(shipping_router.router, prefix="/shipping", tags=["Shipping"])
api_router.include_router(payment_routes.router, prefix="/payment_routes", tags=["payment_routes"])
api_router.include_router(wishlist_routes.router, prefix="/wishlist_routes", tags=["wishlist_routes"])

api_router.include_router(vpa_routes.router,prefix="/bank", tags=["Bank APIs"])
api_router.include_router(vpa_inquiry_routes.router,prefix="/bank", tags=["Bank APIs"])
api_router.include_router(vpa_deactivation_routes.router, prefix="/bank", tags=["Bank APIs"])
api_router.include_router(vpa_deactivation_inquiry_routes.router, prefix="/bank", tags=["Bank APIs"])
api_router.include_router(verify_vpa_routes.router, prefix="/bank", tags=["Bank APIs"])
api_router.include_router(qr_generation_routes.router, prefix="/bank", tags=["Bank APIs"])
api_router.include_router(transaction_status_routes.router, prefix="/bank", tags=["Bank APIs"])
api_router.include_router(transaction_status_extid_routes.router, prefix="/bank", tags=["Bank APIs"])
api_router.include_router(qr_callback_routes.router, prefix="/bank", tags=["Bank APIs"])
api_router.include_router(qr_statement_routes.router, prefix="/bank", tags=["Bank APIs"])
api_router.include_router(oauth_routes.router, prefix="/bank", tags=["Bank OAuth"])
api_router.include_router(review_routes.router, prefix="/review", tags=["review"])
api_router.include_router(faq_router.router, prefix="/faq", tags=["faq"])

# Include ERP customer routes
api_router.include_router(customer_erp.router, prefix="", tags=["Customer ERP"])

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

# ------------------------
# Lambda test route
# ------------------------
@app.get("/")
def root():
    return {"message": "Hello from Lambda 🚀"}

handler = Mangum(app)
