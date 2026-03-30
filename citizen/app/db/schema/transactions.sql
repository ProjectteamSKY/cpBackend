CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    ext_transaction_id VARCHAR(50) UNIQUE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    vpa VARCHAR(100),
    status VARCHAR(20) DEFAULT 'PENDING',
    qr_string TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMP NULL
);