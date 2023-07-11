import socket
from typing import Optional

from .base import StatsClientBase, PipelineBase


class Pipeline(PipelineBase):

    def __init__(self, client: StatsClientBase) -> None:
        super().__init__(client)
        self._maxudpsize = client._maxudpsize

    def _send(self):
        data = self._stats.popleft()
        while self._stats:
            # Use popleft to preserve the order of the stats.
            stat = self._stats.popleft()
            if len(stat) + len(data) + 1 >= self._maxudpsize:
                self._client._after(data)
                data = stat
            else:
                data += '\n' + stat
        self._client._after(data)


class StatsClient(StatsClientBase):
    """A client for statsd."""

    def __init__(self, host: str = 'localhost', port: int = 8125,
                 prefix: Optional[str] = None,
                 maxudpsize: int = 512, ipv6: bool = False) -> None:
        """Create a new client."""
        fam = socket.AF_INET6 if ipv6 else socket.AF_INET
        family, _, _, _, addr = socket.getaddrinfo(
            host, port, fam, socket.SOCK_DGRAM)[0]
        self._addr = addr
        self._sock = socket.socket(family, socket.SOCK_DGRAM)
        self._prefix = prefix
        self._maxudpsize = maxudpsize

    def _send(self, data):
        """Send data to statsd."""
        try:
            self._sock.sendto(data.encode('ascii'), self._addr)
        except (OSError, RuntimeError):
            # No time for love, Dr. Jones!
            pass

    def close(self) -> None:
        if self._sock and hasattr(self._sock, 'close'):
            self._sock.close()
        self._sock = None

    def pipeline(self) -> Pipeline:
        return Pipeline(self)
