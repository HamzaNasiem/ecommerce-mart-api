#main.py

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlmodel import Session, select
from fastapi import FastAPI, Depends, HTTPException
from app.models import Product
from app.db_engine import create_db_and_tables, get_session
from app.kafka import consume_messages, get_kafka_producer
import asyncio
import json

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating tables..")
    task = asyncio.create_task(consume_messages('inventory', 'broker:19092'))
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan, title="Inventory Service", version="0.0.1",
              description="This is the Inventory Service API, which handles products, warehouses, and stock management. It includes CRUD operations for managing inventory data and integrates with Kafka for real-time messaging.")

@app.get("/")
def read_root():
    return {"Hello": "Inventory Service"}

@app.post("/products/", response_model=Product)
async def create_product(product: Product, session: Session = Depends(get_session),
                         producer = Depends(get_kafka_producer)):
    try:
        product_dict = {field: getattr(product, field) for field in product.dict()}
        product_json = json.dumps(product_dict).encode("utf-8")
        await producer.send_and_wait("inventory", product_json)
        session.add(product)
        session.commit()
        session.refresh(product)
        return product
    except HTTPException as e:
        raise e

@app.get("/products/", response_model=list[Product])
def read_products(session: Session = Depends(get_session)):
    try:
        products = session.exec(select(Product)).all()
        return products
    except HTTPException as e:
        raise e

@app.get("/products/{product_id}", response_model=Product)
def read_product(product_id: int, session: Session = Depends(get_session)):
    try:
        product = session.exec(select(Product).filter(Product.id == product_id)).first()
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except HTTPException as e:
        raise e

@app.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: int, product: Product, session: Session = Depends(get_session),
                         producer = Depends(get_kafka_producer)):
    try:
        existing_product = session.exec(select(Product).filter(Product.id == product_id)).first()
        if existing_product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        
        for field, value in product.dict(exclude_unset=True).items():
            setattr(existing_product, field, value)
        
        session.add(existing_product)
        session.commit()
        
        product_dict = {field: getattr(existing_product, field) for field in existing_product.dict()}
        product_json = json.dumps(product_dict).encode("utf-8")
        await producer.send_and_wait("inventory", product_json)
        
        session.refresh(existing_product)
        return existing_product
    except HTTPException as e:
        raise e

@app.delete("/products/{product_id}")
def delete_product(product_id: int, session: Session = Depends(get_session),
                   producer = Depends(get_kafka_producer)):
    try:
        product = session.exec(select(Product).filter(Product.id == product_id)).first()
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        
        session.delete(product)
        session.commit()
        
        product_dict = {field: getattr(product, field) for field in product.dict()}
        product_json = json.dumps(product_dict).encode("utf-8")
        producer.send_and_wait("inventory", product_json)
        
        return {"message": "Product deleted successfully"}
    except HTTPException as e:
        raise e


