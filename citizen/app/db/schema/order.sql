-- =========================================================
-- USER ADDRESSES
-- =========================================================
CREATE TABLE user_addresses (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    address TEXT NOT NULL,
    address_type VARCHAR(50),
    landmark VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    phone VARCHAR(20),
    email VARCHAR(150),
    is_default BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_addresses_user 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =========================================================
-- ORDERS
-- =========================================================
CREATE TABLE orders (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    cart_id VARCHAR(36) NOT NULL,
    address_id VARCHAR(36),

    delivery_charge DECIMAL(10,2) DEFAULT 0,
    courier_id VARCHAR(50),
    courier_name VARCHAR(100),
    estimated_delivery_date DATE,

    delivery_type ENUM('hyperlocal', 'normal') NOT NULL DEFAULT 'normal',

    payment_method ENUM('COD','PREPAID') NOT NULL,
    payment_status ENUM('pending','paid') DEFAULT 'pending',

    status VARCHAR(50) DEFAULT 'pending',

    total_amount DECIMAL(10,2) NOT NULL,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_orders_user 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    CONSTRAINT fk_orders_cart 
        FOREIGN KEY (cart_id) REFERENCES carts(id) ON DELETE CASCADE,

    CONSTRAINT fk_orders_address 
        FOREIGN KEY (address_id) REFERENCES user_addresses(id) ON DELETE SET NULL
);


CREATE TABLE IF NOT EXISTS order_items (
    id CHAR(36) PRIMARY KEY,

    order_id CHAR(36) NOT NULL,
    cart_item_id CHAR(36) NULL,

    product_id CHAR(36) NOT NULL,
    variant_id CHAR(36) NOT NULL,
    variant_price_id CHAR(36) NULL,

    customize_qty INT NULL,

    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,

    selected_attributes JSON NOT NULL,
    discount_id CHAR(36) NULL,

    status VARCHAR(20) DEFAULT 'active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,

    CONSTRAINT fk_order_items_cartitem
        FOREIGN KEY (cart_item_id) REFERENCES cart_items(id) ON DELETE SET NULL,

    CONSTRAINT fk_order_items_product
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,

    CONSTRAINT fk_order_items_variant
        FOREIGN KEY (variant_id) REFERENCES product_variant_combinations(id) ON DELETE CASCADE,

    CONSTRAINT fk_order_items_variant_price
        FOREIGN KEY (variant_price_id) REFERENCES variant_prices(id) ON DELETE SET NULL
);


CREATE TABLE order_item_files (
    id CHAR(36) PRIMARY KEY,

    order_item_id CHAR(36) NOT NULL,  

    front_side_url VARCHAR(255) NULL,
    back_side_url VARCHAR(255) NULL,

    front_original_name VARCHAR(255),
    back_original_name VARCHAR(255),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_orderitemfile_orderitem
        FOREIGN KEY (order_item_id)
        REFERENCES order_items(id)
        ON DELETE CASCADE
);