from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL)

session = sessionmaker(
    autocommit=False,
    bind=engine
)

def get_db():
    
    db = session()
    try:
        yield db
    finally:
        db.close()