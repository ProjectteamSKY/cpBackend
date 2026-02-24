-- =========================================================
-- USER ADDRESSES TABLE
-- =========================================================
CREATE TABLE user_addresses (
    id VARCHAR(36) PRIMARY KEY,

    user_id VARCHAR(36) NOT NULL,

    address TEXT NOT NULL,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    phone VARCHAR(20),

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_user_addresses_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


-- =========================================================
-- ORDERS TABLE
-- =========================================================
CREATE TABLE orders (
    id VARCHAR(36) PRIMARY KEY,

    user_id VARCHAR(36),
    address_id VARCHAR(36),

    status VARCHAR(50) DEFAULT 'pending',

    total_amount FLOAT NOT NULL,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_orders_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_orders_address
        FOREIGN KEY (address_id)
        REFERENCES user_addresses(id)
        ON DELETE SET NULL
);


-- =========================================================
-- ORDER ITEMS TABLE
-- =========================================================
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,

    order_id VARCHAR(36),

    product_id VARCHAR(36),

    quantity INT NOT NULL,

    price FLOAT NOT NULL,

    total FLOAT NOT NULL,

    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_order_items_product
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE RESTRICT
);


-- =========================================================
-- INDEXES (Recommended for performance)
-- =========================================================

CREATE INDEX idx_user_addresses_user_id ON user_addresses(user_id);

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_address_id ON orders(address_id);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);