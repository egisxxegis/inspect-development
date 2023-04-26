from fastapi import APIRouter, Query
from time import sleep
import logging

router = APIRouter(
    prefix="/sleepy",
    tags=["sample"],
)


@router.get("/zzz")
def sleepy(ms: int = Query(), id: str = Query()):
    s = ms / 1000
    print(f"will sleep {s} s. id = {id}")
    sleep(s)
    return id
