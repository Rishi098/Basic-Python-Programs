import threading

class Counter:
    def __init__(self):
        self.count = 0
        self.lock = threading.Lock()  # Lock to synchronize access to the critical section

    def increment(self):
        with self.lock:  # Critical section, only one thread can enter at a time
            self.count += 1

def worker(counter):
    for _ in range(1000):
        counter.increment()

if __name__ == "__main__":
    counter = Counter()

    # Create two threads that will increment the counter
    t1 = threading.Thread(target=worker, args=(counter,))
    t2 = threading.Thread(target=worker, args=(counter,))

    t1.start()
    t2.start()

    # Wait for both threads to complete
    t1.join()
    t2.join()

    # The count should be 2000 since both threads increment it 1000 times
    print(f"Final count: {counter.count}")
