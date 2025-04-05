from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Using direct parameters with explicit port
engine = create_engine(
    "postgresql+psycopg://",
    connect_args={
        "host": settings.database_hostname,
        "port": settings.database_port,
        "user": settings.database_username,
        "password": settings.database_password,
        "dbname": settings.database_name,
        "client_encoding": "utf8"
    },
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base() 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()