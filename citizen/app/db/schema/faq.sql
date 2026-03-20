CREATE TABLE faqs (
    id CHAR(36) PRIMARY KEY,

    question TEXT NOT NULL,
    answer TEXT NOT NULL,

    type ENUM('category', 'product') NOT NULL,

    category_id CHAR(36) NULL,
    product_id CHAR(36) NULL,

    is_active BOOLEAN DEFAULT TRUE,
    sort_order INT DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- 🔗 Foreign Keys
    CONSTRAINT fk_faq_category
        FOREIGN KEY (category_id)
        REFERENCES categories(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_faq_product   
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE
);


CREATE INDEX idx_faq_category_id ON faqs(category_id);
CREATE INDEX idx_faq_product_id ON faqs(product_id);
CREATE INDEX idx_faq_type ON faqs(type);
CREATE INDEX idx_faq_active ON faqs(is_active);
CREATE INDEX idx_faq_sort_order ON faqs(sort_order);