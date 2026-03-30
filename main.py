from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Backend!"}

@app.get("/status")
def get_status():
    return {"status": "online", "framework": "FastAPI", "manager": "uv"}
