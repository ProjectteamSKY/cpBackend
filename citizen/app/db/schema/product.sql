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
-- PAPER TYPE
-- =========================================================
CREATE TABLE paper_types (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- PRINT TYPE
-- =========================================================
CREATE TABLE print_types (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- CUT TYPE
-- =========================================================
CREATE TABLE cut_types (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);





-- =========================================================
-- SIZE
-- =========================================================
CREATE TABLE sizes (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    width FLOAT NOT NULL,
    height FLOAT NOT NULL,
    unit VARCHAR(10) DEFAULT 'mm',
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_size_dimensions UNIQUE (width, height)
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


-- =========================================================
-- PRODUCT VARIANT
-- =========================================================
CREATE TABLE product_variants (
    id VARCHAR(36) PRIMARY KEY,

    product_id VARCHAR(36) NOT NULL,
    size_id VARCHAR(36) NOT NULL,

    paper_type_id VARCHAR(36),
    print_type_id VARCHAR(36),
    cut_type_id VARCHAR(36),

    sides INT,
    two_side_cut BOOLEAN DEFAULT FALSE,
    four_side_cut BOOLEAN DEFAULT FALSE,

    orientation VARCHAR(20) DEFAULT 'Portrait',

    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_variant_product
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_variant_size
        FOREIGN KEY (size_id)
        REFERENCES sizes(id),

    CONSTRAINT fk_variant_paper
        FOREIGN KEY (paper_type_id)
        REFERENCES paper_types(id),

    CONSTRAINT fk_variant_print
        FOREIGN KEY (print_type_id)
        REFERENCES print_types(id),

    CONSTRAINT fk_variant_cut
        FOREIGN KEY (cut_type_id)
        REFERENCES cut_types(id)

);

-- =====================================================
-- PRODUCT DISCOUNT
-- =====================================================
CREATE TABLE product_discounts (
    id VARCHAR(36) PRIMARY KEY,

    product_id VARCHAR(36) NULL,

    description TEXT,

    discount VARCHAR(10) NOT NULL DEFAULT '0%',  

    start_date DATETIME NOT NULL,

    end_date DATETIME NOT NULL,

    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_discounts_product
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE
);


-- =========================================================
-- PRODUCT VARIANT PRICES (with optional discount FK)
-- =========================================================
CREATE TABLE product_variant_prices (
    id VARCHAR(36) PRIMARY KEY,

    variant_id VARCHAR(36) NOT NULL,
    discount_id VARCHAR(36) NULL,  -- optional FK to product_discounts

    min_qty INT NOT NULL,
    
    price FLOAT NOT NULL,

    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- FK to product_variant
    CONSTRAINT fk_variantprice_variant
        FOREIGN KEY (variant_id)
        REFERENCES product_variants(id)
        ON DELETE CASCADE,

    -- FK to product_discounts
    CONSTRAINT fk_variantprice_discount
        FOREIGN KEY (discount_id)
        REFERENCES product_discounts(id)
        ON DELETE SET NULL,

    -- Unique constraint for quantity ranges per variant
    CONSTRAINT uq_variant_qty UNIQUE (variant_id, min_qty)
);