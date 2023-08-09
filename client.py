import asyncio
from urllib import parse
import multiprocessing as mp
from datetime import datetime, timedelta
from time import sleep
from enum import Enum

import requests
import platform_consts as Const

BASE_URL = "http://localhost:8099/"


class _Path(str, Enum):
    SLEEPY = "sleepy/zzz"
    SLEEPY_ASYNCIO_TO_THREAD = "sleepy/zzz/async"
    SLEEPY_FAKE_ASYNC = "sleepy/zzz/async/fake"
    DB_DROP = "db/drop"
    DB_INIT = "db/init"
    DB_POPULATE = "db/populate"
    DB_POSTGRES_SLEEP = "db/query/sleep/postgres"


def __prepare_main_process():
    mp.set_start_method("spawn")


def __sleep_till_start(start_datetime_str: str, step_ms=0.04):
    start_datetime = datetime.fromisoformat(start_datetime_str)
    while datetime.now() < start_datetime:
        sleep(step_ms)


def __handle_response(
    queue: mp.Queue,
    response: requests.Response,
    expected_id: str,
    queue_failed: mp.Queue = None,
):
    if response.status_code != 200:
        if queue_failed is not None:
            return queue_failed.put(id)
        raise RuntimeError(
            f"response not 200: status code {response.status_code}: {response.text}"
        )
    if response.json() != expected_id:
        if queue_failed is not None:
            return queue_failed.put(id)
        raise RuntimeError(f"wrong id returned. expected {id} but got {response.text}")
    queue.put(id)


def __request_sleepy(
    queue: mp.Queue, start_datetime_str: str, url: str, ms: int, the_id: str
):
    __sleep_till_start(start_datetime_str)
    response = requests.get(url, params={"ms": ms, "id": the_id})
    __handle_response(queue, response, the_id)


def count_threads(
    sleep_seconds=5, time_shield_seconds=2, max_threads=100, url_path=_Path.SLEEPY
):
    """counts how many threaded tasks gets completed in backend.
    :param sleep_seconds: how many seconds shall the backend thread sleep
    :param time_shield_seconds: how many seconds to wait after first thread sleep-time
    :param with how many threads attempt the experiment
    :return: count of threads that got executed in time"""

    # prepare
    url = parse.urljoin(BASE_URL + "/", url_path)
    # using asyncio.to_thread reduces number of threads by 2
    # url = parse.urljoin(BASE_URL + "/", "sleepy/zzz/async")
    time_start = datetime.now() + timedelta(seconds=time_shield_seconds)
    time_start_str = time_start.isoformat()

    # create processes
    queue = mp.Queue()
    processes = [
        mp.Process(
            target=__request_sleepy,
            args=(queue, time_start_str, url, sleep_seconds * 1000, f"id-{i}"),
        )
        for i in range(max_threads)
    ]
    [proc.start() for proc in processes]

    # wait while processes are testing capability
    __sleep_till_start(time_start_str, step_ms=0.01)
    sleep(sleep_seconds)
    sleep(time_shield_seconds)

    # kill and collect
    [proc.kill() for proc in processes]

    answered_threads_cnt = 0
    while True:
        try:
            queue.get_nowait()
            answered_threads_cnt += 1
        except Exception:
            break

    return answered_threads_cnt


def _count_threads():
    # sync
    threads_cnt = count_threads(
        sleep_seconds=5, time_shield_seconds=4, max_threads=100, url_path=_Path.SLEEPY
    )
    print(f"number of threads that executed our requests: {threads_cnt}. method: sync")

    # asyncio.to_thread
    threads_cnt = count_threads(
        sleep_seconds=5,
        time_shield_seconds=4,
        max_threads=100,
        url_path=_Path.SLEEPY_ASYNCIO_TO_THREAD,
    )
    print(
        f"number of threads that executed our requests: {threads_cnt}. method: asyncio.to_thread"
    )

    # async fake
    threads_cnt = count_threads(
        sleep_seconds=5,
        time_shield_seconds=4,
        max_threads=100,
        url_path=_Path.SLEEPY_FAKE_ASYNC,
    )
    print(
        f"number of threads that executed our requests: {threads_cnt}. method: run sync in async"
    )


def _init_db(user_count=200, max_messages_per_user=2):
    r = requests.delete(parse.urljoin(BASE_URL + "/", _Path.DB_DROP))
    assert r.status_code == 200, r.text
    r = requests.post(parse.urljoin(BASE_URL + "/", _Path.DB_INIT))
    assert r.status_code == 200, r.text
    print("requesting a population...")
    r = requests.post(
        parse.urljoin(BASE_URL + "/", _Path.DB_POPULATE),
        params={
            "user_count": user_count,
            "max_messages_per_user": max_messages_per_user,
        },
    )
    assert r.status_code == 200, r.text
    print("population done.")


def __connect_db(queue: mp.Queue, queue_failed: mp.Queue, path: str, the_id: str):
    response = requests.get(
        url=parse.urljoin(BASE_URL + "/", path), params={"id": the_id}
    )
    __handle_response(queue, response, the_id, queue_failed)


def count_db_connections(url: str, time_shield_seconds: int, max_requests: int):
    # create processes
    queue = mp.Queue()
    queue_failed = mp.Queue()
    processes = [
        mp.Process(
            target=__connect_db,
            args=(queue, queue_failed, url, f"id-{i}"),
        )
        for i in range(max_requests)
    ]
    [proc.start() for proc in processes]

    # wait while processes are testing capability
    print("requesting db")
    sleep(Const.SQL_SLEEP_SECONDS)
    print("shielding db")
    sleep(time_shield_seconds)

    # kill and collect
    [proc.kill() for proc in processes]

    answered_db_cnt = 0
    while True:
        try:
            queue.get_nowait()
            answered_db_cnt += 1
        except Exception:
            break

    failed_db_cnt = 0
    while True:
        try:
            queue_failed.get_nowait()
            failed_db_cnt += 1
        except Exception:
            break

    return answered_db_cnt, failed_db_cnt


if __name__ == "__main__":
    __prepare_main_process()
    # _count_threads()
    _init_db(user_count=200, max_messages_per_user=2)
    max_requests = 41
    c, c_bad = count_db_connections(
        url=_Path.DB_POSTGRES_SLEEP,
        time_shield_seconds=Const.SQL_SLEEP_SECONDS // 2,
        max_requests=max_requests,
    )
    print(
        f"{c}/{max_requests} DB connections succeeded. {c_bad} failed. {max_requests - c - c_bad} did not finish."
    )
