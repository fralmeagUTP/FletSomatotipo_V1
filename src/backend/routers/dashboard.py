from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth_utils import get_current_user
from ..database import get_db
from ..services import dashboard_service


router = APIRouter(prefix="/dashboard", tags=["Dashboard"], dependencies=[Depends(get_current_user)])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    return dashboard_service.get_dashboard_summary(db)
