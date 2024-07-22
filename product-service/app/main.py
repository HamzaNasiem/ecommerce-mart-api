from contextlib import asynccontextmanager
from typing import Annotated
from sqlmodel import Session, select
from fastapi import FastAPI, Depends, HTTPException
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer
import asyncio
import json

from app.models import Product
from app.db_engine import create_db_and_tables, get_session
from app.kafka import consume_messages, get_kafka_producer
from app import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating tables..")
    create_db_and_tables()
    task = asyncio.create_task(consume_messages('products', settings.BOOTSTRAP_SERVER))
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan, title="Product Service", version="0.0.1", description="The Product Service API manages the product catalog, including CRUD operations for products. It provides endpoints for adding, updating, retrieving, and deleting product information. This service ensures the organization and maintenance of product data, allowing for seamless product management and integration with other services in the system.")

@app.get("/")
def read_root():
    return {"Hello": "Product Service"}

@app.post("/products/", response_model=Product)
async def create_new_product(
    product: Product,
    session: Annotated[Session, Depends(get_session)],
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
) -> Product:
    try:
        product_dict = {field: getattr(product, field) for field in product.dict()}
        product_json = json.dumps(product_dict).encode("utf-8")
        await producer.send_and_wait("products", product_json)
        session.add(product)
        session.commit()
        session.refresh(product)
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/", response_model=list[Product])
def read_products(session: Annotated[Session, Depends(get_session)]):
    try:
        products = session.exec(select(Product)).all()
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/{product_id}", response_model=Product)
def read_product_by_id(product_id: int, session: Annotated[Session, Depends(get_session)]):
    try:
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/products/{product_id}", response_model=Product)
def update_product(
    product_id: int, 
    updated_product: Product, 
    session: Annotated[Session, Depends(get_session)]
) -> Product:
    try:
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product_data = updated_product.dict(exclude_unset=True)
        for key, value in product_data.items():
            setattr(product, key, value)
        
        session.add(product)
        session.commit()
        session.refresh(product)
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/products/{product_id}")
def delete_product(product_id: int, session: Annotated[Session, Depends(get_session)]):
    try:
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        session.delete(product)
        session.commit()
        return {"detail": "Product deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
