CREATE TABLE carts (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    status VARCHAR(20) DEFAULT 'active', -- active, ordered, cancelled
    total_amount FLOAT DEFAULT 0,
    total_discount FLOAT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE cart_items (
    id VARCHAR(36) PRIMARY KEY,
    cart_id VARCHAR(36) NOT NULL,
    product_id VARCHAR(36) NOT NULL,
    variant_id VARCHAR(36) NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price FLOAT NOT NULL,

    discount_id VARCHAR(36) NULL,   
    total_price FLOAT NOT NULL,
    selected_options JSON NULL,
    status VARCHAR(20) DEFAULT 'active', -- active, ordered, cancelled

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    -- Foreign keys
    CONSTRAINT fk_cartitem_cart FOREIGN KEY (cart_id) REFERENCES carts(id) ON DELETE CASCADE,
    CONSTRAINT fk_cartitem_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    CONSTRAINT fk_cartitem_variant FOREIGN KEY (variant_id) REFERENCES product_variants(id) ON DELETE CASCADE,
    CONSTRAINT fk_cartitem_discount FOREIGN KEY (discount_id) REFERENCES product_discounts(id) ON DELETE SET NULL
);

ALTER TABLE cart_items
ADD CONSTRAINT uq_cart_variant UNIQUE(cart_id, variant_id);


CREATE TABLE cart_item_files (
    id VARCHAR(36) PRIMARY KEY,
    cart_item_id VARCHAR(36) NOT NULL,

    front_side_url VARCHAR(255) NULL,
    back_side_url VARCHAR(255) NULL,

    front_original_name VARCHAR(255),
    back_original_name VARCHAR(255),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_cartitemfile_cartitem 
    FOREIGN KEY (cart_item_id) 
    REFERENCES cart_items(id) 
    ON DELETE CASCADE
);  