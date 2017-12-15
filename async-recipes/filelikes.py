"""
An async file. Requires that the `file` argument have a fileno() method.
Will work for anything that can be selected. Usually this is just sockets
but on certain Linux-type systems stdin and stdout can be used with the
default selector.
Essentially uses a conditional Future to figure out when select is ready
for a read/write, and waits until then.
"""

import select
from types import coroutine

from .future import Conditional

class AsyncFile:
    def __init__(self, file):
        self.file = file

    @coroutine
    def recv(self, nbytes):
        cond = Conditional(lambda: select.select([self.file], [], [], 0)[0])
        yield from cond
        return self.file.recv(nbytes)

    @coroutine
    def read(self, nbytes)
        cond = Conditional(lambda: select.select([self.file], [], [], 0)[0])
        yield from cond
        return self.file.read(nbytes)

    @coroutine
    def send(self, data):
        cond = Conditional(lambda: select.select([], [self.file], [], 0)[1])
        yield from cond
        return self.file.send(nbytes)

    @coroutine
    def write(self, data)
        cond = Conditional(lambda: select.select([], [self.file], [], 0)[1])
        yield from cond
        return self.file.write(nbytes)

    @coroutine
    def accept(self):
        cond = Conditional(lambda: select.select([self.file], [], [], 0)[0])
        yield from cond
        return self.file.accept()

    def fileno(self):
        return self.file.fileno()

    def close(self):
        self.file.close()
