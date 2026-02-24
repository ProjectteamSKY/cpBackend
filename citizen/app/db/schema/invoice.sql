CREATE TABLE invoices (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),

    order_id VARCHAR(36) NOT NULL,

    invoice_number VARCHAR(100) NOT NULL UNIQUE,

    invoice_date DATETIME DEFAULT CURRENT_TIMESTAMP,

    total_amount FLOAT NOT NULL,

    gst_amount FLOAT NOT NULL,

    final_amount FLOAT NOT NULL,

    pdf_url VARCHAR(500),

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_invoices_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_invoices_order_id ON invoices(order_id);