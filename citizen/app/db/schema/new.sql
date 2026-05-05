CREATE TABLE attributes (
    id VARCHAR(36) PRIMARY KEY,

    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,

    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE attribute_values (
    id CHAR(36) PRIMARY KEY,   -- ✅ UUID optimized

    attribute_id CHAR(36) NOT NULL,
    value VARCHAR(100) NOT NULL,

    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(attribute_id, value),

    CONSTRAINT fk_attribute_values_attribute
        FOREIGN KEY (attribute_id) REFERENCES attributes(id)
);

CREATE INDEX idx_attribute_values_attribute_id 
ON attribute_values(attribute_id);
