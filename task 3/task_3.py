from concurrent.futures.thread import ThreadPoolExecutor
from threading import Thread, Lock


class Counter:

    def __init__(self):
        self.lock = Lock()
        self.value = 0

    def inc(self):
        with self.lock:
            self.value += 1


def function(counter: Counter, value: int):
    for _ in range(value):
        counter.inc()


def main():
    counter = Counter()

    with ThreadPoolExecutor(max_workers=2) as executor:
        for i in range(5):
            executor.submit(function, counter, 1000000)
    print("----------------------", counter.value)


main()
