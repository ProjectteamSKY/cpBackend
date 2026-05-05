CREATE TABLE shipments (
    id VARCHAR(36) PRIMARY KEY,

    order_id VARCHAR(36) NOT NULL,

    shiprocket_order_id BIGINT,
    shipment_id BIGINT,

    awb_code VARCHAR(100) UNIQUE,

    courier_id VARCHAR(36),
    courier_name VARCHAR(255),

    freight_charges DECIMAL(10,2),

    tracking_url TEXT,
    manifest_url TEXT,
    pickup_status VARCHAR(100),

    current_status VARCHAR(100) DEFAULT 'CREATED',

    delivered_at TIMESTAMP NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_shipments_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE CASCADE
);


CREATE INDEX idx_shipments_awb ON shipments(awb_code);
CREATE INDEX idx_shipments_order_id ON shipments(order_id);
CREATE INDEX idx_shipments_status ON shipments(current_status);

