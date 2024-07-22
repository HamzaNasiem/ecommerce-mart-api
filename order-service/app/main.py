from contextlib import asynccontextmanager
from typing import Annotated
from sqlmodel import Session, select
from fastapi import FastAPI, Depends, HTTPException
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer
import asyncio
import json

from app.models import Order
from app.db_engine import create_db_and_tables, get_session
from app.kafka import consume_messages, get_kafka_producer
from app import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating tables..")
    create_db_and_tables()
    task = asyncio.create_task(consume_messages(
        'order', settings.BOOTSTRAP_SERVER))
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan, title="Order Service", version="0.0.1", description="The Order Service API is responsible for handling order creation, updating, and tracking. It provides endpoints for placing new orders, updating order details, and tracking order statuses throughout their lifecycle. This service manages the order process and integrates with other services to ensure accurate and up-to-date order information.")


@app.get("/")
def read_root():
    return {"Hello": "Order Service"}


@app.post("/orders/", response_model=Order)
async def create_new_order(
    order: Order,
    session: Annotated[Session, Depends(get_session)],
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
) -> Order:
    try:
        order_dict = {field: getattr(order, field)
                        for field in order.dict()}
        order_json = json.dumps(order_dict).encode("utf-8")
        await producer.send_and_wait("orders", order_json)
        session.add(order)
        session.commit()
        session.refresh(order)
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/orders/", response_model=list[Order])
def read_orders(session: Annotated[Session, Depends(get_session)]):
    try:
        orders = session.exec(select(Order)).all()
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/orders/{order_id}", response_model=Order)
def read_order_by_id(order_id: int, session: Annotated[Session, Depends(get_session)]):
    try:
        order = session.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/orders/{order_id}", response_model=Order)
def update_order(
    order_id: int,
    updated_order: Order,
    session: Annotated[Session, Depends(get_session)]
) -> Order:
    try:
        order = session.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="order not found")

        order_data = updated_order.dict(exclude_unset=True)
        for key, value in order_data.items():
            setattr(order, key, value)

        session.add(order)
        session.commit()
        session.refresh(order)
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/orders/{order_id}")
def delete_order(order_id: int, session: Annotated[Session, Depends(get_session)]):
    try:
        order = session.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Product not found")

        session.delete(order)
        session.commit()
        return {"detail": "Order deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
