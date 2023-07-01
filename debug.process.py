import multiprocessing as mp
import os
import time


def foo(q: mp.Queue, name: str, sleep_seconds: int | float):
    time.sleep(sleep_seconds)
    q.put(name)


if __name__ == "__main__":
    mp.set_start_method("spawn")
    q = mp.Queue()
    ps = [mp.Process(target=foo, args=(q, f"{i}", i / 100)) for i in range(200)]
    [p.start() for p in ps]
    time.sleep(3)
    [p.kill() for p in ps]
    for _ in range(200):
        print(q.get())
