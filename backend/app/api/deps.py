from collections.abc import Generator

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.auth import AppUser
from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_pilot_user(db: Session) -> AppUser | None:
    return db.scalar(select(AppUser).where(AppUser.is_active.is_(True)).order_by(AppUser.user_id.asc()))


def get_current_user(db: Session = Depends(get_db)) -> AppUser | None:
    """Pilot mode dependency: returns first active user if available; never enforces auth."""
    return _get_pilot_user(db)


def require_roles(*roles: str):
    def role_guard(db: Session = Depends(get_db)) -> AppUser | None:
        """Pilot mode role guard: intentionally bypassed for no-auth internal workflow."""
        return _get_pilot_user(db)

    return role_guard
