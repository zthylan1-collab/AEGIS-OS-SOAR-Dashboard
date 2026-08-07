from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from jsonschema import ValidationError as SchemaValidationError
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from config.settings import settings
from database.models import Asset, SessionLocal
from event_pipeline.producer import get_producer, send_event
from event_pipeline.schema import validate_event

app = FastAPI(
    title="AEGIS-OS Cloud Infrastructure API",
    description="واجهة الطالب الأول: الأصول السحابية + نقطة الإدخال الموحدة للأحداث",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    type: str
    cloud_provider: str
    region: str
    details: dict
    last_seen: datetime


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok", "service": "AEGIS-OS Cloud Engine", "version": "1.0.0"}


@app.get("/api/v1/assets", response_model=list[AssetOut])
def list_assets(db: Session = Depends(get_db)):
    return db.query(Asset).order_by(Asset.last_seen.desc()).all()


@app.get("/api/v1/assets/{asset_id}", response_model=AssetOut)
def get_asset(asset_id: str, db: Session = Depends(get_db)):
    asset = db.get(Asset, asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@app.post("/api/v1/ingest", status_code=202)
def ingest_event(payload: dict):
    """نقطة إدخال موحدة: تتحقق من العقد ثم تنشر الحدث إلى Redpanda"""
    try:
        validate_event(payload)
    except SchemaValidationError as exc:
        raise HTTPException(status_code=422, detail=f"Event violates contract: {exc.message}")
    send_event(get_producer(), settings.RAW_EVENTS_TOPIC, payload)
    return {"status": "accepted", "event_id": payload.get("event_id")}