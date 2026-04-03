CREATE TABLE design_requests (
    id VARCHAR(50) PRIMARY KEY,

    user_id VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100),

    product_id VARCHAR(50),
    product_name VARCHAR(150),

    variant_id VARCHAR(50),
    product_variant_price_id VARCHAR(50),

    design_notes TEXT,
    logo_images JSON,
    designed_images JSON,

    status VARCHAR(30) DEFAULT 'NEW',
    is_approved BOOLEAN DEFAULT FALSE,
    design_price DECIMAL(10,2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_design_requests_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_design_requests_product
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_design_requests_variant
        FOREIGN KEY (variant_id)
        REFERENCES product_variants(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_design_requests_variant_price
        FOREIGN KEY (product_variant_price_id)
        REFERENCES product_variant_prices(id)
        ON DELETE SET NULL
);