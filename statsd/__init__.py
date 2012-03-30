import socket

try:
    from django.conf import settings
except ImportError:
    settings = None

from client import StatsClient


__all__ = ['StatsClient', 'statsd']

VERSION = (0, 4, 0)
__version__ = '.'.join(map(str, VERSION))


if settings:
    try:
        host = getattr(settings, 'STATSD_HOST', 'localhost')
        port = getattr(settings, 'STATSD_PORT', 8125)
        prefix = getattr(settings, 'STATSD_PREFIX', None)
        statsd = StatsClient(host, port, prefix)
    except (socket.error, socket.gaierror, ImportError):
        statsd = None
