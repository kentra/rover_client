from fastapi import APIRouter

router = APIRouter(prefix="/states",tags=["states"],)


@router.get("/hello-world")
async def hello_world():
    return {"Hello": "World"}
