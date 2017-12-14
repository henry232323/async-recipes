from types import coroutine
import typing
from time import monotonic

@coroutine
def sleep(seconds: typing.Union[float, int]):
    """Sleep for a specified amount of time. Will work with any library."""
    if seconds == 0:
        yield
    elif seconds == inf:
        yield from sleepinf()
    else:
        end = monotonic() + seconds
        while end >= monotonic():
            yield

@coroutine
def sleepinf():
    try:
        while True:
            yield
    except:
        return
