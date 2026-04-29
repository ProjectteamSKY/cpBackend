CREATE TABLE bank_oauth_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,

    bank_name VARCHAR(100) DEFAULT 'canara',

    access_token TEXT,
    refresh_token TEXT,

    expires_at DATETIME,
    refresh_expires_at DATETIME,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY unique_user_bank (user_id, bank_name)
);  