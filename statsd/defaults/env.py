from __future__ import absolute_import
import os

from statsd import defaults
from statsd.client import StatsClient


statsd = None

if statsd is None:
    host = os.getenv('STATSD_HOST', defaults.HOST)
    port = int(os.getenv('STATSD_PORT', defaults.PORT))
    prefix = os.getenv('STATSD_PREFIX', defaults.PREFIX)
    maxudpsize = int(os.getenv('STATSD_MAXUDPSIZE', defaults.MAXUDPSIZE))
    statsd = StatsClient(host, port, prefix, maxudpsize)
