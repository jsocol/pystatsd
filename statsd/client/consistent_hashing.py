from __future__ import absolute_import, division, unicode_literals

import socket

from .base import StatsClientBase, PipelineBase


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
        return PipelineBase(self)