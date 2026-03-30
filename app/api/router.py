from app.api.endpoints import ingest, auth

api_router = APIRouter()

# Include Ingest Endpoint
api_router.include_router(ingest.router, prefix="/ingest", tags=["ingestion"])

# Include Auth Endpoint
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
