from sqlmodel import SQLModel, Field
from typing import Optional


class EmailNotification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    recipient_email: str
    subject: str
    message: str


class SMSNotification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    phone_number: str
    message: str
