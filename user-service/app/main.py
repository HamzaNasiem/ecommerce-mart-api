# main.py
from contextlib import asynccontextmanager
from typing import Annotated
from sqlmodel import Session, select
from fastapi import FastAPI, Depends, HTTPException
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer
import asyncio
import json

from app.models import User
from app.db_engine import create_db_and_tables, get_session
from app.kafka import consume_messages, get_kafka_producer


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating tables..")
    # loop.run_until_complete(consume_messages('todos', 'broker:19092'))
    task = asyncio.create_task(consume_messages('users', 'broker:19092'))
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="User Service",
              version="0.0.1", description="The User Service API is responsible for managing user authentication, registration, and profiles. It handles user sign-ups, logins, and profile updates, ensuring secure and efficient user management. This service provides endpoints for user-related operations, including authentication and profile management, and integrates with other services to maintain user information across the system.")


@app.get("/")
def read_root():
    return {"Hello": "User Service"}


@app.post("/users/", response_model=User)
async def create_new_user(
    user: User,
    session: Annotated[Session, Depends(get_session)],
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
) -> User:
    try:
        user_dict = {field: getattr(user, field) for field in user.dict()}
        user_json = json.dumps(user_dict).encode("utf-8")
        await producer.send_and_wait("users", user_json)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users/", response_model=list[User])
def read_users(session: Annotated[Session, Depends(get_session)]):
    try:
        users = session.exec(select(User)).all()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users/{user_id}", response_model=User)
def read_user_by_id(user_id: int, session: Annotated[Session, Depends(get_session)]):
    try:
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
    session: Annotated[Session, Depends(get_session)]
) -> User:
    try:
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
def delete_user(user_id: int, session: Annotated[Session, Depends(get_session)]):
    try:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        session.delete(user)
        session.commit()
        return {"detail": "User deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



