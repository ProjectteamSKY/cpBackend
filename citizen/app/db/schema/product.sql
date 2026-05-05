-- =========================================================
-- CATEGORY
-- =========================================================
CREATE TABLE categories (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- SUBCATEGORY
-- =========================================================
CREATE TABLE subcategories (
    id VARCHAR(36) PRIMARY KEY,
    category_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    images JSON,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_subcategory_category
        FOREIGN KEY (category_id)
        REFERENCES categories(id)
        ON DELETE CASCADE
);

-- =========================================================
-- PRODUCT
-- =========================================================
CREATE TABLE products (
    id VARCHAR(36) PRIMARY KEY,

    category_id VARCHAR(36),
    subcategory_id VARCHAR(36),

    name VARCHAR(255) NOT NULL,
    description TEXT,
    sku VARCHAR(50) UNIQUE,
    min_order_qty INT DEFAULT 100,
    max_order_qty INT,

    images JSON,
    related_images JSON,

    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_product_category
        FOREIGN KEY (category_id)
        REFERENCES categories(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_product_subcategory
        FOREIGN KEY (subcategory_id)
        REFERENCES subcategories(id)
        ON DELETE SET NULL
);

-- =====================================================
-- PRODUCT DISCOUNT
-- =====================================================
CREATE TABLE product_discounts (
    id VARCHAR(36) PRIMARY KEY,
    product_id VARCHAR(36) NULL,
    title VARCHAR(100) NULL,              -- Banner title
    description TEXT,
    discount VARCHAR(10) NOT NULL DEFAULT '0%',
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    banner_image_url VARCHAR(255) NULL,   -- Banner image URL
    cta_text VARCHAR(50) NULL,            -- Button text
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_discounts_product
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE
);  




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