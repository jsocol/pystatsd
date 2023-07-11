import os
from typing import Optional

from statsd import defaults
from statsd.client import StatsClient


host: str = os.getenv('STATSD_HOST', defaults.HOST)
port: int = int(os.getenv('STATSD_PORT', defaults.PORT))
prefix: Optional[str] = os.getenv('STATSD_PREFIX', defaults.PREFIX)
maxudpsize: int = int(os.getenv('STATSD_MAXUDPSIZE', defaults.MAXUDPSIZE))
ipv6: bool = bool(int(os.getenv('STATSD_IPV6', defaults.IPV6)))
statsd: StatsClient = StatsClient(host=host, port=port, prefix=prefix,
                                  maxudpsize=maxudpsize, ipv6=ipv6)
