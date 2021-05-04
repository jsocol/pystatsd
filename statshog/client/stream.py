from __future__ import absolute_import, division, unicode_literals

import socket
from typing import Tuple, Union

from .base import StatsClientBase, PipelineBase


class StreamPipeline(PipelineBase):
    def _send(self):
        self._client._after("\n".join(self._stats))
        self._stats.clear()


class StreamClientBase(StatsClientBase):
    def connect(self):
        raise NotImplementedError()

    def close(self):
        if self._sock and hasattr(self._sock, "close"):
            self._sock.close()
        self._sock = None

    def reconnect(self):
        self.close()
        self.connect()

    def pipeline(self):
        return StreamPipeline(self)

    def _send(self, data: str):
        """Send data to statsd."""
        if not self._sock:
            self.connect()
        self._do_send(data)

    def _do_send(self, data: str):
        self._sock.sendall(data.encode("ascii") + b"\n")


class TCPStatsClient(StreamClientBase):
    """TCP version of StatsClient."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8125,
        prefix: Union[str, None] = None,
        timeout: Union[float, None] = None,
        ipv6: bool = False,
        telegraf: bool = False,
    ):
        """Create a new client."""
        self._host = host
        self._port = port
        self._ipv6 = ipv6
        self._timeout = timeout
        self._prefix = prefix
        self._sock = None
        self._telegraf = telegraf

    def connect(self):
        fam = socket.AF_INET6 if self._ipv6 else socket.AF_INET
        family, _, _, _, addr = socket.getaddrinfo(
            self._host, self._port, fam, socket.SOCK_STREAM
        )[0]
        self._sock = socket.socket(family, socket.SOCK_STREAM)
        self._sock.settimeout(self._timeout)
        self._sock.connect(addr)


class UnixSocketStatsClient(StreamClientBase):
    """Unix domain socket version of StatsClient."""

    def __init__(
        self,
        socket_path: Union[Tuple, str, bytes],
        prefix: Union[str, None] = None,
        timeout: Union[float, None] = None,
        telegraf: bool = False,
    ):
        """Create a new client."""
        self._socket_path = socket_path
        self._timeout = timeout
        self._prefix = prefix
        self._sock = None
        self._telegraf = telegraf

    def connect(self):
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._sock.settimeout(self._timeout)
        self._sock.connect(self._socket_path)
