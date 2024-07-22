
#db_engine.py
from app import settings
from sqlmodel import create_engine, Session

connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg")

engine = create_engine(connection_string, connect_args={}, pool_recycle=300)


def create_db_and_tables():
    from app.models import Payment  # Importing here to avoid circular import
    Payment.__table__.create(bind=engine, checkfirst=True)


def get_session():
    with Session(engine) as session:
        yield session


