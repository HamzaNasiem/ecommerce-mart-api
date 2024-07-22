# # settings.py

from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

DATABASE_URL = config("DATABASE_URL", cast=Secret)
SMTP_SERVER = config("SMTP_SERVER", cast=str)
SMTP_PORT = config("SMTP_PORT", cast=int)
SMTP_USERNAME = config("SMTP_USERNAME", cast=str)
SMTP_PASSWORD = config("SMTP_PASSWORD", cast=Secret)
FROM_EMAIL = config("FROM_EMAIL", cast=str)

# Twilio Settings
TWILIO_ACCOUNT_SID = config("TWILIO_ACCOUNT_SID", cast=str)
TWILIO_AUTH_TOKEN = config("TWILIO_AUTH_TOKEN", cast=str)
TWILIO_PHONE_NUMBER = config("TWILIO_PHONE_NUMBER", cast=str)
