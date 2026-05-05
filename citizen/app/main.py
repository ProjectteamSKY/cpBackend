from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

# Import all routers
from fastapi import FastAPI, APIRouter
from fastapi.openapi.utils import get_openapi 

from app.routes import user_routes
from app.routes import user_profile_routes

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


from app.routes import attribute_router
from app.routes import attribute_value_router
from app.routes import product_attribute_router
from app.routes import product_variant_combinations_routes
from app.routes import variant_attribute_value_router
from app.routes import variant_price_router
from app.routes import transaction_routes




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
from app.routes import design_request_routes
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
#     print("🟢 Database initialized on startup - main.py:85")

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
        "/api/users/register",
        "/api/users/verify-otp",
        "/api/users/login",
        "/api/users/google-login",                  # Create user
        "/api/users/",
        "/api/users/",
        "/api/users/{user_id}",
        "/api/users/{user_id}",       # Get/Delete user
        
        # Role Management
        "/api/roles/create",
        "/api/role/list",                  # List roles
        "/api/role/{id}",
        "/api/role/{id}",
        "/api/role/{id}"
        "//api/role/{id}/activate",
        "/api/role/{id}/deactivate",
        
        # User-Role Assignment
        "/api/user_role/assign",
        "/api/user_role/list",    # Get user roles
        "/api/user_role/{id}",
        "/api/user_role/{id}",
        "/api/user_role/user/{user_id}",
        
        
        # Resource Management
        "/api/resource/create",              # Create/List resources
        "/api/resource/list", # Get/Update/Delete resource
        "/api/resource/{id}",
        "/api/resource/{id}",
        "/api/resource/{id}",
        "/api/resource/{id}/activate",
        "/api/resource/{id}/deactivate",

        
        # Permission Management
        "/api/permission/create",
        "/api/permission/list",            # List permissions
        "/api/permission/{id}",
        "/api/permission/{id}",
        "/api/permission/{id}",
        "/api/permission/{id}/activate",
        "/api/permission/{id}/deactivate",
        
        # Role-Permission Assignment
        "/api/role_permission/assign",
        "/api/role_permission/list", 
        "/api/role_permission/{id}",
        "/api/role_permission/{id}",
        "/api/role_permission/{role_id}",
        "/api/role_permission/role/{role_id}",
        "/api/role_permission/permission/{permission_id}",

        "/api/category/list",
        "/api/category/{id}",
        "/api/subcategory/list",
        "/api/subcategory/{id}",
        "/api/product/list",
        "/api/product/active/list",
        "/api/product/{id}",
        "/api/product_variant/list",
        "/api/product_variant/{id}",
        "/api/product_variant/product/{product_id}",
        "/api/product_variant/{variant_id}/weight",
        "/api/product_discount/list",
        "/api/product_discount/list/active",
        "/api/product_discount/{id}",
        "/api/product_discount/product/{product_id}",
        "/api/product_discount/by_date_range",
        "/api/product_discount/active/last5",
        "/api/product_variant_price/list",
        "/api/product_variant_price/{id}",
        "/api/product_variant_price/{id}",
        "/api/product_variant_price/variant/{variant_id}/price-weight/{price_id}",
        "/api/productsetup/products/{product_id}",
        "/api/productsetup/list",
        "/api/paper_type/list",
        "/api/paper_type/list/active",
        "/api/paper_type/{id}",
        "/api/print_type/list",
        "/api/print_type/list/active",
        "/api/print_type/{id}",
        "/api/cut_type/list",
        "/api/cut_type/list/active",
        "/api/cut_type/{id}",
        "/api/size/list",
        "/api/size/list/active",
        "/api/size/{id}",
        "/api/cart/",
        "/api/cart/",
        "/api/cart/{id}",
        "/api/cart/{id}",
        "/api/cart/{id}",
        "/api/cart/user/{user_id}",
        "/api/cartitems/",
        "/api/cartitems/with-files",
        "/api/cartitems/cart/{cart_id}",
        "/api/cartitems/user/{user_id}",
        "/api/cartitems/{id}",
        "/api/cartitems/{id}",
        "/api/cartitems/{id}",
        "/api/user_address/create",
        "/api/user_address/list/{user_id}",
        "/api/user_address/{id}",
        "/api/user_address/update/{id}",
        "/api/user_address/update/{id}",
        "/api/orders_routes/checkout"
        "/api/orders_routes/tracking"
        "/api/orders_routes/total"
        "/api/orders_routes/total/{user_id}"
        "/api/orders_routes/summary",
        "/api/orders_routes/{order_id}",
        "/api/orders_routes/list/{user_id}",
        "/api/shipping/create-order/{order_id}",
        "/api/shipping/couriers/{order_id}"
        "/api/shipping/serviceavailability",
        "/api/wishlist_routes/create",
       " /api/wishlist_routes/list"
        "/api/wishlist_routes/{id}",
        "/api/wishlist_routes/{id}",
        "/api/wishlist_routes/user/{user_id}",
        "/api/bank/qr-generate",
        "/api/bank/qr-image",
        "/api/bank/api/upi-callback",
        "/api/review/create",
        "/api/review/{id}",
        "/api/review/{id}",
        "/api/review/{id}",
        "/api/review/list",
        "/api/review/{id}/activate",
        "/api/review/{id}/deactivate",
        "/api/review/product/{product_id}/latest",
        "/api/faq/create",
        "/api/faq/list",
       " /api/faq/product",
        "/api/faq/category/{category_id}",
        "/api/faq/{id}",
        "/api/faq/{id}",
        "/api/design_request/create",
        "/api/design_request/{id}/update",
        "/api/design_request/{id}/status",
        "/api/design_request/designedimage/{id}/approve",
        "/api/design_request/designedimage/{id}/reject",
        "/api/design_request/list",
        "/api/design_request/{id}",
        "/api/design_request/{id}",
        "/api/design_request/user/{user_id}",
        "/api/product/search",
        "/api/product/category/search",
        "/api/product/subcategory/search",

        # attribute and attribute value and related endpoints
        "/api/attribute/create",
        "/api/attribute/list",
        "/api/attribute/{id}",
        "/api/attribute/{id}",
        "/api/attribute/{id}/activate",
        "/api/attribute/{id}/deactivate",
        "/api/attribute_value/create",
        "/api/attribute_value/list",
        "/api/attribute_value/attribute/{attribute_id}",
        "/api/attribute_value/{id}",
        "/api/attribute_value/{id}",
        "/api/attribute_value/{id}/activate",
        "/api/attribute_value/{id}/deactivate",
        #product attribute and variant attribute value endpoints
        "/api/product_attribute/create",
        "/api/product_attribute/list",
        "/api/product_attribute/product/{product_id}",
        "/api/product_attribute/{id}",
        "/api/product_attribute/{id}",
        "/api/product_variant_combinations/create",
        "/api/product_variant_combinations/list",
        "/api/product_variant_combinations/product/{product_id}",
        "/api/product_variant_combinations/{id}",
        "/api/product_variant_combinations/{id}",
        "/api/product_variant_combinations/{id}/activate",
        "/api/product_variant_combinations/{id}/deactivate",
        "/api/variant_attribute_value/create",
        "/api/variant_attribute_value/list",
        "/api/variant_attribute_value/variant/{variant_id}",
        "/api/variant_attribute_value/update",
        "/api/variant_attribute_value/{id}",
        "/api/variant_attribute_value/{id}",
        "/api/variant_attribute_value/{id}/activate",
        "/api/variant_attribute_value/{id}/deactivate",
        "/api/variant_attribute_value/product/{product_id}/full-details",
        "/api/variant_price/create",
        "/api/variant_price/list",
        "/api/variant_price/variant/{variant_id}",
        "/api/variant_price/{id}",
        "/api/variant_price/{id}",
        "/api/variant_price/{id}/activate",
        "/api/variant_price/{id}/deactivate",
        "/api/variant_attribute_value/total",



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


