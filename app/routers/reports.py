from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.models import FieldReport

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])

# Check 3: Strict Contract Validation
class FieldReportCreate(BaseModel):
    report_id: UUID
    reporter_id: UUID
    latitude: float
    longitude: float
    photo_url: str
    ai_confidence: float
    status: Optional[str] = "pending"

@router.post("/sync")
def sync_reports(reports: List[FieldReportCreate], db: Session = Depends(get_db)):
    """
    Accepts offline field reports batch.
    Ignores duplicates gracefully to prevent DB crashes.
    """
    inserted = 0
    ignored = 0
    
    for r in reports:
        # Convert lat/lon to WKT POINT for PostGIS
        point_wkt = f"SRID=4326;POINT({r.longitude} {r.latitude})"
        
        new_report = FieldReport(
            report_id=r.report_id,
            reporter_id=r.reporter_id,
            geom=point_wkt,
            photo_url=r.photo_url,
            ai_confidence=r.ai_confidence,
            status=r.status
        )
        
        db.add(new_report)
        try:
            db.commit()
            inserted += 1
        except IntegrityError:
            db.rollback()
            ignored += 1
            
    return {"status": "success", "inserted": inserted, "ignored": ignored}
