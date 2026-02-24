-- =====================================================
-- USERS TABLE
-- =====================================================
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    full_name VARCHAR(250) NOT NULL,
    email VARCHAR(200) NOT NULL UNIQUE,
    contact VARCHAR(30),
    password_hash VARCHAR(255) NOT NULL,
    bearer_token TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_email (email)
);


-- =====================================================
-- USER PROFILES TABLE (One-to-One with users)
-- =====================================================
CREATE TABLE user_profiles (
    user_id VARCHAR(36) PRIMARY KEY,
    profile_picture VARCHAR(500),
    phone_number VARCHAR(30),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    date_of_birth DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_user_profiles_user
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);


-- =====================================================
-- USER TOKENS TABLE
-- =====================================================
CREATE TABLE user_tokens (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    token TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,

    CONSTRAINT fk_user_tokens_user
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);


-- =====================================================
-- ROLES TABLE
-- =====================================================
CREATE TABLE roles (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


-- =====================================================
-- RESOURCES TABLE
-- =====================================================
CREATE TABLE resources (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


-- =====================================================
-- PERMISSIONS TABLE
-- =====================================================
CREATE TABLE permissions (
    id VARCHAR(36) PRIMARY KEY,
    resource_id VARCHAR(36),
    action VARCHAR(50) NOT NULL,
    method VARCHAR(10) NOT NULL,
    path TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_permissions_resource
    FOREIGN KEY (resource_id)
    REFERENCES resources(id)
    ON DELETE CASCADE
);


-- =====================================================
-- USER ROLES TABLE (Many-to-Many)
-- =====================================================
CREATE TABLE user_roles (
    user_id VARCHAR(36),
    role_id VARCHAR(36),
    assigned_by VARCHAR(36),
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id, role_id),

    CONSTRAINT fk_user_roles_user
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE,

    CONSTRAINT fk_user_roles_role
    FOREIGN KEY (role_id)
    REFERENCES roles(id)
    ON DELETE CASCADE,

    CONSTRAINT fk_user_roles_assigned_by
    FOREIGN KEY (assigned_by)
    REFERENCES users(id)
);


-- =====================================================
-- ROLE PERMISSIONS TABLE (Many-to-Many)
-- =====================================================
CREATE TABLE role_permissions (
    role_id VARCHAR(36),
    permission_id VARCHAR(36),

    PRIMARY KEY (role_id, permission_id),

    CONSTRAINT fk_role_permissions_role
    FOREIGN KEY (role_id)
    REFERENCES roles(id)
    ON DELETE CASCADE,

    CONSTRAINT fk_role_permissions_permission
    FOREIGN KEY (permission_id)
    REFERENCES permissions(id)
    ON DELETE CASCADE
);