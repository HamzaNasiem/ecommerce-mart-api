#main.py
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlmodel import Session, select
from fastapi import FastAPI, Depends, HTTPException
from app.models import Payment
from app.db_engine import create_db_and_tables, get_session
from app.kafka import consume_messages, get_kafka_producer
from stripe import PaymentIntent, StripeError, stripe
from app import settings
import asyncio
import json

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating tables..")
    task = asyncio.create_task(consume_messages('payments', 'broker:19092'))
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan, title="Payment Service", version="0.0.1",
              description="The Payment Service API processes payments and manages transaction records. It provides endpoints for handling payment transactions, recording payment details, and ensuring secure financial operations. This service integrates with other services to manage transaction data and ensure accurate financial processing.")

# Initialize Stripe API with your API key
stripe.api_key = settings.STRIPE_API_KEY


@app.get("/")
def read_root():
    return {"Hello": "Payment Service"}


@app.post("/payments/stripe/", response_model=Payment)
async def create_payment_stripe(amount: int, session: Session = Depends(get_session),
                                producer=Depends(get_kafka_producer)):
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            payment_method_types=["card"]
        )
        payment = Payment(amount=amount, payment_method="Stripe")
        session.add(payment)
        session.commit()
        session.refresh(payment)
        return payment
    except StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/payments/creditcard/", response_model=Payment)
async def create_payment_credit_card(payment: Payment, session: Session = Depends(get_session),
                                     producer=Depends(get_kafka_producer)):
    try:
        payment_dict = {field: getattr(payment, field)
                        for field in payment.dict()}
        payment_json = json.dumps(payment_dict).encode("utf-8")
        await producer.send_and_wait("payments", payment_json)
        session.add(payment)
        session.commit()
        session.refresh(payment)
        return payment
    except HTTPException as e:
        raise e


@app.get("/payments/", response_model=list[Payment])
def read_payments(session: Session = Depends(get_session)):
    try:
        payments = session.exec(select(Payment)).all()
        return payments
    except HTTPException as e:
        raise e


@app.get("/payments/{payment_id}", response_model=Payment)
def read_payment(payment_id: int, session: Session = Depends(get_session)):
    try:
        payment = session.exec(select(Payment).filter(
            Payment.id == payment_id)).first()
        if payment is None:
            raise HTTPException(status_code=404, detail="Payment not found")
        return payment
    except HTTPException as e:
        raise e


