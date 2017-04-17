import os

from statsd.client import StatsClient

HOST = 'localhost'
PORT = 8125
IPV6 = False
PREFIX = None
MAXUDPSIZE = 512


def from_env():
    """Return a StatsClient populated from environment variables"""

    host = os.getenv('STATSD_HOST', HOST)
    port = int(os.getenv('STATSD_PORT', PORT))
    prefix = os.getenv('STATSD_PREFIX', PREFIX)
    maxudpsize = int(os.getenv('STATSD_MAXUDPSIZE', MAXUDPSIZE))
    ipv6 = bool(int(os.getenv('STATSD_IPV6', IPV6)))
    return StatsClient(host=host, port=port, prefix=prefix,
                       maxudpsize=maxudpsize, ipv6=ipv6)
