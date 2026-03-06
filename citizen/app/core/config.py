import os
from dotenv import load_dotenv

SECRET_KEY = "2da93ba33ef883d05c8313c326e0b43488235180d44a80df28d669d033673aac"
ALGORITHM = "HS256"

ACCESS_EXPIRE_MINUTES = 15
REFRESH_EXPIRE_DAYS = 30

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "psriram543@gmail.com"
SMTP_PASS = "gwnr oskj dvpx kkrl"



load_dotenv()

class Settings:
    SHIPROCKET_EMAIL: str = os.getenv("SHIPROCKET_EMAIL")
    SHIPROCKET_PASSWORD: str = os.getenv("SHIPROCKET_PASSWORD")
    WAREHOUSE_PINCODE: str = os.getenv("WAREHOUSE_PINCODE")

    if not SHIPROCKET_EMAIL or not SHIPROCKET_PASSWORD:
        raise ValueError("Shiprocket credentials missing in .env")

settings = Settings()