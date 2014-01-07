from __future__ import absolute_import
import os
import socket

try:
    from django.conf import settings
    from django.core.exceptions import ImproperlyConfigured
    try:
        # This handles the case where Django >=1.5 is in the python path
        # but this particular project is not a django project. In
        # that case, settings aren't configured.
        getattr(settings, 'STATSD_HOST', 'localhost')
    except ImproperlyConfigured:
        settings = None
except ImportError:
    settings = None

from .client import StatsClient


VERSION = (2, 1, 2)
__version__ = '.'.join(map(str, VERSION))
__all__ = ['StatsClient', 'statsd']

statsd = None

if settings:
    try:
        host = getattr(settings, 'STATSD_HOST', 'localhost')
        port = getattr(settings, 'STATSD_PORT', 8125)
        prefix = getattr(settings, 'STATSD_PREFIX', None)
        maxudpsize = getattr(settings, 'STATSD_MAXUDPSIZE', 512)
        statsd = StatsClient(host, port, prefix, maxudpsize)
    except (socket.error, socket.gaierror, ImportError):
        pass
elif 'STATSD_HOST' in os.environ:
    try:
        host = os.environ['STATSD_HOST']
        port = int(os.environ['STATSD_PORT'])
        prefix = os.environ.get('STATSD_PREFIX')
        maxudpsize = int(os.environ.get('STATSD_MAXUDPSIZE', 512))
        statsd = StatsClient(host, port, prefix, maxudpsize)
    except (socket.error, socket.gaierror, KeyError):
        pass
