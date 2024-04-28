from threading import Lock, Timer


class BoundedTokenBucket:
    def __init__(self, capacity, refill_interval):
        self.capacity = capacity
        self.tokens = 0
        self.lock = Lock()
        self.refill_interval = refill_interval
        self.timer = Timer(self.refill_interval, self._refill_bucket)
        self.timer.start()

    def consume(self, tokens):
        with self.lock:
            if tokens <= self.tokens:
                self.tokens -= tokens
                return True
            else:
                return False

    def _refill_bucket(self):
        with self.lock:
            self.tokens = min(self.capacity, self.tokens + 1)
            self.timer = Timer(self.refill_interval, self._refill_bucket)
            self.timer.start()

    def stop(self):
        self.timer.cancel()


if __name__ == '__main__':
    bucket = BoundedTokenBucket()
