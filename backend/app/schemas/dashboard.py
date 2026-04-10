from datetime import datetime

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_products: int
    total_customers: int
    total_trucks: int
    total_orders: int
    total_runs: int
    manual_review_count: int
    no_fit_count: int


class RecentImport(BaseModel):
    import_log_id: int
    source_name: str | None = None
    file_name: str | None = None
    status: str | None = None
    started_at: datetime | None = None


class RecentRun(BaseModel):
    run_id: int
    order_id: int
    status: str | None = None
    run_started_at: datetime | None = None


class RecommendationStatusBreakdown(BaseModel):
    recommendation_status: str
    count: int
