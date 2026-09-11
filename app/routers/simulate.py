from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import GridCell
from app.services.weather import fetch_weather_data
from app.services.notifier import send_telegram_alert
import sys
import os

# Ensure engine is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from engine.isro_formula import compute_isro_probability
from engine.predictor import predict_cell_risk

router = APIRouter(prefix="/api/v1/simulate", tags=["simulate"])

class SimulatePayload(BaseModel):
    rainfall_mm: float

@router.post("/weather")
def simulate_weather(payload: SimulatePayload, db: Session = Depends(get_db)):
    """
    Simulates extreme weather by accepting a manual rainfall override,
    running the ML engine on all grid cells, updating the DB, and dispatching alerts.
    """
    # 1. Fetch current background weather data (to get 3DCR and 30DAR baselines)
    weather = fetch_weather_data()
    
    # 2. Override DR with the simulated payload
    simulated_dr = payload.rainfall_mm
    
    # Recalculate 3DCR by replacing the most recent day with the simulated one
    # If weather.dcr3 was a sum of 3 days including a 0 for today, we just add simulated_dr
    # But since we don't have the exact daily array here, let's roughly approximate:
    # new_dcr3 = (weather.dcr3 - weather.dr) + simulated_dr
    simulated_dcr3 = max(0, weather.dcr3 - weather.dr) + simulated_dr
    simulated_dar30 = weather.dar30
    
    # 3. Calculate z-score once for these rainfall conditions
    z, p_isro = compute_isro_probability(simulated_dr, simulated_dcr3, simulated_dar30)
    
    cells = db.query(GridCell).all()
    max_risk = -1.0
    highest_risk_cell = None
    highest_base_slope = -1.0
    
    for cell in cells:
        features = {
            "z_score": z,
            "DR": simulated_dr,
            "3DCR": simulated_dcr3,
            "30DAR": simulated_dar30,
            "base_slope": cell.base_slope,
            "soil_porosity": cell.soil_porosity
        }
        
        # 4. Predict Risk
        risk = predict_cell_risk(features)
        
        # 5. Update cell
        cell.current_risk = risk
        
        # Tie-breaking logic: if XGBoost trees saturate and return identical probabilities,
        # fallback to picking the cell with the steeper slope.
        if risk > max_risk + 1e-6:
            max_risk = risk
            highest_risk_cell = cell.grid_id
            highest_base_slope = cell.base_slope
        elif abs(risk - max_risk) <= 1e-6:
            if cell.base_slope > highest_base_slope:
                highest_risk_cell = cell.grid_id
                highest_base_slope = cell.base_slope
            
    db.commit()
    
    # 6. Trigger Telegram alert if any cell's risk is >= 0.70
    if max_risk >= 0.70:
        alert_msg = (
            f"🚨 LANDSLIDE ALERT 🚨\n"
            f"Simulated Rainfall: {simulated_dr}mm\n"
            f"Highest Risk Cell: {highest_risk_cell} (Risk: {max_risk:.2f})\n"
            f"Please review the GeoShield Dashboard immediately."
        )
        send_telegram_alert(alert_msg)
        
    return {"status": "success", "max_risk": max_risk, "highest_risk_cell": highest_risk_cell}
