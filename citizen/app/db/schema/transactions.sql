CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) NULL,
    ext_transaction_id VARCHAR(50) NOT NULL UNIQUE,
    amount NUMERIC(10,2) NOT NULL CHECK (amount > 0),
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'SUCCESS', 'FAILED')),
    rrn VARCHAR(20) NULL,                 -- Bank reference number
    txn_id VARCHAR(100) NULL,             -- UPI txnId
    customer_vpa VARCHAR(100) NULL,
    qr_string TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMP NULL
);