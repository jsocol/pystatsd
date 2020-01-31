from __future__ import absolute_import, division, unicode_literals

import socket
import random

from .base import StatsClientBase


class Pipeline(PipelineBase):

    def __init__(self, client):
        super(Pipeline, self).__init__(client)
        self._maxudpsize = client._maxudpsize

    def _send(self):
        data = self._stats.popleft()
        stat = None
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


class ConsistentHashingStatsClient(StatsClientBase):
    """A client for statsd."""

    # we have to update the kwarg to be host since the newer versions require it to be `host` instead of `hosts`
    def __init__(self, host=('localhost'), port=8125, prefix=None,
                 maxudpsize=512, ipv6=False):
        self._addrs = []
        self._sock = None
        # host is actually hosts
        hosts = host
        for host in hosts:
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

    def _send_stat(self, stat, value, rate):
        values = self._prepare(stat, value, rate)
        if values:
            self._after(values[0], values[1])

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

    def _after(self, stat, data):
        if data:
            self._send(stat, data)

    def _prepare(self, stat, value, rate=1):
        if rate < 1:
            if random.random() > rate:
                return

        return stat, value
