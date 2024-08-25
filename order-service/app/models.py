#models.py

from sqlmodel import SQLModel, Field
from typing import  Optional
from datetime import datetime


class Order(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    user_id: int
    products: int
    total_amount: float


# from sqlmodel import SQLModel, Field
# from typing import Optional
# from datetime import datetime


# class Order(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     user_id: int
#     products: int   
#     total_amount: float
#     status: str

