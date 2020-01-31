from __future__ import absolute_import

from .client import StatsClient as UDPStatsClient
from .client import TCPStatsClient
from .client import UnixSocketStatsClient
from .client import ConsistentHashingStatsClient as StatsClient

VERSION = (3, 2, 1)
__version__ = '.'.join(map(str, VERSION))
__all__ = ['UDPStatsClient', 'TCPStatsClient', 'UnixSocketStatsClient', 'StatsClient']
