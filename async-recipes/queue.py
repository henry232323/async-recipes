"""
Several queues to be used, including a FIFO/LIFO regular queue and
a Heap Queue, which both wait until an operation may be done. If the
queue is full, wait until a spot clears to add. If the queue is empty,
wait until an item is added to pop.
"""


from collections import deque
from heapq import heappush, heappop

from .future import Future
from types import coroutine


class QueueWouldBlock(Exception):
    pass


class Queue:
    def __init__(self, size=0, lifo=False):
        self._lifo = lifo
        self.size = size
        self._getters = deque()
        self._putters = deque()
        self._queue = deque()

    def __len__(self):
        return len(self._queue)

    def empty(self):
        return not self._queue

    def full(self):
        return self.size and len(self._queue) == self.size

    async def get(self):
        if not self.empty():
            result = self._pop()
            if self._putters:
                future, item = self._putters.popleft()
                while future.cancelled:
                    future, item = self._putters.popleft()
                self._append(item)
                future.set_result(None)
            return result

        future = Future()
        self._getters.append(future)
        return await future

    async def put(self, item):
        if not self.full():
            if self._getters:
                getter = self._getters.popleft()
                while getter.cancelled:
                    getter = self._getters.popleft()
                getter.set_result(item)
                return
            self._append(item)
            return

        future = Future()
        self._putters.append((future, item))
        return await future

    def get_nowait(self):
        if self.empty():
            raise QueueWouldBlock("Queue is empty!")
        return self._pop()

    def put_nowait(self, item):
        if self.full():
            raise QueueWouldBlock("Queue is full!")
        return self._append(item)

    def _pop(self):
        if self._lifo:
            return self._queue.pop()
        return self._queue.popleft()

    def _append(self, item):
        self._queue.append(item)

    def setlifo(self, bool: bool):
        self._lifo = bool

    async def __anext__(self):
        return await self.get()

    async def __aiter__(self):
        return self

    @coroutine
    def join(self):
        while self._queue:
            yield


class HeapQueue(Queue):
    def __init__(self, size=0):
        self.size = size
        self._getters = deque()
        self._putters = deque()
        self._queue = list()

    def _pop(self):
        return heappop(self._queue)

    def _append(self, item):
        return heappush(self._queue, item)

    @property
    def setlifo(self):
        raise AttributeError("HeapQueue doesn't implement LIFO!")
