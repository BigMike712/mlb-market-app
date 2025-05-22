from fastapi import APIRouter

router = APIRouter(prefix="/players", tags=["Players"])

# When someone sends a GET request to the route /players/, call the function below:
@router.get("/")
def list_players():
    return {"message": "This will list player data soon!"}

@router.get("/test")
def say_hello():
    return {"message": "Hello from your API!"}