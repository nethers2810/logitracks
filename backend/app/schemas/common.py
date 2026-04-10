from pydantic import BaseModel, Field


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int


class ListResponse(BaseModel):
    items: list
    meta: PaginationMeta


class ListQueryParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=200)
    sort_by: str | None = None
    sort_order: str = "asc"
    q: str | None = None
