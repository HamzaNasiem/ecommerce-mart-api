#main.py
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator
from sqlmodel import Session, select
from fastapi import FastAPI, Depends, HTTPException, status
from aiokafka import AIOKafkaProducer
import asyncio
import json
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

from app.models import User, Token
from app.db_engine import create_db_and_tables, get_session
from app.kafka import consume_messages, get_kafka_producer
from app.auth import authenticate_user, create_access_token, get_current_user, get_password_hash
from app import settings

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating tables...")
    task = asyncio.create_task(consume_messages('users', 'broker:19092'))
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan, title="User Service",
              version="0.0.1", description="The User Service API is responsible for managing user authentication, registration, and profiles.")

@app.get("/")
def read_root():
    return {"Hello": "User Service"}


@app.post("/users/register", response_model=User)
async def register_user(
    user: User,
    session: Annotated[Session, Depends(get_session)],
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
) -> User:
    try:
        existing_user = session.exec(select(User).where(User.user_email == user.user_email)).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")

        user.password = get_password_hash(user.password)  # Hashing the password
        session.add(user)
        session.commit()
        session.refresh(user)

        user_dict = user.dict()
        user_dict.pop("password")  # Don't publish the password
        user_json = json.dumps(user_dict).encode("utf-8")
        await producer.send_and_wait("users", user_json)

        return user
    except Exception as e:
        print(f"Error occurred during user registration: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/users/", response_model=list[User])
def read_users(
    session: Annotated[Session, Depends(get_session)],
    current_user: User = Depends(get_current_user)  # Secure the endpoint
):
    try:
        users = session.exec(select(User).where(User.id == current_user.id)).all()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}", response_model=User)
def read_user_by_id(
    user_id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: User = Depends(get_current_user)  # Secure the endpoint
):
    try:
        if user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this user data")
        
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/users/{user_id}", response_model=User)
def update_user(
    user_id: int,
    updated_user: User,
    session: Annotated[Session, Depends(get_session)],
    current_user: User = Depends(get_current_user)  # Secure the endpoint
) -> User:
    try:
        if user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this user data")
        
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user_data = updated_user.dict(exclude_unset=True)
        for key, value in user_data.items():
            setattr(user, key, value)

        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: User = Depends(get_current_user)  # Secure the endpoint
):
    try:
        if user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this user data")
        
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        session.delete(user)
        session.commit()
        return {"detail": "User deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
