import asyncio
from urllib import parse
import multiprocessing as mp
from datetime import datetime, timedelta
from time import sleep
from enum import Enum

import requests

BASE_URL = "http://localhost:8099/"


class Paths(str, Enum):
    SLEEPY = "sleepy/zzz"
    SLEEPY_ASYNCIO_TO_THREAD = "sleepy/zzz/async"
    SLEEPY_FAKE_ASYNC = "sleepy/zzz/async/fake"


def __prepare_main_process():
    mp.set_start_method("spawn")


def __sleep_till_start(start_datetime_str: str, step_ms=0.04):
    start_datetime = datetime.fromisoformat(start_datetime_str)
    while datetime.now() < start_datetime:
        sleep(step_ms)


def __request_sleepy(
    queue: mp.Queue, start_datetime_str: str, url: str, ms: int, id: str
):
    __sleep_till_start(start_datetime_str)
    response = requests.get(url, params={"ms": ms, "id": id})
    if response.status_code != 200:
        raise RuntimeError(
            f"response not 200: status code {response.status_code}: {response.text}"
        )
    if response.json() != id:
        raise RuntimeError(f"wrong id returned. expected {id} but got {response.text}")
    queue.put(id)


def count_threads(
    sleep_seconds=5, time_shield_seconds=2, max_threads=100, url_path=Paths.SLEEPY
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
    __prepare_main_process()
    # sync
    threads_cnt = count_threads(
        sleep_seconds=5, time_shield_seconds=4, max_threads=100, url_path=Paths.SLEEPY
    )
    print(f"number of threads that executed our requests: {threads_cnt}. method: sync")

    # asyncio.to_thread
    threads_cnt = count_threads(
        sleep_seconds=5,
        time_shield_seconds=4,
        max_threads=100,
        url_path=Paths.SLEEPY_ASYNCIO_TO_THREAD,
    )
    print(
        f"number of threads that executed our requests: {threads_cnt}. method: asyncio.to_thread"
    )

    # async fake
    threads_cnt = count_threads(
        sleep_seconds=5,
        time_shield_seconds=4,
        max_threads=100,
        url_path=Paths.SLEEPY_FAKE_ASYNC,
    )
    print(
        f"number of threads that executed our requests: {threads_cnt}. method: run sync in async"
    )


if __name__ == "__main__":
    _count_threads()
