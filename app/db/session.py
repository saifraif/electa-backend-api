from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# This should come from an environment variable
SQLALCHEMY_DATABASE_URL = "postgresql://electa:electa@db:5432/electa_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()