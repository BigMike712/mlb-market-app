from fastapi import FastAPI
from app.routers import players, investments, frontend
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI(title = "MLB The Show Market Tracker")

# Register player routes
app.include_router(players.router)
app.include_router(investments.router)
app.include_router(frontend.router)

# Frontend stuff
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

