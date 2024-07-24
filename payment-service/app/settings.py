#settings.py
from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

DATABASE_URL = config("DATABASE_URL", cast=Secret)
TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=Secret)

# Stripe API Key
STRIPE_API_KEY = config("STRIPE_API_KEY", cast=str)
STRIPE_ENDPOINT_SECRET = config("STRIPE_ENDPOINT_SECRET", cast=str)

# Kafka settings
BOOTSTRAP_SERVER = config("BOOTSTRAP_SERVER", cast=str)
KAFKA_PAYMENT_TOPIC = config("KAFKA_PAYMENT_TOPIC", cast=str)
KAFKA_CONSUMER_GROUP_ID_FOR_PAYMENT = config(
    "KAFKA_CONSUMER_GROUP_ID_FOR_PAYMENT", cast=str)
