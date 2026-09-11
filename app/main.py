from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import grid, simulate, reports
from app.database import engine
from app.models import Base

# Ensure tables are created if they don't exist (useful for testing/initialization)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GeoShield-NER API", version="1.0.0")

# Check 1: Explicitly configure CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(grid.router)
app.include_router(simulate.router)
app.include_router(reports.router)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "GeoShield Backend"}
