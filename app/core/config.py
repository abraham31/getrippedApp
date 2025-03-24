# core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY")
    MONGO_URI = os.getenv("MONGO_URI")
    DATABASE_NAME = os.getenv("DATABASE_NAME")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
    INVITE_TOKEN_EXPIRE_HOURS = int(os.getenv("INVITE_TOKEN_EXPIRE_HOURS", 24))
    ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    FROM_EMAIL = os.getenv("FROM_EMAIL")
    APP_URL = os.getenv("APP_URL")

settings = Settings()
