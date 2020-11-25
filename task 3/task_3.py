from threading import Thread, Lock


class Counter:

    def __init__(self):
        self.lock = Lock()
        self.value = 0

    def inc(self):
        with self.lock:
            self.value += 1


def function(counter: Counter, arg: int):
    for _ in range(arg):
        counter.inc()


def main():
    counter = Counter()
    threads = []
    for i in range(5):
        thread = Thread(target=function, args=(counter, 1000000,))
        thread.start()
        threads.append(thread)

    [t.join() for t in threads]
    print("----------------------", counter.value)


main()
