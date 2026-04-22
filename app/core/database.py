from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

    def connect_to_mongo(self):
        if not settings.MONGODB_URL:
            print("WARNING: MONGODB_URL not found in environment. Persistence disabled.")
            return
        
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB]
        print(f"Connected to MongoDB (Async): {settings.MONGODB_DB}")

    def close_mongo_connection(self):
        if self.client:
            self.client.close()
            print("MongoDB connection closed.")

db = Database()
