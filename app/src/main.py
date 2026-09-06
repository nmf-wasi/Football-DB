from fastapi import FastAPI
from app.routers import users

app = FastAPI()
app.include_router(users.router, prefix="/api/users", tags=["users"])


@app.get("/")
def home():
    return {"Author: Wasi"}
