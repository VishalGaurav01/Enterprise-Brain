from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from core.database import get_db
from apps.gateway.router import gateway_router
from core.db_events import setup_db_events

# Initialize SQLAlchemy event listeners for Kafka sync
setup_db_events()

app = FastAPI(title="Brain API")

# Centralized API Gateway
app.include_router(gateway_router)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/db-test")
def test_db(db=next(get_db())):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "Database connection successful"}
    except Exception as e:
        return {"status": "Database connection failed", "error": str(e)}
