import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)

class Config:
    APP_NAME = "DoomerPOS v4.0"
    SECRET_KEY = os.environ.get("DOOMERPOS_SECRET_KEY", "dev-cambia-esta-clave-en-produccion-v4")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", f"sqlite:///{INSTANCE_DIR / 'doomerpos_v4.db'}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_BLOCK_MINUTES = 10
    DEFAULT_TAX_RATE = "15.00"
    JSON_SORT_KEYS = False
