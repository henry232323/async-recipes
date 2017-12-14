from time import monotonic

class timeout:
    def __init__(self, coro, timeout):
        self._coro = coro
        self._finish = monotonic() + timeout

    def __iter__(self):
        try:
            val = None
            while monotonic() < self._finish:
                val = yield self._coro.send(val)
            else:
                raise TimeoutError
        except StopIteration as err:
            return err.value

    __await__ = __iter__

    def send(self, data):
        if monotonic() < self._finish:
            return self._coro.send(val)
        raise TimeoutError

    def throw(self, data):
        if monotonic() < self._finish:
            return self._coro.throw(val)
        raise TimeoutError
