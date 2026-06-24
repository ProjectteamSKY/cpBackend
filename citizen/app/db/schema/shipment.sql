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
    pickup_token_number VARCHAR(255),
    pickup_scheduled_date DATETIME NULL,

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


CREATE TABLE shipment_webhook_logs (

    id VARCHAR(36) PRIMARY KEY,

    shipment_id VARCHAR(36) NOT NULL,

    awb_code VARCHAR(100) NOT NULL,

    event_status VARCHAR(100),

    payload JSON NOT NULL,

    created_at TIMESTAMP NOT NULL
    DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_shipment_webhook_logs_shipment
        FOREIGN KEY (shipment_id)
        REFERENCES shipments(id)
        ON DELETE CASCADE
);

