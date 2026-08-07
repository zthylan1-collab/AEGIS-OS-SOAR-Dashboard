import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / "config" / ".env")


class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://aegis:aegis123@localhost:5432/aegis_db")
    REDPANDA_BOOTSTRAP = os.getenv("REDPANDA_BOOTSTRAP_SERVERS", "localhost:9092")
    LOCALSTACK_ENDPOINT = os.getenv("LOCALSTACK_ENDPOINT", "http://localhost:4566")
    RAW_EVENTS_TOPIC = os.getenv("RAW_EVENTS_TOPIC", "raw-cloud-events")


settings = Settings()