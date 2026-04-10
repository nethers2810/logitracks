from typing import Any

from sqlalchemy import String, asc, cast, desc, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AppError


class CRUDService:
    def __init__(self, model: type, id_field: str, search_fields: list[str], duplicate_fields: list[str] | None = None):
        self.model = model
        self.id_field = id_field
        self.search_fields = search_fields
        self.duplicate_fields = duplicate_fields or []

    def list(
        self,
        db: Session,
        page: int,
        page_size: int,
        sort_by: str | None,
        sort_order: str,
        q: str | None,
        filters: dict[str, Any],
    ) -> tuple[list[Any], int]:
        stmt = select(self.model)
        for key, value in filters.items():
            if value is None or not hasattr(self.model, key):
                continue
            stmt = stmt.where(getattr(self.model, key) == value)

        if q:
            conditions = [cast(getattr(self.model, field), String).ilike(f"%{q}%") for field in self.search_fields if hasattr(self.model, field)]
            if conditions:
                stmt = stmt.where(or_(*conditions))

        sort_col = getattr(self.model, sort_by) if sort_by and hasattr(self.model, sort_by) else getattr(self.model, self.id_field)
        stmt = stmt.order_by(desc(sort_col) if sort_order == "desc" else asc(sort_col))

        total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)).all()
        return items, total

    def get(self, db: Session, entity_id: int) -> Any:
        instance = db.get(self.model, entity_id)
        if not instance:
            raise AppError(f"{self.model.__name__} {entity_id} not found", status_code=404, code="not_found")
        return instance

    def create(self, db: Session, payload: dict[str, Any]) -> Any:
        self._check_duplicate(db, payload)
        instance = self.model(**payload)
        db.add(instance)
        self._flush_or_raise(db)
        db.commit()
        db.refresh(instance)
        return instance

    def update(self, db: Session, entity_id: int, payload: dict[str, Any]) -> Any:
        instance = self.get(db, entity_id)
        merged = {**{k: getattr(instance, k, None) for k in payload.keys()}, **payload}
        self._check_duplicate(db, merged, exclude_id=entity_id)
        for key, value in payload.items():
            setattr(instance, key, value)
        self._flush_or_raise(db)
        db.commit()
        db.refresh(instance)
        return instance

    def delete(self, db: Session, entity_id: int) -> None:
        instance = self.get(db, entity_id)
        db.delete(instance)
        db.commit()

    def _check_duplicate(self, db: Session, payload: dict[str, Any], exclude_id: int | None = None) -> None:
        if not self.duplicate_fields:
            return
        conditions = []
        for field in self.duplicate_fields:
            value = payload.get(field)
            if value is None:
                return
            conditions.append(getattr(self.model, field) == value)
        stmt = select(self.model).where(*conditions)
        existing = db.scalars(stmt).first()
        if existing and getattr(existing, self.id_field) != exclude_id:
            raise AppError("Possible duplicate detected", status_code=409, code="duplicate_detected")

    def _flush_or_raise(self, db: Session) -> None:
        try:
            db.flush()
        except IntegrityError as exc:
            db.rollback()
            raise AppError("Data integrity error", status_code=409, code="integrity_error") from exc
