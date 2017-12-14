"""
Two coroutines for sleeping in an async loop. Instead of using loop 
internals will just pass until the timeout has been reached.

sleepinf will just pass until it is stopped or thrown an error.
If an error is thrown, it wont raise, instead it will just return

sleep will just act as a normal yield, allowing the loop to pass once
if seconds is 0 and thus wouldn't wait at all. If math.inf is passed
then it'll just run sleepinf. Otherwise, itll pass until the current time
surpasses the start time plus the wait time.
"""

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