api_router.include_router(resource_routes.router,prefix="/resource", tags=["resource"])
api_router.include_router(user_routes.router)
api_router.include_router(role_routes.router,prefix="/role", tags=["role"])
api_router.include_router(user_role_routes.router,prefix="/user_role", tags=["user_role"])
api_router.include_router(permission_routes.router,prefix="/permission", tags=["permission"])
api_router.include_router(role_permission_routes.router,prefix="/role_permission", tags=["role_permission"])
api_router.include_router(user_profile_routes.router,prefix="/user-profile", tags=["User Profile"])

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

api_router.include_router(attribute_router.router, prefix="/attribute", tags=["attribute"])
api_router.include_router(attribute_value_router.router, prefix="/attribute_value", tags=["attribute_value"])
api_router.include_router(product_attribute_router.router, prefix="/product_attribute", tags=["product_attribute"])
api_router.include_router(product_variant_combinations_routes.router, prefix="/product_variant_combinations", tags=["product_variant_combinations"])
api_router.include_router(variant_attribute_value_router.router, prefix="/variant_attribute_value", tags=["variant_attribute_value"])
api_router.include_router(variant_price_router.router, prefix="/variant_price", tags=["variant_price"])



api_router.include_router(cart_routes.router, prefix="/cart", tags=["cart"])
api_router.include_router(cart_item_routes.router, prefix="/cartitems", tags=["cartitems"])

api_router.include_router(user_addresses_routes.router, prefix="/user_address", tags=["user_addresses"])
api_router.include_router(orders_routes.router, prefix="/orders_routes", tags=["orders_routes"])
api_router.include_router(order_items_routes.router, prefix="/order_items_routes", tags=["order_items_routes"])

api_router.include_router(shipping_router.router, prefix="/shipping", tags=["Shipping"])
# api_router.include_router(payment_routes.router, prefix="/payment_routes", tags=["payment_routes"])
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
api_router.include_router(design_request_routes.router, prefix="/design_request", tags=["design_request"])
api_router.include_router(transaction_routes.router, prefix="/transactions", tags=["Transactions"])


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
