from fastapi import FastAPI
from app.routers import players

app = FastAPI(title = "MLB The Show Market Tracker")

# Register player routes
app.include_router(players.router)