from fastapi import APIRouter

router = APIRouter(
    prefix="/move",
    tags=["movement"],
)


@router.get("/direction/<dir:str>")
async def direction(dir: str) -> bool:
    return True
