from collections.abc import Generator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.core.security import decode_token
from app.db.models.auth import AppUser
from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme), db: Session = Depends(get_db)) -> AppUser:
    if not credentials:
        raise AppError("Authentication required", status_code=401, code="unauthorized")
    try:
        payload = decode_token(credentials.credentials)
    except Exception as exc:  # noqa: BLE001
        raise AppError("Invalid or expired token", status_code=401, code="unauthorized") from exc

    email = payload.get("sub")
    if not email:
        raise AppError("Invalid token subject", status_code=401, code="unauthorized")

    user = db.scalar(select(AppUser).where(AppUser.email == email, AppUser.is_active.is_(True)))
    if not user:
        raise AppError("User not found or inactive", status_code=401, code="unauthorized")
    return user


def require_roles(*roles: str):
    def role_guard(current_user: AppUser = Depends(get_current_user)) -> AppUser:
        if current_user.role not in roles:
            raise AppError("Insufficient role permissions", status_code=403, code="forbidden")
        return current_user

    return role_guard
