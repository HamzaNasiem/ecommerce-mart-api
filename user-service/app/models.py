

#models.py
from sqlmodel import SQLModel, Field
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_name: str
    user_email: str
    address: str = Field(max_length=60)
    phone_number: int
    password: str

class Token(SQLModel):
    access_token: str
    token_type: str

