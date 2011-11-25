try:
    from django.conf import settings
    from django.utils.importlib import import_module
except ImportError:
    settings = None


__all__ = ['StatsClient', 'statsd']

VERSION = (0, 3, 0)
__version__ = '.'.join(map(str, VERSION))


if settings:
    try:
        client = getattr(settings, 'STATSD_CLIENT', 'statsd.client')
        host = getattr(settings, 'STATSD_HOST', 'localhost')
        port = getattr(settings, 'STATSD_PORT', 8125)
        prefix = getattr(settings, 'STATSD_PREFIX', None)
        statsd = import_module(client).StatsClient(host, port, prefix)
    except ImportError:
        statsd = None
