import asyncio
import json
from fastapi.responses import StreamingResponse
import requests
import uvicorn
from fastapi import Body, FastAPI, APIRouter, Query

from sample_router import router
from db_router import router as db_router
import time

# import models
# from database import engine
import platform_consts as Const
from config_logger import config_logger

config_logger()

root_router = APIRouter()


def include_routers(the_app: FastAPI) -> None:
    the_app.include_router(root_router)
    the_app.include_router(router)
    the_app.include_router(db_router)


def set_settings(the_app: FastAPI) -> None:
    pass


@root_router.get("/")
async def read_root():
    return {"Hello_from": "backend"}


@root_router.post("/proxy")
def proxy(
    full_url: str = Query(),
    body: None | str = Body(default=None),
    headers: None | dict = None,
    method: str = "GET",
):
    print(f"will get {full_url}")
    body = None if body == "string" else body
    headers = None if headers == {} else headers
    r = requests.request(method, full_url, data=body, headers=headers)
    print(f"got {r.status_code} {r.text}")
    return r.json()


@root_router.post("/pulsing_proxy")
async def pulsing_proxy(
    full_url: str = Query(),
    body: None | str = Body(default=None),
    headers: None | dict = None,
    method: str = "GET",
):
    future = asyncio.to_thread(
        proxy, full_url=full_url, body=body, headers=headers, method=method
    )

    async def noise():
        task = asyncio.create_task(future)
        yield '{\n"noise": "'
        while not task.done():
            yield "."
            await asyncio.sleep(0.1)

        yield '",\n"data": '
        yield json.dumps(task.result())
        yield "\n}"

    return StreamingResponse(noise(), media_type="json")


if __name__ == "__main__":
    # models.Base.metadata.create_all(bind=engine)

    app = FastAPI()

    include_routers(app)
    set_settings(app)

    uvicorn.run(app, host=Const.HOST, port=Const.PORT)
