#models.py

from sqlmodel import SQLModel, Field
from typing import Optional


class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    payment_method: str


