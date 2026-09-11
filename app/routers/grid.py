import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import GridCell
import shapely.wkt
from shapely.geometry import mapping
from geoalchemy2.shape import to_shape

router = APIRouter(prefix="/api/v1/grid", tags=["grid"])

@router.get("/risk")
def get_grid_risk(db: Session = Depends(get_db)):
    """
    Returns GeoJSON FeatureCollection of all grid cells and their current_risk.
    """
    cells = db.query(GridCell).all()
    features = []
    
    for cell in cells:
        # geoalchemy2 provides to_shape to easily convert WKBElement to Shapely geometry
        geom = to_shape(cell.geom)
        features.append({
            "type": "Feature",
            "properties": {
                "grid_id": cell.grid_id,
                "current_risk": cell.current_risk,
                "base_slope": cell.base_slope,
                "soil_porosity": cell.soil_porosity
            },
            "geometry": mapping(geom)
        })
        
    return {
        "type": "FeatureCollection",
        "features": features
    }
