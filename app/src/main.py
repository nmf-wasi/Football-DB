from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.routers import users
from app.routers import players, teams, matches, leagues, country
from app.middleware.rate_limitter import rate_limitter
from app.core.logging import setup_logging
from app.middleware.logging import logging_middleware
import logging

setup_logging()
app = FastAPI()

app.middleware("http")(logging_middleware)
app.middleware("http")(rate_limitter)

logger = logging.getLogger(__name__)


# global exception handler and logging
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled error on {request.method} {request.url.path}: {exc}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occured!",
        },
    )


app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(players.router, prefix="/api/players", tags=["players"])
app.include_router(teams.router, prefix="/api/teams", tags=["teams"])
app.include_router(matches.router, prefix="/api/matches", tags=["matches"])
app.include_router(leagues.router, prefix="/api/leagues", tags=["leagues"])
app.include_router(country.router, prefix="/api/countries", tags=["countries"])


@app.get("/")
def home():
    return {"Author: Wasi"}
