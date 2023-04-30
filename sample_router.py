from fastapi import APIRouter, Query
from time import sleep
import asyncio
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


@router.get("/zzz/async")
async def sleepy_async(ms: int = Query(), id: str = Query()):
    return await asyncio.to_thread(sleepy, ms, id)
