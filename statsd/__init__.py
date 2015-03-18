from __future__ import absolute_import

from .client import StatsClient
from .client import TCPStatsClient


VERSION = (3, 1, 0)
__version__ = '.'.join(map(str, VERSION))
__all__ = ['StatsClient', 'TCPStatsClient']
