from fastapi import APIRouter

router = APIRouter(prefix="/players", tags=["Players"])

@router.get("/")
def list_players():
    return {"message": "This will list player data soon!"}
