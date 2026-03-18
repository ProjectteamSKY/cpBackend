-- =========================================================
-- CUSTOMER REVIEWS
-- =========================================================
CREATE TABLE customer_reviews (
    id VARCHAR(36) PRIMARY KEY,
    product_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    rating FLOAT NOT NULL,  -- 1.0 to 5.0
    comment TEXT,
    image_url VARCHAR(500),        -- optional review image
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- ---------------------------
    -- FOREIGN KEYS
    -- ---------------------------
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);