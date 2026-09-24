from fastapi import FastAPI
from app.routers import users
from app.routers import players, teams, matches, leagues, country
from app.middleware.rate_limitter import rate_limitter

app = FastAPI()
app.middleware("http")(rate_limitter)
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(players.router, prefix="/api/players", tags=["players"])
app.include_router(teams.router, prefix="/api/teams", tags=["teams"])
app.include_router(matches.router, prefix="/api/matches", tags=["matches"])
app.include_router(leagues.router, prefix="/api/leagues", tags=["leagues"])
app.include_router(country.router, prefix="/api/countries", tags=["countries"])


@app.get("/")
def home():
    return {"Author: Wasi"}
