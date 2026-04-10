from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SourceImportLog(Base):
    __tablename__ = "source_import_log"
    __table_args__ = ({"schema": "audit"},)

    import_log_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_name: Mapped[str | None] = mapped_column(String(100))
    file_name: Mapped[str | None] = mapped_column(String(255))
    import_type: Mapped[str | None] = mapped_column(String(100))
    row_count: Mapped[int | None] = mapped_column(Integer)
    success_count: Mapped[int | None] = mapped_column(Integer)
    error_count: Mapped[int | None] = mapped_column(Integer)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)


class ValidationError(Base):
    __tablename__ = "validation_error"
    __table_args__ = (
        Index("ix_audit_validation_error_import_log_id", "import_log_id"),
        Index("ix_audit_validation_error_entity_name", "entity_name"),
        {"schema": "audit"},
    )

    validation_error_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    import_log_id: Mapped[int | None] = mapped_column(ForeignKey("audit.source_import_log.import_log_id"))
    entity_name: Mapped[str | None] = mapped_column(String(100))
    row_identifier: Mapped[str | None] = mapped_column(String(255))
    field_name: Mapped[str | None] = mapped_column(String(100))
    error_code: Mapped[str | None] = mapped_column(String(100))
    error_message: Mapped[str | None] = mapped_column(Text)
    severity: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
