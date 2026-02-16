# app/core/security.py

from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

# ------------------ CONFIG ------------------
SECRET_KEY = "SUPER_SECRET_KEY_CHANGE_THIS"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Passlib context for bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# ------------------ PASSWORD ------------------
def hash_password(password: str) -> str:
    """
    Hash the password using bcrypt.
    Truncate to 72 bytes manually to avoid bcrypt limitations.
    """
    # Ensure password is UTF-8 bytes and max 72 bytes
    truncated = password.encode("utf-8")[:72]
    # Decode back to string for Passlib
    return pwd_context.hash(truncated.decode("utf-8"))


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify password against hashed value.
    Truncate to 72 bytes to match hashing rules.
    """
    truncated = password.encode("utf-8")[:72]
    return pwd_context.verify(truncated.decode("utf-8"), hashed)


# ------------------ JWT TOKEN ------------------
def create_access_token(user_id: int, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    """
    Create a JWT access token for a user.
    """
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload = {
        "sub": str(user_id),
        "exp": expire
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token
