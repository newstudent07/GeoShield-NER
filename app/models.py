import uuid
from sqlalchemy import Column, String, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from geoalchemy2 import Geometry

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role = Column(String, nullable=False)
    phone_number = Column(String, unique=True)
    
    reports = relationship("FieldReport", back_populates="reporter")


class GridCell(Base):
    __tablename__ = "grid_cells"

    grid_id = Column(String, primary_key=True)
    geom = Column(Geometry('POLYGON', srid=4326, spatial_index=True))
    base_slope = Column(Float)
    soil_porosity = Column(Float)
    current_risk = Column(Float, default=0.0)
    
    weather_logs = relationship("WeatherLog", back_populates="grid_cell")


class WeatherLog(Base):
    __tablename__ = "weather_logs"

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grid_id = Column(String, ForeignKey("grid_cells.grid_id"))
    timestamp = Column(DateTime(timezone=True), index=True)
    daily_rain = Column(Float)
    cumulative_3d = Column(Float)
    antecedent_30d = Column(Float)
    
    grid_cell = relationship("GridCell", back_populates="weather_logs")


class FieldReport(Base):
    __tablename__ = "field_reports"

    report_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    geom = Column(Geometry('POINT', srid=4326, spatial_index=True))
    photo_url = Column(String)
    ai_confidence = Column(Float)
    status = Column(String, default="pending")
    
    reporter = relationship("User", back_populates="reports")
