CREATE TABLE user_order_design_files (
    id VARCHAR(36) PRIMARY KEY,

    order_id VARCHAR(36) NOT NULL,

    user_id VARCHAR(36) NOT NULL,

    file_name VARCHAR(255) NOT NULL,

    file_url VARCHAR(500) NOT NULL,

    file_type VARCHAR(50),

    file_size INT,

    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_user_order_design_files_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_user_order_design_files_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_user_order_design_files_order_id
ON user_order_design_files(order_id);

CREATE INDEX idx_user_order_design_files_user_id
ON user_order_design_files(user_id);