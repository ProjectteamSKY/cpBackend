CREATE TABLE design_requests (
    id CHAR(36) PRIMARY KEY,

    user_id CHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100),

    product_id CHAR(36),
    product_name VARCHAR(150),

    variant_id CHAR(36) NOT NULL,

    -- ✅ FIX 1: Match type EXACTLY with variant_prices.id
    variant_price_id VARCHAR(36) NULL,

    selected_attributes JSON NOT NULL,
    design_notes TEXT,
    logo_images JSON,
    designed_images JSON,
    revision_count INT DEFAULT 0,
    rejection_reason TEXT,
    status VARCHAR(30) DEFAULT 'NEW',
    is_approved BOOLEAN DEFAULT FALSE,
    design_price DECIMAL(10,2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- -------------------------
    -- ✅ CONSTRAINTS (NAMED)
    -- -------------------------
    CONSTRAINT fk_dr_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_dr_product
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_dr_variant
        FOREIGN KEY (variant_id)
        REFERENCES product_variant_combinations(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_dr_variant_price
        FOREIGN KEY (variant_price_id)
        REFERENCES variant_prices(id)
        ON DELETE SET NULL
);