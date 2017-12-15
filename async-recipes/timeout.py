"""
Wrap a coroutine in an awaitable timeout. It will intercept
all send/throw calls and any advance of the generator.
A little more meta than it should be.

This will as long as the task is still being processed.
For example, if there is an asyncio.sleep() and it passes
the mark, it will wait the full time of the sleep and THEN
raise. This is because when asyncio sees a sleep, instead
of leaving it to be processed with every loop to check on
the status, it waits until it is finished to add it back.

This will work with the universal sleep from sleep.py.
However, the universal sleep and sleep forever may take
up more resources to process than a normal sleep. This is
because with each loop it needs to be checked and advance
the generator, whereas with many async platforms, there
is no need to use the generator to check if it is complete.

Example usage:

```python
from sleep import sleepinf

async def my_func():
    await timeout(sleepinf(), 10)
```
This makes sleepinf act like a normal sleep, cutting out
at 10 seconds and raising.

This may also be used with socked waits like seen in filelikes.py

```python
from filelikes import AsyncFile
my_file = AsyncFile(...)

async def read_timeout(async_file):
    return await timeout(async_file.read(), 20)

await read_timeout(my_file)
```

This will attempt to read from the async file, and if it does
not successfully within 20 seconds, it will cancel and raise a
TimeoutError
"""


from time import monotonic

class timeout:
    def __init__(self, coro, timeout):
        if hasattr(coro, "__await__"):
            self._coro = coro.__await__()
        else:
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
            return self._coro.send(data)
        raise TimeoutError

    def throw(self, data):
        if monotonic() < self._finish:
            return self._coro.throw(data)
        raise TimeoutError
