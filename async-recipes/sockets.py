"""
This module provides two main functions.

First: `async_connect`

  Async connect aims to use the error codes provided by `socket.connect_ex`
    to determine whether the socket has connected, is still connecting, or
    has failed to connect.

  If any unexpected error code is returned, it is raised like a normal OSError
    (meaning a failure).

  The specific error codes excepted make sure that the socket does not block
    and will tell us if it has successfully connected.

  This code segment does not include a part on timeouts, though that should
    be simple to determine.

  Every time the error does not indicate that it is connected, but has not 
    failed, the coroutine yields to let another round of events process.

Second: `ssl_do_handshake`

  The function is fairly simple, if to perform the handshake it needs read or
    write to be ready, it will raise to ask for either one.

  Each time it raises the function will yield so other tasks may process, then
    will return once it does not raise.



"""

import socket
import errno
import ssl
from types import coroutine
from functools import wraps

yerrlist = [
    "EINPROGRESS",
    "WSAEINPROGRESS",
    "EWOULDBLOCK",
    "WSAEWOULDBLOCK",
    "EINVAL",
    "WSAEINVAL",
]
yerrors = {getattr(errno, name) for name in yerrlist if hasattr(errno, name)}

@coroutine
@wraps(socket.socket.connect)
def async_connect(sock, host):
    sock.setblocking(False)
    while True:
        err = sock.connect_ex(host)
        if err in yerrors:
            yield
        elif err in (getattr(errno, "EISCONN"), getattr(errno, "WSAEISCONN")):
            break
        else:
            raise OSError(err, os.strerror(err))


@coroutine
@wraps(_ssl.SSLSocket.do_handshake)
def ssl_do_handshake(socket, *args, **kwargs):
    while True:
        try:
            return socket.do_handshake()
        except (_ssl.SSLWantReadError, _ssl.SSLWantWriteError):
            yield
