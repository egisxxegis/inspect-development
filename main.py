import uvicorn
from fastapi import FastAPI, APIRouter

from sample_router import router
from db_router import router as db_router

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


if __name__ == "__main__":
    # models.Base.metadata.create_all(bind=engine)

    app = FastAPI()

    include_routers(app)
    set_settings(app)

    uvicorn.run(app, host=Const.HOST, port=Const.PORT)
