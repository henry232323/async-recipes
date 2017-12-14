"""
An async file. Requires that the `file` argument have a fileno() method.
Will work for anything that can be selected. Usually this is just sockets
but on certain Linux-type systems stdin and stdout can be used with the
default selector.

Essentially uses a conditional Future to figure out when select is ready
for a read/write, and waits until then.
"""

import select

from .future import Conditional

class AsyncFile:
    def __init__(self, file):
        self.file = file

    async def recv(self, nbytes):
        cond = Conditional(lambda: select.select([self.file], [], [], 0)[0])
        await cond
        return self.file.recv(nbytes)

    async def read(self, nbytes)
        cond = Conditional(lambda: select.select([self.file], [], [], 0)[0])
        await cond
        return self.file.read(nbytes)

    async def send(self, data):
        cond = Conditional(lambda: select.select([], [self.file], [], 0)[1])
        await cond
        return self.file.send(nbytes)

    async def write(self, data)
        cond = Conditional(lambda: select.select([], [self.file], [], 0)[1])
        await cond
        return self.file.write(nbytes)

    def fileno(self):
        return self.file.fileno()

    def close(self):
        self.file.close()
