from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

DATABASE_URL = "sqlite:///./consultant.db"  # Using SQLite for now

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)
