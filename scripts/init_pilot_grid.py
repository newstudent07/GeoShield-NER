import json
import random
import uuid
from typing import List, Dict

from shapely.geometry import Polygon, mapping
from shapely.validation import make_valid
from pyproj import Transformer

from sqlalchemy import create_engine, Column, String, Float, text
from sqlalchemy.orm import declarative_base, sessionmaker
from geoalchemy2 import Geometry

# --- CONFIGURATION ---
DB_URL = "postgresql://postgres:geoshield123@localhost:5432/geoshield_db"

# Aizawl / NH-29 Corridor BBox (Approx)
LAT_MIN, LAT_MAX = 23.70, 23.76
LON_MIN, LON_MAX = 92.68, 92.75

# Cell Size in meters
CELL_SIZE_M = 500

# EPSG Codes
CRS_WGS84 = 4326
CRS_UTM46N = 32646  # UTM Zone 46N covers Mizoram (90E to 96E)

# --- DATABASE SETUP ---
Base = declarative_base()

class GridCell(Base):
    __tablename__ = 'grid_cells'

    grid_id = Column(String, primary_key=True)
    geom = Column(Geometry('POLYGON', srid=4326, spatial_index=True))
    base_slope = Column(Float)
    soil_porosity = Column(Float)
    current_risk = Column(Float, default=0.1)

def setup_db():
    engine = create_engine(DB_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return engine, Session()

def generate_pilot_grid() -> List[Dict]:
    # Transformers
    transformer_to_utm = Transformer.from_crs(CRS_WGS84, CRS_UTM46N, always_xy=True)
    transformer_to_wgs84 = Transformer.from_crs(CRS_UTM46N, CRS_WGS84, always_xy=True)

    # 1. Project BBox corners to UTM to find metric boundaries
    # Note: always_xy=True means we pass (lon, lat)
    min_x_utm, min_y_utm = transformer_to_utm.transform(LON_MIN, LAT_MIN)
    max_x_utm, max_y_utm = transformer_to_utm.transform(LON_MAX, LAT_MAX)

    # 2. Generate Grid
    cells = []
    x = min_x_utm
    cell_count = 0
    
    # We need ~150 cells, the total area is (0.07 deg * 111km) ~ 7.7km x 6.6km, which is huge!
    # A 500m x 500m cell is 0.25 sq km. The total area is ~50 sq km, which means ~200 cells.
    # Let's just generate the grid based on the coordinates.
    
    while x < max_x_utm:
        y = min_y_utm
        while y < max_y_utm:
            # Create cell in UTM
            poly_utm = Polygon([
                (x, y),
                (x + CELL_SIZE_M, y),
                (x + CELL_SIZE_M, y + CELL_SIZE_M),
                (x, y + CELL_SIZE_M),
                (x, y)
            ])
            
            # Reproject cell back to WGS84
            # We transform each coordinate
            exterior_coords = [
                transformer_to_wgs84.transform(cx, cy) for cx, cy in poly_utm.exterior.coords
            ]
            poly_wgs84 = Polygon(exterior_coords)
            
            # Validate geometry per Check 2
            if not poly_wgs84.is_valid:
                poly_wgs84 = make_valid(poly_wgs84)
            
            # Generate mock parameters
            base_slope = round(random.uniform(15.0, 48.0), 2)
            soil_porosity = round(random.uniform(40.0, 58.0), 2)
            current_risk = 0.1
            grid_id = f"cell_{str(uuid.uuid4())[:8]}"

            cells.append({
                "grid_id": grid_id,
                "geom": poly_wgs84,
                "base_slope": base_slope,
                "soil_porosity": soil_porosity,
                "current_risk": current_risk
            })
            
            cell_count += 1
            # Stop if we reach roughly 150 contiguous cells as requested (optional, but requested "~150 contiguous")
            # If we want exact ~150 contiguous we might want to stop here or just let it map the bbox.
            # Bbox is roughly 7x6 km = 42km2 / 0.25 = ~168 cells. So we're good to just let it finish.
            
            y += CELL_SIZE_M
        x += CELL_SIZE_M

    return cells

def save_to_db(session, cells):
    print("Clearing existing data...")
    session.query(GridCell).delete()
    
    print(f"Inserting {len(cells)} cells into PostGIS...")
    for c in cells:
        # We need to construct WKT for GeoAlchemy2 insertion
        # WKT format is generally used for insertion. 
        # Alternatively, using element.geom.wkt
        geom_wkt = c["geom"].wkt
        
        # We use explicit SRID in WKT for PostGIS
        srid_wkt = f"SRID=4326;{geom_wkt}"

        cell_record = GridCell(
            grid_id=c["grid_id"],
            geom=srid_wkt,
            base_slope=c["base_slope"],
            soil_porosity=c["soil_porosity"],
            current_risk=c["current_risk"]
        )
        session.add(cell_record)
    
    session.commit()
    print("Successfully inserted rows.")

def export_geojson(cells, output_file="data/pilot_corridor.geojson"):
    import os
    if not os.path.exists("data"):
        os.makedirs("data")

    features = []
    for c in cells:
        feature = {
            "type": "Feature",
            "properties": {
                "grid_id": c["grid_id"],
                "base_slope": c["base_slope"],
                "soil_porosity": c["soil_porosity"],
                "current_risk": c["current_risk"]
            },
            "geometry": mapping(c["geom"])
        }
        features.append(feature)

    feature_collection = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(output_file, 'w') as f:
        json.dump(feature_collection, f, indent=2)
    print(f"Created {output_file}.")

def main():
    print("Connecting to database...")
    engine, session = setup_db()
    
    # Ensure PostGIS is enabled
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.commit()
    session.commit() # just in case
    
    print("Generating pilot grid...")
    cells = generate_pilot_grid()
    
    save_to_db(session, cells)
    export_geojson(cells)
    
if __name__ == "__main__":
    main()
