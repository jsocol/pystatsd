from __future__ import absolute_import
import os
import socket

try:
    from django.conf import settings
except ImportError:
    settings = None

from .client import StatsClient


__all__ = ['StatsClient', 'statsd']

VERSION = (1, 0, 0)
__version__ = '.'.join(map(str, VERSION))


statsd = None

if settings:
    try:
        host = getattr(settings, 'STATSD_HOST', 'localhost')
        port = getattr(settings, 'STATSD_PORT', 8125)
        prefix = getattr(settings, 'STATSD_PREFIX', None)
        batch_len = getattr(settings, 'STATSD_BATCH_LEN', 1)
        thread_safe = getattr(settings, 'STATSD_THREAD_SAFE', False)
        debug = getattr(settings, 'STATSD_DEBUG', False)
        statsd = StatsClient(host, port, prefix, batch_len, thread_safe, debug)
    except (socket.error, socket.gaierror, ImportError):
        pass
elif 'STATSD_HOST' in os.environ:
    try:
        host = os.environ['STATSD_HOST']
        port = int(os.environ['STATSD_PORT'])
        prefix = os.environ.get('STATSD_PREFIX')
        batch_len = int(os.environ.get('STATSD_BATCH_LEN', 1))
        thread_safe = os.environ.get('STATSD_THREAD_SAFE') == 'True'
        debug = os.environ.get('STATSD_DEBUG') == 'True'
        statsd = StatsClient(host, port, prefix, batch_len, thread_safe, debug)
    except (socket.error, socket.gaierror, KeyError):
        pass
