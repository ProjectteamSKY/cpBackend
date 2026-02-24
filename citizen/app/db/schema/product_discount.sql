-- =====================================================
-- PRODUCT 
-- =====================================================


CREATE TABLE product_discounts (
    id VARCHAR(36) PRIMARY KEY,

    product_id VARCHAR(36) NULL,

    description TEXT,

    discount_type VARCHAR(20) DEFAULT 'percentage',

    start_date DATETIME NOT NULL,

    end_date DATETIME NOT NULL,

    is_active BOOLEAN DEFAULT TRUE,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_discounts_product
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE
);