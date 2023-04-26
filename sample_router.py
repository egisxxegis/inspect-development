from fastapi import APIRouter

router = APIRouter(
    prefix="",
    tags=["sample"],
)


@router.get("")
async def list_runtimes():
    return "q"
