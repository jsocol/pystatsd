from __future__ import absolute_import, division, unicode_literals


import socket

from .udp import PipelineBase, StatsClient
from .timer import Timer


class ScaleTimer(Timer):
    """A context manager/decorator for statsd.timing()."""

    def __init__(self, client, stat, rate=1, scale=1):
        super(ScaleTimer, self).__init__(client, stat, rate=rate)
        self.scale = scale

    def send(self):
        if self.ms is None:
            raise RuntimeError('No data recorded.')
        if self._sent:
            raise RuntimeError('Already sent data.')
        self._sent = True
        scaled_timer = self.ms * self.scale
        self.client.timing(self.stat, scaled_timer, self.rate)


class Pipeline(PipelineBase):

    def __init__(self, client):
        super(Pipeline, self).__init__(client)
        self._maxudpsize = client._maxudpsize

    def _send(self):
        stat = data = self._stats.popleft()
        while self._stats:
            # Use popleft to preserve the order of the stats.
            stat = self._stats.popleft()
            if len(stat) + len(data) + 1 >= self._maxudpsize:
                self._client._after(stat, data)
                data = stat
            else:
                data += '\n' + stat
        if stat is not None:
            self._client._after(stat, data)


class ConsistentHashingStatsClient(StatsClient):
    """A client for statsd."""

    # we have to update the kwarg to be host since the newer versions require it to be `host` instead of `hosts`
    def __init__(self, host=('localhost',), port=8125, prefix=None,
                 maxudpsize=512, ipv6=False):
        # host is actually hosts
        self.hosts = host
        # we should convert a single host to hosts if called with a string
        if isinstance(self.hosts, basestring):
            self.hosts = (self.hosts,)
        self._addrs = []
        self._sock = None
        for host in self.hosts:
            self._addrs.append(self._get_addr(ipv6, host, port))
        self._prefix = prefix
        self._maxudpsize = maxudpsize

    def _get_addr(self, ipv6, host, port):
        fam = socket.AF_INET6 if ipv6 else socket.AF_INET
        family, _, _, _, addr = socket.getaddrinfo(
            host, port, fam, socket.SOCK_DGRAM)[0]
        if not self._sock:
            self._sock = socket.socket(family, socket.SOCK_DGRAM)
        return addr

    def _send_stat(self, stat, data, rate):
        value = self._prepare(stat, data, rate)
        if value:
            self._after(stat, value)

    def _send(self, stat, data):
        """Send data to statsd."""
        try:
            address_index = hash(stat) % len(self._addrs)
            addr = self._addrs[address_index]
            self._sock.sendto(data.encode('ascii'), addr)
        except (socket.error, RuntimeError):
            # Whimmy wham wham wozzle
            pass

    def pipeline(self):
        return Pipeline(self)

    def timer(self, stat, rate=1, scale=1):
        return ScaleTimer(self, stat, rate, scale)

    def _after(self, stat, data):
        if data:
            self._send(stat, data)
