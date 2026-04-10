from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


@dataclass
class ImportContext:
    source_import_log_id: int


class AuditService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_import_log(self, source_type: str, file_name: str, row_count: int = 0) -> ImportContext:
        row = self.session.execute(
            text(
                """
                INSERT INTO audit.source_import_log
                    (source_type, file_name, started_at, status, row_count)
                VALUES
                    (:source_type, :file_name, now(), 'processing', :row_count)
                RETURNING source_import_log_id
                """
            ),
            {"source_type": source_type, "file_name": file_name, "row_count": row_count},
        ).one()
        return ImportContext(source_import_log_id=row[0])

    def add_validation_error(
        self,
        source_import_log_id: int,
        row_number: int | None,
        field_name: str | None,
        error_code: str,
        message: str,
        raw_payload: dict[str, Any] | None = None,
    ) -> None:
        self.session.execute(
            text(
                """
                INSERT INTO audit.validation_error
                    (source_import_log_id, row_number, field_name, error_code, error_message, raw_payload, created_at)
                VALUES
                    (:source_import_log_id, :row_number, :field_name, :error_code, :message, CAST(:raw_payload AS jsonb), now())
                """
            ),
            {
                "source_import_log_id": source_import_log_id,
                "row_number": row_number,
                "field_name": field_name,
                "error_code": error_code,
                "message": message,
                "raw_payload": None if raw_payload is None else str(raw_payload).replace("'", '"'),
            },
        )

    def mark_complete(self, source_import_log_id: int, processed_rows: int, error_rows: int) -> None:
        self.session.execute(
            text(
                """
                UPDATE audit.source_import_log
                SET status = CASE WHEN :error_rows > 0 THEN 'completed_with_errors' ELSE 'completed' END,
                    finished_at = now(),
                    processed_rows = :processed_rows,
                    error_rows = :error_rows
                WHERE source_import_log_id = :source_import_log_id
                """
            ),
            {
                "source_import_log_id": source_import_log_id,
                "processed_rows": processed_rows,
                "error_rows": error_rows,
            },
        )
