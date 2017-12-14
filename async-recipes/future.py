"""
Three classes.

The First, a Future will wait until it's result is set or an error is set
    If the result is set, it will return the result. If an error is set, it will
    raise the error.

The Second, a Task wraps a coroutine or another Future, and will pass everything
    forward until it is done.

The Third, a Conditional Future, it will wait until its condition becomes true,
    checking with each pass of the event loop.
"""


import typing

class Future:
    def __init__(self):
        """An awaitable that will yield until an exception or result is set."""
        self.__name__ = self.__class__.__name__
        self._data = None
        self._result = None
        self._error = None
        self.complete = False
        self.cancelled = False
        self._running = False
        self._callback = None

    def running(self):
        return self._running

    def done(self):
        return self.complete

    def result(self):
        if self._error is not None:
            raise self._error
        if not self.complete:
            raise RuntimeError("Result isn't ready!")
        return self._result

    def set_result(self, data: typing.Any):
        if self.complete or self._error is not None:
            raise RuntimeError("Future already completed")
        self.complete = True
        self._result = data
        if self._callback:
            self._callback()

    def set_exception(self, exception: typing.Union[Exception, typing.Callable[..., Exception]]):
        if self.complete or self._error is not None:
            raise RuntimeError("Future already completed")
        self._error = exception

    def cancel(self):
        if self.cancelled:
            return True
        if self.complete:
            return False
        if self.running():
            return False
        self.cancelled = True
        self.set_exception(CancelledError)
        return True

    def __iter__(self):
        while not self.complete and self._error is None:
            yield
        return self.result()

    __await__ = __iter__

    def send(self, data):
        if not self.complete and self._error is None:
            return
        raise StopIteration(self.result())

    def add_done_callback(self, fn, *args, **kwargs):
        self._callback = partial(fn, args=args, kwargs=kwargs)

    def close(self):
        self._error = StopIteration("Closed!")


class Task(Future):
    def __init__(self, task: typing.Union[typing.Generator, typing.Awaitable], data: typing.Any):
        """A Future that wraps a coroutine or another future"""
        super().__init__()
        if hasattr(task, "__await__"):
            self._task = task.__await__()
        else:
            self._task = task
        self._data = data

    def __iter__(self):
        return self._task

    __await__ = __iter__

    def send(self, data):
        return self._task.send(data)

    def throw(self, exc):
        return self._task.throw(exc)

    def cancel(self):
        if self.cancelled:
            return True
        if self.complete:
            return False
        if self.running():
            return False
        try:
            self.throw(CancelledError)
        except CancelledError:
            self.cancelled = True
            self.set_exception(CancelledError)
            return True
        except StopIteration as err:
            self.set_result(err.value)
            return False
        else:
            return False

    def close(self):
        self._task.close()


class Conditional(Future):
    def __init__(self, condition: typing.Callable[..., bool]):
        """An awaitable that waits until the condition becomes true. Returns whatever the done callback returns"""
        super().__init__()
        self.condition = condition

    def __iter__(self):
        while not self.condition():
            yield
        return self.result()

    __await__ = __init__  # These just keep yielding / passing until our condition is true.

    def send(self, data):
        if not self.condition():
            return
        raise StopIteration(self.result())

    def result(self):
        if self._error is not None:
            raise self._error
        if not self.complete:
            raise RuntimeError("Result isn't ready!")
        return self._callback()
