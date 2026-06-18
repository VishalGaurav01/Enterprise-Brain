from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from env import Env

env = Env()

DATABASE_URL = env.postgres.url
print(f"Connecting to database at: {DATABASE_URL}")
engine = create_engine(DATABASE_URL)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
Base = declarative_base()

try:
    from core.db_events import setup_db_events
    setup_db_events()
except ImportError:
    pass