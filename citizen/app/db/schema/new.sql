CREATE TABLE attributes (
    id VARCHAR(36) PRIMARY KEY,

    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,

    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE attribute_values (
    id CHAR(36) PRIMARY KEY,   -- ✅ UUID optimized

    attribute_id CHAR(36) NOT NULL,
    value VARCHAR(100) NOT NULL,

    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(attribute_id, value),

    CONSTRAINT fk_attribute_values_attribute
        FOREIGN KEY (attribute_id) REFERENCES attributes(id)
);

CREATE INDEX idx_attribute_values_attribute_id 
ON attribute_values(attribute_id);

CREATE TABLE product_attributes (
    id CHAR(36) PRIMARY KEY,

    product_id CHAR(36) NOT NULL,
    attribute_id CHAR(36) NOT NULL,

    is_required BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,

    sort_order INT DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- ✅ Prevent duplicate active mappings
    UNIQUE(product_id, attribute_id, is_deleted),   

    CONSTRAINT fk_pa_product
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_pa_attribute
        FOREIGN KEY (attribute_id)
        REFERENCES attributes(id)
        ON DELETE CASCADE
);

-- ✅ Indexes (VERY IMPORTANT)
CREATE INDEX idx_pa_product ON product_attributes(product_id);
CREATE INDEX idx_pa_attribute ON product_attributes(attribute_id);


CREATE TABLE product_variant_combinations (
    id CHAR(36) PRIMARY KEY,

    product_id CHAR(36) NOT NULL,
    sku VARCHAR(100) UNIQUE,

    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_pvc_product
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE
);

-- ✅ Indexes
CREATE INDEX idx_pvc_product ON product_variant_combinations(product_id);
CREATE INDEX idx_pvc_sku ON product_variant_combinations(sku);

CREATE TABLE variant_attribute_values (
    id CHAR(36) PRIMARY KEY,

    variant_id CHAR(36) NOT NULL,
    attribute_id CHAR(36) NOT NULL,
    attribute_value_id CHAR(36) NOT NULL,

    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- ✅ IMPORTANT FIX (allow multiple values per attribute)
    UNIQUE(variant_id, attribute_id, attribute_value_id),

    CONSTRAINT fk_vav_variant
        FOREIGN KEY (variant_id)
        REFERENCES product_variant_combinations(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_vav_attr
        FOREIGN KEY (attribute_id)
        REFERENCES attributes(id),

    CONSTRAINT fk_vav_value
        FOREIGN KEY (attribute_value_id)
        REFERENCES attribute_values(id)
);

CREATE INDEX idx_vav_variant ON variant_attribute_values(variant_id);
CREATE INDEX idx_vav_attribute ON variant_attribute_values(attribute_id);
CREATE INDEX idx_vav_value ON variant_attribute_values(attribute_value_id);


CREATE TABLE variant_prices (
    id VARCHAR(36) PRIMARY KEY,

    variant_id VARCHAR(36) NOT NULL,

    min_qty INT NOT NULL,
    max_qty INT,
    custom_qty BOOLEAN DEFAULT FALSE,
    price DECIMAL(10,2) NOT NULL,
    weight DECIMAL(10,3) DEFAULT 0.0,
    length DECIMAL(10,2) DEFAULT 0,
    breadth DECIMAL(10,2) DEFAULT 0,
    height DECIMAL(10,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_price_variant
        FOREIGN KEY (variant_id)
        REFERENCES product_variant_combinations(id)
        ON DELETE CASCADE,

);