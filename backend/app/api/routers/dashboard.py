from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.dashboard import DashboardSummary, RecentImport, RecentRun, RecommendationStatusBreakdown
from app.services.dashboard import get_dashboard_summary, recent_imports, recent_runs, recommendation_status_breakdown

router = APIRouter(prefix="/dashboard")


@router.get("/summary", response_model=DashboardSummary)
def summary(db: Session = Depends(get_db)):
    return get_dashboard_summary(db)


@router.get("/recent-imports", response_model=list[RecentImport])
def get_recent_imports(limit: int = 20, db: Session = Depends(get_db)):
    return recent_imports(db, limit)


@router.get("/recent-runs", response_model=list[RecentRun])
def get_recent_runs(limit: int = 20, db: Session = Depends(get_db)):
    return recent_runs(db, limit)


@router.get("/recommendation-status-breakdown", response_model=list[RecommendationStatusBreakdown])
def get_reco_breakdown(db: Session = Depends(get_db)):
    return recommendation_status_breakdown(db)
