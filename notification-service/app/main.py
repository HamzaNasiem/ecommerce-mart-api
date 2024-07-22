from typing import Annotated
from sqlmodel import Session, select
from fastapi import FastAPI, Depends, HTTPException, Request

from app.models import EmailNotification, SMSNotification
from app.db_engine import create_db_and_tables, get_session
from app.smtp import send_email
from app.sms import send_sms

app = FastAPI(title="Notification Service", version="0.0.2", description="The Notification Service API sends notifications (email and SMS) to users about order statuses and other important updates. It provides endpoints for creating and sending notifications, ensuring timely and effective communication with users. This service integrates with other services to deliver relevant updates and maintain user engagement.")


@app.on_event("startup")
def on_startup():
    print("Creating tables..")
    create_db_and_tables()


@app.get("/")
def read_root():
    return {"Hello": "Notification Service"}

# Endpoints for Email Notifications


@app.post("/notifications/", response_model=EmailNotification)
async def create_new_email_notification(
    notification: EmailNotification,
    session: Annotated[Session, Depends(get_session)]
) -> EmailNotification:
    try:
        send_email(notification.recipient_email,
                   notification.subject, notification.message)
        session.add(notification)
        session.commit()
        session.refresh(notification)
        return notification
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/notifications/", response_model=list[EmailNotification])
def read_notifications(session: Annotated[Session, Depends(get_session)]):
    try:
        notifications = session.exec(select(EmailNotification)).all()
        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @app.get("/notifications/{notification_id}", response_model=EmailNotification)
# def read_notification_by_id(notification_id: int, session: Annotated[Session, Depends(get_session)]):
#     try:
#         notification = session.get(EmailNotification, notification_id)
#         if not notification:
#             raise HTTPException(
#                 status_code=404, detail="Notification not found")
#         return notification
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@app.delete("/notifications/{notification_id}")
def delete_notification(notification_id: int, session: Annotated[Session, Depends(get_session)]):
    try:
        notification = session.get(EmailNotification, notification_id)
        if not notification:
            raise HTTPException(
                status_code=404, detail="Notification not found")

        session.delete(notification)
        session.commit()
        return {"detail": "Notification deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints for SMS Notifications


@app.post("/sms/", response_model=SMSNotification)
async def create_new_sms_notification(
    notification: SMSNotification,
    session: Annotated[Session, Depends(get_session)]
) -> SMSNotification:
    try:
        send_sms(notification.phone_number, notification.message)
        session.add(notification)
        session.commit()
        session.refresh(notification)
        return notification
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sms/", response_model=list[SMSNotification])
def read_sms_notifications(session: Annotated[Session, Depends(get_session)]):
    try:
        notifications = session.exec(select(SMSNotification)).all()
        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @app.get("/sms/{notification_id}", response_model=SMSNotification)
# def read_sms_notification_by_id(notification_id: int, session: Annotated[Session, Depends(get_session)]):
#     try:
#         notification = session.get(SMSNotification, notification_id)
#         if not notification:
#             raise HTTPException(
#                 status_code=404, detail="SMS Notification not found")
#         return notification
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@app.delete("/sms/{notification_id}")
def delete_sms_notification(notification_id: int, session: Annotated[Session, Depends(get_session)]):
    try:
        notification = session.get(SMSNotification, notification_id)
        if not notification:
            raise HTTPException(
                status_code=404, detail="SMS Notification not found")

        session.delete(notification)
        session.commit()
        return {"detail": "SMS Notification deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint for receiving SMS notifications from Twilio


# @app.post("/sms/receive/")
# async def receive_sms(request: Request):
#     form_data = await request.form()
#     from_number = form_data.get("From")
#     message_body = form_data.get("Body")

#     # Process SMS here
#     print(f"Received SMS from {from_number}: {message_body}")

#     # You can also store SMS in the database or trigger other actions here

#     return {"status": "SMS received"}
