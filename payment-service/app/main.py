# #main.py
# from contextlib import asynccontextmanager
# from typing import AsyncGenerator
# from sqlmodel import Session, select
# from fastapi import FastAPI, Depends, HTTPException
# from app.models import Payment
# from app.db_engine import create_db_and_tables, get_session
# from app.kafka import consume_messages, get_kafka_producer
# from stripe import PaymentIntent, StripeError, stripe
# from app import settings
# import asyncio
# import json

# app = FastAPI()


# @asynccontextmanager
# async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
#     print("Creating tables..")
#     task = asyncio.create_task(consume_messages('payments', 'broker:19092'))
#     create_db_and_tables()
#     yield

# app = FastAPI(lifespan=lifespan, title="Payment Service", version="0.0.1",
#               description="The Payment Service API processes payments and manages transaction records. It provides endpoints for handling payment transactions, recording payment details, and ensuring secure financial operations. This service integrates with other services to manage transaction data and ensure accurate financial processing.")

# # Initialize Stripe API with your API key
# stripe.api_key = settings.STRIPE_API_KEY


# @app.get("/")
# def read_root():
#     return {"Hello": "Payment Service"}


# @app.post("/payments/stripe/", response_model=Payment)
# async def create_payment_stripe(amount: int, session: Session = Depends(get_session),
#                                 producer=Depends(get_kafka_producer)):
#     try:
#         payment_intent = stripe.PaymentIntent.create(
#             amount=amount,
#             currency="usd",
#             payment_method_types=["card"]
#         )
#         payment = Payment(amount=amount, payment_method="Stripe")
#         session.add(payment)
#         session.commit()
#         session.refresh(payment)
#         return payment
#     except StripeError as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @app.post("/payments/creditcard/", response_model=Payment)
# async def create_payment_credit_card(payment: Payment, session: Session = Depends(get_session),
#                                      producer=Depends(get_kafka_producer)):
#     try:
#         payment_dict = {field: getattr(payment, field)
#                         for field in payment.dict()}
#         payment_json = json.dumps(payment_dict).encode("utf-8")
#         await producer.send_and_wait("payments", payment_json)
#         session.add(payment)
#         session.commit()
#         session.refresh(payment)
#         return payment
#     except HTTPException as e:
#         raise e


# @app.get("/payments/", response_model=list[Payment])
# def read_payments(session: Session = Depends(get_session)):
#     try:
#         payments = session.exec(select(Payment)).all()
#         return payments
#     except HTTPException as e:
#         raise e


# @app.get("/payments/{payment_id}", response_model=Payment)
# def read_payment(payment_id: int, session: Session = Depends(get_session)):
#     try:
#         payment = session.exec(select(Payment).filter(
#             Payment.id == payment_id)).first()
#         if payment is None:
#             raise HTTPException(status_code=404, detail="Payment not found")
#         return payment
#     except HTTPException as e:
#         raise e

# #main.py
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from fastapi import FastAPI, Depends, HTTPException, Request
from app.models import Payment
from app.db_engine import create_db_and_tables, get_session
from app.kafka import consume_messages, get_kafka_producer
from stripe import PaymentIntent, StripeError, stripe
from app import settings
import asyncio
import json

app = FastAPI()

stripe.api_key = settings.STRIPE_API_KEY
endpoint_secret = settings.STRIPE_ENDPOINT_SECRET


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating tables..")
    await asyncio.to_thread(create_db_and_tables)
    task = asyncio.create_task(consume_messages(
        settings.KAFKA_PAYMENT_TOPIC, settings.BOOTSTRAP_SERVER))
    yield
    task.cancel()
app = FastAPI(lifespan=lifespan, title="Payment Service", version="0.0.1",
              description="The Payment Service API processes payments and manages transaction records. It provides endpoints for handling payment transactions, recording payment details, and ensuring secure financial operations. This service integrates with other services to manage transaction data and ensure accurate financial processing.")


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


@app.post('/webhooks/stripe')
async def webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        print('PaymentIntent was successful!')
    else:
        print(f'Unhandled event type {event["type"]}')

    return JSONResponse(content={'success': True})


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
