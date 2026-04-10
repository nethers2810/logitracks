from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.db.models.auth import AppUser


def get_user_by_email(db: Session, email: str) -> AppUser | None:
    return db.scalar(select(AppUser).where(AppUser.email == email.lower().strip()))


def authenticate_user(db: Session, email: str, password: str) -> AppUser | None:
    user = get_user_by_email(db, email)
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
