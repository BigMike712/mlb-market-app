from fastapi import FastAPI
from app.routers import players, investments

app = FastAPI(title = "MLB The Show Market Tracker")

# Register player routes
app.include_router(players.router)
app.include_router(investments.router)