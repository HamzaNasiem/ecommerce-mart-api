#models.py
from sqlmodel import SQLModel, Field
from typing import Optional


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_name: str | None
    user_email: str | None
    address: str | None = Field(max_length=60)
    phone_number: int | None
    password: str | None


