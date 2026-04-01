from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.config import settings
from app.core.database import db

app = FastAPI(title=settings.PROJECT_NAME)

@app.on_event("startup")
def startup_db_client():
    db.connect_to_mongo()

@app.on_event("shutdown")
def shutdown_db_client():
    db.close_mongo_connection()

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
