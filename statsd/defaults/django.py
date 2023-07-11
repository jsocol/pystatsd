from typing import Optional
from django.conf import settings

from statsd import defaults
from statsd.client import StatsClient


host: str = getattr(settings, 'STATSD_HOST', defaults.HOST)
port: int = getattr(settings, 'STATSD_PORT', defaults.PORT)
prefix: Optional[str] = getattr(settings, 'STATSD_PREFIX', defaults.PREFIX)
maxudpsize: int = getattr(settings, 'STATSD_MAXUDPSIZE', defaults.MAXUDPSIZE)
ipv6: bool = getattr(settings, 'STATSD_IPV6', defaults.IPV6)
statsd: StatsClient = StatsClient(host=host, port=port, prefix=prefix,
                                  maxudpsize=maxudpsize, ipv6=ipv6)
