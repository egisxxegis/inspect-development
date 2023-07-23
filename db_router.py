import random
import string

from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db, Base, engine
import models


router = APIRouter(prefix="/db", tags=["db", "database"])


@router.delete("/drop")
def drop_db():
    Base.metadata.drop_all(bind=engine)


@router.post("/init")
def init_db():
    Base.metadata.create_all(bind=engine)


@router.post("/populate")
def populate_db(
    db: Session = Depends(get_db),
    max_messages_per_user: int = Query(default=2),
    user_count: int = Query(default=156),
):
    Base.metadata.create_all(bind=engine)
    symbols = string.ascii_lowercase + string.digits + " _-"

    _random_str = lambda min_length, max_length: "".join(
        random.choices(symbols, k=random.randint(min_length, max_length))
    )

    # create users
    for user_i in range(user_count):
        db_user = models.User(name=_random_str(4, 20))
        db.add(db_user)
        db.flush()

        # create messages for each user
        for _ in range(max_messages_per_user):
            if random.randint(0, 1) == 1:
                "skip"
                break
            is_moderated = random.randint(0, 1) == 1 and user_i != 0
            db_message = models.Message(
                content=_random_str(50, 10000),
                user_id=db_user.id,
                moderator_id=random.randint(db_user.id - user_i, db_user.id - 1)
                if is_moderated
                else None,
            )
            db.add(db_message)

        db.commit()


@router.get("/query/status")
def query_status(db: Session = Depends(get_db)):
    try:
        users_cnt = db.query(models.User).count()
        messages_cnt = db.query(models.Message).count()
        first_user = db.query(models.User).order_by(models.User.id.asc()).first()
        last_user = db.query(models.User).order_by(models.User.id.desc()).first()

        return {
            "users_cnt": users_cnt,
            "messages_cnt": messages_cnt,
            "first_user": first_user,
            "last_user": last_user,
        }
    except:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "is DB even init'ed?"
        )


@router.get("/query/sleep/postgres")
def query_sleep_postgres(db: Session = Depends(get_db), id: int = Query()):
    try:
        q = db.query(func.now(), func.pg_sleep(10)).all()
    except Exception as ex:
        if "no such function" in str(ex).lower():
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "you sure db is on postgresql?"
            )
        else:
            raise ex
    print(q)
    print(q[0])
    return id
