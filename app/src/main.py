from fastapi import FastAPI
from app.routers import users
from app.routers import players
app = FastAPI()
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(players.router, prefix="/api/players", tags=["players"])

@app.get("/")
def home():
    return {"Author: Wasi"}

