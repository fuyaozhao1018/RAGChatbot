import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
try:
    import bcrypt  # optional direct use; passlib normally wraps this
except Exception:
    bcrypt = None
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import load_project_env

load_project_env()

# Use PBKDF2-SHA256 as a robust pure-Python password hashing scheme to
# avoid platform-specific bcrypt binary issues and the 72-byte truncation
# limitation. This is safe for development and small deployments. For
# production you may prefer argon2 or a properly installed bcrypt C-extension.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
security = HTTPBearer()

JWT_SECRET = os.getenv("JWT_SECRET", "change_me")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "43200"))
ALGORITHM = "HS256"

def get_password_hash(password: str) -> str:
    """Return a bcrypt hash for `password` using passlib.

    If the underlying bcrypt extension is missing, this will still work
    when passlib falls back to a pure-Python implementation, but for
    best performance ensure the `bcrypt` package is installed.
    """
    # bcrypt only processes the first 72 bytes of a password. Ensure we
    # truncate at the same boundary to avoid ValueError from the backend
    # and keep behavior predictable across environments.
    # Truncate to 72 bytes in a UTF-8 safe way so the resulting str, when
    # encoded, is at most 72 bytes. This avoids bcrypt backend ValueError.
    b = password.encode('utf-8')[:72]
    safe = b.decode('utf-8', 'ignore')
    return pwd_context.hash(safe)

def verify_password(plain_password: str, password_hash: str) -> bool:
    # Apply the same 72-byte truncation rule used when hashing.
    b = plain_password.encode('utf-8')[:72]
    safe = b.decode('utf-8', 'ignore')
    try:
        return pwd_context.verify(safe, password_hash)
    except Exception:
        # fallback to direct bcrypt if available and passlib failed for some reason
        if bcrypt is not None:
            try:
                return bcrypt.checkpw(safe.encode('utf-8'), password_hash.encode('utf-8'))
            except Exception:
                return False
        return False


def require_bcrypt_installed() -> None:
    """Raise a helpful error if the bcrypt package is missing.

    Call this from scripts or deploy checks to prompt installing the
    binary dependency when necessary.
    """
    if bcrypt is None:
        raise RuntimeError("Missing 'bcrypt' package — run: pip install bcrypt")


def hash_password_with_bcrypt(password: str) -> str:
    """Directly hash a password using the bcrypt package (fallback helper).

    Useful when you want the explicit bcrypt-generated hash string.
    """
    if bcrypt is None:
        raise RuntimeError("bcrypt package is not installed")
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
