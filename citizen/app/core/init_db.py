import asyncio
from app.core.database import engine
from app.db.models.user_model import (
    Base,
    User,
    UserProfile,
    UserToken,
    Role,
    Resource,
    Permission,
    UserRole,
    RolePermission
)
from app.db.models.product_models import (
    Category,
    SubCategory,
    ProductType,
    PaperType,
    Finish,
    CutType,
    Product,
    ProductVariant,
    ProductImage,
    SheetTemplate,
)

from app.db.models.discounts_models import (
   Discount
)

from app.db.models.order_models import (
    OrderAddress,              
    Order,                    
    OrderItem,                 
    ShipRocketAuth,            
    ShipRocketPickupLocation, 
    ShipRocketCourier,        
    ShipRocketCourierRate,     
    ShipRocketServiceability,  
    ShipRocketOrder,           
    ShipRocketShipment,        
    ShipRocketInvoice,         
    ShipRocketLabel,           
    ShipRocketManifest,        
    ShipRocketTracking,        
    ShipRocketNDR,             
    ShipRocketReturn,          
    ShipRocketCODSettlement    
)

from app.db.models.order_files_models import (
    OrderFile,                
)

from app.db.models.payments_models import (
    Payment,
    Refund,
    PaymentMethod,
    BankAccount,
    Payout
)


from app.db.models.invoice_models import (
   Invoice
)

from app.db.models.wishlist_model import (
   Wishlist
)

async def init_db():
    async with engine.begin() as conn:
        print("Creating tables... - init_db.py:74")

        # Run sync create_all inside async connection
        #  Order matters due to foreign keys:
        # 1. Users first
        # 2. Roles and permissions
        # 3. Products, categories, subcategories, variants, images
        await conn.run_sync(Base.metadata.create_all)

        print("All tables created successfully! - init_db.py:83")

if __name__ == "__main__":
    asyncio.run(init_db())
