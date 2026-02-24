# app/db/models/user_model.py

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from app.core.database import Base


# =============================================================================
# USER TABLE
# =============================================================================

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String(250), nullable=False)

    email = Column(String(200), nullable=False, unique=True, index=True)

    contact = Column(String(30))

    password_hash = Column(String(255), nullable=False)

    bearer_token = Column(Text)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)


# =============================================================================
# USER PROFILE
# =============================================================================

class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(String(36),
                     ForeignKey("users.id", ondelete="CASCADE"),
                     primary_key=True)

    profile_picture = Column(String(500))

    phone_number = Column(String(30))

    address = Column(Text)

    city = Column(String(100))

    state = Column(String(100))

    country = Column(String(100))

    postal_code = Column(String(20))

    date_of_birth = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(DateTime,
                        default=datetime.utcnow,
                        onupdate=datetime.utcnow)


# =============================================================================
# USER TOKEN
# =============================================================================

class UserToken(Base):
    __tablename__ = "user_tokens"

    id = Column(String(36),
                primary_key=True,
                default=lambda: str(uuid.uuid4()))

    user_id = Column(String(36),
                     ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False)

    token = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    expires_at = Column(DateTime)


# =============================================================================
# ROLE TABLE
# =============================================================================

class Role(Base):
    __tablename__ = "roles"

    id = Column(String(36),
                primary_key=True,
                default=lambda: str(uuid.uuid4()))

    name = Column(String(50), nullable=False, unique=True)

    description = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(DateTime,
                        default=datetime.utcnow,
                        onupdate=datetime.utcnow)


# =============================================================================
# RESOURCE TABLE
# =============================================================================

class Resource(Base):
    __tablename__ = "resources"

    id = Column(String(36),
                primary_key=True,
                default=lambda: str(uuid.uuid4()))

    name = Column(String(100), unique=True, nullable=False)

    description = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(DateTime,
                        default=datetime.utcnow,
                        onupdate=datetime.utcnow)


# =============================================================================
# PERMISSION TABLE
# =============================================================================

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(String(36),
                primary_key=True,
                default=lambda: str(uuid.uuid4()))

    resource_id = Column(String(36),
                         ForeignKey("resources.id", ondelete="CASCADE"))

    action = Column(String(50), nullable=False)

    method = Column(String(10), nullable=False)

    path = Column(Text, nullable=False)

    description = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(DateTime,
                        default=datetime.utcnow,
                        onupdate=datetime.utcnow)


# =============================================================================
# USER ROLE TABLE (Many-to-Many)
# =============================================================================

class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(String(36),
                     ForeignKey("users.id", ondelete="CASCADE"),
                     primary_key=True)

    role_id = Column(String(36),
                     ForeignKey("roles.id", ondelete="CASCADE"),
                     primary_key=True)

    assigned_by = Column(String(36),
                         ForeignKey("users.id"))

    assigned_at = Column(DateTime,
                         default=datetime.utcnow)

    created_at = Column(DateTime,
                        default=datetime.utcnow)

    updated_at = Column(DateTime,
                        default=datetime.utcnow,
                        onupdate=datetime.utcnow)


# =============================================================================
# ROLE PERMISSION TABLE (Many-to-Many)
# =============================================================================

class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id = Column(String(36),
                     ForeignKey("roles.id", ondelete="CASCADE"),
                     primary_key=True)

    permission_id = Column(String(36),
                           ForeignKey("permissions.id", ondelete="CASCADE"),
                           primary_key=True)
