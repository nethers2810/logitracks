from collections.abc import Generator

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.db.models.auth import AppUser
from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_pilot_user(db: Session) -> AppUser | None:
    if not hasattr(db, "scalar"):
        return None
    return db.scalar(select(AppUser).where(AppUser.is_active.is_(True)).order_by(AppUser.user_id.asc()))


def get_current_user(db: Session = Depends(get_db)) -> AppUser | None:
    """Pilot mode dependency: returns first active user if available; never enforces auth."""
    return _get_pilot_user(db)


def require_roles(*roles: str):
    def role_guard(current_user: AppUser | None = Depends(get_current_user)) -> AppUser | None:
        """Enforce role checks when a pilot user context is available."""
        if current_user is None:
            return None
        if current_user.role not in roles:
            raise AppError("Forbidden", status_code=403, code="forbidden")
        return current_user

    return role_guard
