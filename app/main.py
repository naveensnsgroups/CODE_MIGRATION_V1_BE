from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.config import settings
from app.core.database import db

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to DB
    db.connect_to_mongo()
    yield
    # Shutdown: Close Connection
    db.close_mongo_connection()

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# Register CORS Middleware
app.add_middleware(

    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Main API Router
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": f"Welcome to the {settings.PROJECT_NAME} API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
