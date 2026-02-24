CREATE TABLE wishlists (
    id VARCHAR(36) PRIMARY KEY,

    user_id VARCHAR(36) NOT NULL,

    product_id VARCHAR(36) NOT NULL,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_wishlist_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_wishlist_product
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_user_product UNIQUE (user_id, product_id)
);

CREATE INDEX idx_wishlist_user ON wishlists(user_id);
CREATE INDEX idx_wishlist_product ON wishlists(product_id);