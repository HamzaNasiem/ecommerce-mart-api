from twilio.rest import Client
from app import settings


def send_sms(to_phone_number: str, body: str) -> str:
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=body,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=to_phone_number
    )
    return message.sid
