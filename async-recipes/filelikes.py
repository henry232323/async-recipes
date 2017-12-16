"""
An async file. Requires that the `file` argument have a fileno() method.
Will work for anything that can be selected. Usually this is just sockets
but on certain Linux-type systems stdin and stdout can be used with the
default selector.
Essentially uses a conditional Future to figure out when select is ready
for a read/write, and waits until then.

`AsyncFile.connect`
This sets the socket to non-blocking, thus, using any recv method
while waiting on a connect will make it instantly ready (select will
assume ready to read) and then error. tl;dr Dont try to read before
you've connected.

What it does: waits until we can successfully get our peername. If
it errors, that means we arent connected, and need to try another pass.
If we get a different error (like failed to connect completely) it will
raise.
"""

import select
from types import coroutine
import errno

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
    def read(self, nbytes):
        cond = Conditional(lambda: select.select([self.file], [], [], 0)[0])
        yield from cond
        return self.file.read(nbytes)

    @coroutine
    def readwith(self, func, *args, **kwargs):
        """Read using a custom function, args will be forwarded. Will call the function when ready to read.
        AsyncFile.file to pass the underlying socket"""
        cond = Conditional(lambda: select.select([self.file], [], [], 0)[0])
        yield from cond
        return func(*args, **kwargs)

    @coroutine
    def send(self, data):
        cond = Conditional(lambda: select.select([], [self.file], [], 0)[1])
        yield from cond
        return self.file.send(data)

    @coroutine
    def write(self, data):
        cond = Conditional(lambda: select.select([], [self.file], [], 0)[1])
        yield from cond
        return self.file.write(data)

    @coroutine
    def accept(self):
        cond = Conditional(lambda: select.select([self.file], [], [], 0)[0])
        yield from cond
        return self.file.accept()

    @coroutine
    def connect(self, hostpair):
        self.file.setblocking(False)
        self.file.connect_ex(hostpair)
        while True:
            try:
                self.file.getpeername()
                break
            except OSError as err:
                if err.errno == errno.ENOTCONN:
                    yield
                else:
                    raise

        self.file.setblocking(True)

    def dup(self):
        return AsyncFile(self.file.dup())

    def makefile(self, mode='r', buffering=None, *, encoding=None, errors=None, newline=None):
        return AsyncFile(self.file.makefile(mode, buffering, encoding=encoding, errors=errors, newline=newline))

    def fileno(self):
        return self.file.fileno()

    def close(self):
        self.file.close()
